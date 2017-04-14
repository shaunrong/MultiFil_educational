#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pymongo
import yaml

from custodian import Custodian
from fireworks import explicit_serialize, FireTaskBase, FWAction

from point_run_input import PointRunInput
from MultiFil_edu.settings.db_singleton import MyDB

from custodian.vasp.jobs import VaspJob
from pymatgen.io.vasp import Oszicar

__author__ = 'Ziqin (Shaun) Rong'
__version__ = '0.1'
__maintainer__ = 'Ziqin (Shaun) Rong'
__email__ = 'rongzq08@gmail.com'


def load_class(mod, name):
    mod = __import__(mod, globals(), locals(), [name], 0)
    return getattr(mod, name)


@explicit_serialize
class WritePointRunInput(FireTaskBase):
    """
    Write Vasp Gamma input set, using parameters settings in generateGammaRun.py
    """
    required_params = ['structure', "moving_cation"]

    def run_task(self, fw_spec):
        struct = self["structure"]
        params = PointRunInput(struct, ggaU=False)
        incar = params.get_incar(relax=True)
        moving_cation = self["moving_cation"]
        poscar = params.get_poscar(moving_cation)
        potcar = params.get_potcar()
        kpoints = params.get_kpoints()

        # WRite out VASP input files
        incar.write_file("INCAR")
        poscar.write_file("POSCAR")
        potcar.write_file("POTCAR")
        kpoints.write_file("KPOINTS")

        return FWAction()


@explicit_serialize
class PointCustodianRun(FireTaskBase):
    required_params = ['handlers']

    def run_task(self, fw_spec):
        # Vesta VASP run job command below
        print(os.environ['COBALT_PARTNAME'])
        cobalt_partname = os.environ['COBALT_PARTNAME']
        vasp_cmd = ['runjob', '-n', str(fw_spec["_queueadapter"]["nnodes"]), '--block', cobalt_partname,
                    '-p', '1', ":", fw_spec["_fw_env"]['vasp_cmd']]
        # Vesta End
        job = VaspJob(vasp_cmd=vasp_cmd, auto_gamma=False, auto_npar=False)
        if self["handlers"] == "all":
            hnames = ["VaspErrorHandler", "MeshSymmetryErrorHandler",
                      "UnconvergedErrorHandler", "NonConvergingErrorHandler",
                      "PotimErrorHandler", "WalltimeHandler"]
        else:
            hnames = self["handlers"]
        handlers = [load_class("custodian.vasp.handlers", n)() for n in hnames]
        c = Custodian(handlers, [job], **self.get("custodian_params", {}))

        MyDB.db_access().connect()
        collection = MyDB.db_access().collection(fw_spec['collection'])

        doc = collection.find_one({'mp-id': fw_spec["mp_id"], 'pair_index': fw_spec["pair_index"]})
        if "MEP_energy" in doc.keys():
            MEP_energy = doc["MEP_energy"]
        else:
            MEP_energy = {}

        MEP_energy["image_{}".format(fw_spec["image_num"])] = {}
        MEP_energy["image_{}".format(fw_spec["image_num"])]["file_path"] = os.getcwd()
        MEP_energy["image_{}".format(fw_spec["image_num"])]["status"] = "started"

        collection.update({"mp-id": fw_spec["mp_id"], "pair_index": fw_spec["pair_index"]},
                          {"$set": {"MEP_energy": MEP_energy}})

        output = c.run()

        MyDB.db_access().close()

        return FWAction()


@explicit_serialize
class PointRunAnalyze(FireTaskBase):

    def run_task(self, fw_spec):

        MyDB.db_access().connect()
        collection = MyDB.db_access().collection(fw_spec['collection'])

        doc = collection.find_one({'mp-id': fw_spec["mp_id"], 'pair_index': fw_spec["pair_index"]})
        MEP_energy = doc["MEP_energy"]

        with open('vasp.out', 'r') as output:
            content = output.readlines()

        examine_1 = content[-2].strip()
        examine_2 = content[-3].strip()
        if examine_1[0:25] == 'reached required accuracy' or examine_2[0:25] == 'reached required accuracy':
            oszicar = Oszicar('OSZICAR')
            energy = oszicar.final_energy
            MEP_energy["image_{}".format(fw_spec["image_num"])]["status"] = "success"
            MEP_energy["image_{}".format(fw_spec["image_num"])]["energy"] = energy
            collection.update({"mp-id": fw_spec["mp_id"], "pair_index": fw_spec["pair_index"]},
                              {"$set": {"MEP_energy": MEP_energy}})

            MyDB.db_access().close()
            return FWAction()
        else:
            MEP_energy[fw_spec["image_num"]]["status"] = "failed"
            collection.update({"mp-id": fw_spec["mp_id"], "pair_index": fw_spec["pair_index"]},
                              {"$set": {"MEP_energy": MEP_energy}})
            MyDB.db_access().close()
            return FWAction()
