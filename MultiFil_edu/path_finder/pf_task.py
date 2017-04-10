#!/usr/bin/env python
import os
from custodian import Custodian
from custodian.vasp.jobs import VaspJob
from fireworks import explicit_serialize, FireTaskBase, FWAction
from pymatgen.analysis.structure_analyzer import VoronoiCoordFinder
from pymatgen.io.vaspio import Chgcar
from pymatgen import Structure
from gamma_input_set import VaspBulk
from path_finder import NEBPathfinder, ChgcarPotential
from MultiFil_edu.settings.db_singleton import MyDB

__author__ = 'Shaun Rong'
__version__ = '0.1'
__maintainer__ = 'Shaun Rong'
__email__ = 'rongzq08@gmail.com'


def load_class(mod, name):
    mod = __import__(mod, globals(), locals(), [name], 0)
    return getattr(mod, name)


@explicit_serialize
class WriteGammaInputTask(FireTaskBase):
    """
    Write Vasp Gamma input set, using parameters settings in gamma_input_set.py
    """
    required_params = ["structure"]

    def run_task(self, fw_spec):
        gamma_struct = self["structure"]
        params = VaspBulk(gamma_struct, ggaU=False)
        # Get VASP input files from the parameter set
        incar = params.get_incar(relax=False)
        poscar = params.get_poscar()
        potcar = params.get_potcar()
        kpoints = params.get_kpoints()

        # WRite out VASP input files
        incar.write_file("INCAR")
        poscar.write_file("POSCAR")
        potcar.write_file("POTCAR")
        kpoints.write_file("KPOINTS")


@explicit_serialize
class VaspCustodianTask(FireTaskBase):
    """
    Run the Gamma Point Vasp Job
    """

    def run_task(self, fw_spec):
        # Edison setting
        # vasp_cmd = ['aprun', '-n', str(fw_spec["_queueadapter"]["mppwidth"]), fw_spec["_fw_env"]['vasp_cmd']]
        # Vesta setting
        cobalt_partname = os.environ['COBALT_PARTNAME']
        vasp_cmd = ['runjob', '-n', str(fw_spec["_queueadapter"]["nnodes"]), '--block', cobalt_partname,
                    '-p', '1', ":", fw_spec["_fw_env"]['vasp_cmd']]
        job = VaspJob(vasp_cmd=vasp_cmd, auto_gamma=False, auto_npar=False)
        if self["handlers"] == "all":
            hnames = ["VaspErrorHandler", "MeshSymmetryErrorHandler",
                      "UnconvergedErrorHandler", "NonConvergingErrorHandler",
                      "PotimErrorHandler", "WalltimeHandler"]
        else:
            hnames = self["handlers"]
        handlers = [load_class("custodian.vasp.handlers", n)() for n in hnames]
        c = Custodian(handlers, [job], **self.get("custodian_params", {}))
        output = c.run()

        chgcar_dir = os.getcwd()

        MyDB.db_access().connect()
        collection = MyDB.db_access().collection(fw_spec['collection'])
        collection.update({"mp-id": fw_spec["mp-id"], "pair_index": fw_spec["pair_index"]},
                          {"$set": {"chgcar_dir": chgcar_dir}})
        MyDB.db_access().close()
        return FWAction(stored_data=output)


@explicit_serialize
class PathFinderAnalyze(FireTaskBase):
    """
    Extract the CHGCAR, interpolate the path, analyze the effective coordination number change, insert things
    back to the database.
    """
    required_params = ['struct_s1', 'struct_s2']

    def run_task(self, fw_spec):

        MyDB.db_access().connect()
        collection = MyDB.db_access().collection(fw_spec['collection'])

        with open('vasp.out', 'r') as output:
            content = output.readlines()
        examine = content[-2].strip()
        if examine[0:3] == '1 F':
            chgcar = Chgcar.from_file('CHGCAR')
            s1 = self['struct_s1']
            s2 = self['struct_s2']
            relax_sites = []
            for site_i, site in enumerate(s1.sites):
                if site.specie == fw_spec['moving_cation']:
                    relax_sites.append(site_i)

            pf = NEBPathfinder(s1, s2, relax_sites=relax_sites, v=ChgcarPotential(chgcar).get_v(), n_images=8)
            images = pf.images

            doc = collection.find_one({'mp-id': fw_spec["mp-id"], 'pair_index': fw_spec["pair_index"]})
            path = []
            coordination_number = []
            for image in images:
                struct = Structure.from_dict(doc["gamma_structure"])
                site_index = image.species.index(fw_spec['moving_cation'])
                cation_site = image[site_index]
                struct.insert(0, cation_site.specie, cation_site.frac_coords,
                              properties=cation_site.properties)
                path.append(image[site_index].as_dict())
                voro_cn = VoronoiCoordFinder(struct)
                cn = voro_cn.get_coordination_number(0)
                coordination_number.append(cn)

            collection.update({"mp-id": fw_spec["mp-id"], "pair_index": fw_spec["pair_index"]},
                              {"$set": {"status": "success", "CN_path": coordination_number,
                                         "path": path}})
        else:
            collection.update({"mp-id": fw_spec["mp-id"], "pair_index": fw_spec["pair_index"]},
                              {"$set": {"status": "error"}})

        MyDB.db_access().close()

        return FWAction()
