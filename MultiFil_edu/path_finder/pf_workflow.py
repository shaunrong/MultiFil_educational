#!/usr/bin/env python
from fireworks import Workflow, Firework

from pf_task import WriteGammaInputTask, VaspCustodianTask, PathFinderAnalyze
from pymatgen import MPRester
from end_point_finder import EndPointFinder
from MultiFil_edu.settings.db_singleton import MyDB

__author__ = 'Shaun Rong'
__version__ = '0.1'
__maintainer__ = 'Shaun Rong'
__email__ = 'rongzq08@gmail.com'


def multifil_wf(mp_id, specie, col):
    """
    :param mp_id: mp_id for fully discharged Li cathode structures
    :param specie: Moving cation.
    :param db_scripts: default value to rongzq_fw on matgen.mit.edu
    :return: a firework workflow to work on Hopper
    """
    MyDB.db_access().connect()
    collection = MyDB.db_access().collection(col)

    with MPRester('DbftwqIehya780rm') as m:
        response = m.get_data(mp_id, prop='structure')
        formula = m.get_data(mp_id, prop='pretty_formula')
    struct = response[0]['structure']
    struct_copy = struct.copy()
    end_point_finder = EndPointFinder(struct, specie)
    end_point_pairs = end_point_finder.get_end_point_pairs()

    if not end_point_pairs:
        print("No end point pairs found")
        return None
    else:
        struct_orig = []
        for i in range(len(end_point_pairs)):
            struct_orig.append(struct_copy.copy())

        fw_list = []
        fw_depend = {}
        last_fw = None
        for pair in range(len(end_point_pairs)):
            (struct_s1, struct_s2, gamma_struct) = end_point_finder.get_gamma_struct(struct_orig[pair],
                                                                                     end_point_pairs[pair])
            # Insert into the database
            s1_index = struct_s1.species.index(specie)
            s2_index = struct_s2.species.index(specie)
            collection.insert_one({'mp-id': mp_id, 'pretty_formula': formula[0]['pretty_formula'],
                                    'gamma_structure': gamma_struct.as_dict(),
                                    'pair_index': pair,
                                    'cation_diffusion_start': struct_s1[s1_index].as_dict(),
                                    'cation_diffusion_end': struct_s2[s2_index].as_dict()})
            task1 = WriteGammaInputTask(structure=gamma_struct.as_dict())
            task2 = VaspCustodianTask(handlers='all')
            task3 = PathFinderAnalyze(struct_s1=struct_s1.as_dict(), struct_s2=struct_s2.as_dict())
            fw = Firework([task1, task2, task3], spec={"mp-id": mp_id,
                                                       'cation_diffusion_start': struct_s1[s1_index].as_dict(),
                                                       'cation_diffusion_end': struct_s2[s2_index].as_dict(),
                                                       'moving_cation': specie.as_dict(),
                                                       'pair_index': pair,
                                                       "collection": col,
                                                       "_queueadapter": {'nnodes': 128, 'walltime': '12:00:00',
                                                                         'queue': 'Q.JCESR',
                                                                         'job_name': "{}".format(
                                                                             formula[0]['pretty_formula'])}})
            fw_list.append(fw)
            if last_fw is not None:
                fw_depend[last_fw] = [fw]
            last_fw = fw
        wf = Workflow(fw_list, fw_depend)
        MyDB.db_access().close()
        return wf
