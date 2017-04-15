#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os

from pymatgen import Structure, MPRester
from MultiFil_edu.settings.db_singleton import MyDB
from MultiFil_edu.settings.environ import REPO_ROOT

__author__ = 'Ziqin (Shaun) Rong'
__version__ = '0.1'
__maintainer__ = 'Ziqin (Shaun) Rong'
__email__ = 'rongzq08@gmail.com'


if __name__ == '__main__':
    # Paramters
    col = 'Mg_MV'
    input_file = os.path.join(REPO_ROOT, 'production', 'Mg_approx_neb_example.txt')

    MyDB.db_access().connect()
    collection = MyDB.db_access().collection(col)
    summary = []

    for doc in collection.find({'status': 'success'}):
        if 'MEP_energy' in doc.keys():
            if 'image_0' in doc['MEP_energy'].keys() and 'image_1' in doc['MEP_energy'].keys() and \
                'image_2' in doc['MEP_energy'].keys() and 'image_3' in doc['MEP_energy'].keys() and \
                'image_4' in doc['MEP_energy'].keys() and 'image_5' in doc['MEP_energy'].keys() and \
                'image_6' in doc['MEP_energy'].keys() and 'image_7' in doc['MEP_energy'].keys() and \
                    'image_8' in doc['MEP_energy'].keys():
                if doc['MEP_energy']['image_0']['status'] == 'success' and \
                    doc['MEP_energy']['image_1']['status'] == 'success' and \
                    doc['MEP_energy']['image_2']['status'] == 'success' and \
                    doc['MEP_energy']['image_3']['status'] == 'success' and \
                    doc['MEP_energy']['image_4']['status'] == 'success' and \
                    doc['MEP_energy']['image_5']['status'] == 'success' and \
                    doc['MEP_energy']['image_6']['status'] == 'success' and \
                    doc['MEP_energy']['image_7']['status'] == 'success' and \
                                doc['MEP_energy']['image_8']['status'] == 'success':
                    gamma_struct = Structure.from_dict(doc['gamma_structure'])
                    start_end = []
                    intermediate = []
                    for i, cn in enumerate(doc['CN_path']):
                        if i == 0 or i == 8:
                            start_end.append(cn)
                        else:
                            intermediate.append(cn)
                    stable_site_cn = sum(start_end) / len(start_end)
                    max_cn = max(start_end + intermediate)
                    min_cn = min(start_end + intermediate)
                    energy = []
                    for i in range(0, 9):
                        energy.append(doc['MEP_energy']['image_{}'.format(i)]['energy'])
                    migration_energy = (max(energy) - min(energy)) * 1000
                    summary.append({'mp-id': str(doc['mp-id']),
                                    'pair_index': doc['pair_index'],
                                    'pretty_formula': doc['pretty_formula'],
                                    'stable_cn': stable_site_cn,
                                    'min_cn': min_cn,
                                    'max_cn': max_cn,
                                    'cn_range': (max_cn - min_cn),
                                    'migration_barrier': migration_energy})

    print("mp-id", "pretty_formula", "migration_barrier_lower_bound", "stable_cn", "cn_range", 'e_above_hull')

    for mat in summary:
        with MPRester('DbftwqIehya780rm') as m:
            response = m.get_data(mat['mp-id'], prop='e_above_hull')
        print(mat['mp-id'], mat['pretty_formula'], mat['migration_barrier'], mat["stable_cn"],
              mat["cn_range"], response[0]['e_above_hull'] * 1000)
