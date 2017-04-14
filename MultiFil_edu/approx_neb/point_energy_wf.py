#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pymongo
import yaml
from fireworks import Firework, Workflow

from MultiFil_edu.settings.db_singleton import MyDB
from point_energy_task import WritePointRunInput, PointCustodianRun, PointRunAnalyze
from pymatgen import Structure, PeriodicSite

__author__ = 'Ziqin (Shaun) Rong'
__version__ = '0.1'
__maintainer__ = 'Ziqin (Shaun) Rong'
__email__ = 'rongzq08@gmail.com'


def end_point_wf(mp_id, pair_index, image_num, moving_cation, col):
    """

    :param col: collection name
    :param mp_id: mp_id in the db_scripts
    :param pair_index: pair_index in the db_scripts
    :param image_num: index number of the image on the path from the db_scripts
    :param moving_cation: pymatgen.Element object, represeting the moving cation, e.g. Element('Mg')
    :return:
    """
    MyDB.db_access().connect()
    collection = MyDB.db_access().collection(col)

    doc = collection.find_one({'mp-id': mp_id, 'pair_index': pair_index})

    # Calculation that is already successful
    if 'MEP_energy' in doc.keys() and ("image_{}".format(image_num) in doc['MEP_energy']):
        if doc['MEP_energy']['image_{}'.format(image_num)]['status'] == 'success':
            return
        else:
            # Calculation that has halted halfway due to errors
            if 'CONTCAR_struct' in doc['MEP_energy']['image_{}'.format(image_num)].keys():
                struct = Structure.from_dict(doc["MEP_energy"]["image_{}".format(image_num)]["CONTCAR_struct"])
            # Calculation that has not been run before
            else:
                struct = Structure.from_dict(doc['gamma_structure'])
                cation_site = PeriodicSite.from_dict(doc['path'][image_num])
                struct.insert(0, cation_site.specie, cation_site.frac_coords,
                              properties=doc['path'][image_num]['properties'])
    else:
        struct = Structure.from_dict(doc['gamma_structure'])
        cation_site = PeriodicSite.from_dict(doc['path'][image_num])
        struct.insert(0, cation_site.specie, cation_site.frac_coords, properties=doc['path'][image_num]['properties'])

    task1 = WritePointRunInput(structure=struct.as_dict(), moving_cation=moving_cation.as_dict())
    task2 = PointCustodianRun(handlers='all')
    task3 = PointRunAnalyze()

    fw = Firework([task1, task2, task3], spec={"mp_id": mp_id,
                                               "pair_index": pair_index,
                                               "image_num": image_num,
                                               "collection": col,
                                               "_queueadapter": {'nnodes': 128, 'walltime': '10:00:00',
                                                                 'queue': 'Q.JCESR',
                                                                 'job_name': "{}_{}".format(doc["pretty_formula"],
                                                                                            image_num)}})

    wf_list = [fw]
    wf_depend = {}
    wf = Workflow(wf_list, wf_depend)

    MyDB.db_access().close()
    return wf


