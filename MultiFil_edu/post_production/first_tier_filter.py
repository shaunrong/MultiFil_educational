#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os

import yaml

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

    with open(input_file, 'r') as f:
        content = f.readlines()

    summary = []

    for i, data in enumerate(content):
        content[i] = data.split()
        content[i][1] = int(content[i][1])

    for i, data in enumerate(content):
        print(data)
        for doc in collection.find({"mp-id": data[0], "pair_index": data[1]}):
            if "MEP_energy" in doc.keys():
                if "image_0" in doc["MEP_energy"].keys() and doc['MEP_energy']['image_0']['status'] == 'success' and \
                   "image_4" in doc["MEP_energy"].keys() and doc['MEP_energy']['image_4']['status'] == 'success':
                    start_end = []
                    intermediate = []
                    for image_num, cn in enumerate(doc['CN_path']):
                        if image_num == 0 or image_num == 8:
                            start_end.append(cn)
                        else:
                            intermediate.append(cn)
                    stable_site_cn = sum(start_end) / len(start_end)
                    max_cn = max(start_end + intermediate)
                    min_cn = min(start_end + intermediate)
                    migration_energy_lower_bound = abs((doc['MEP_energy']['image_4']["energy"] -
                                                        doc['MEP_energy']['image_0']["energy"])) * 1000
                    if 'e_above_hull' in doc.keys():
                        e_above_hull = doc['e_above_hull']
                    else:
                        e_above_hull = 'missing'
                    summary.append({'mp-id': unicode(doc['mp-id']),
                                    'pair_index': doc['pair_index'],
                                    'pretty_formula': doc['pretty_formula'],
                                    'stable_cn': stable_site_cn,
                                    'min_cn': min_cn,
                                    'max_cn': max_cn,
                                    'cn_range': (max_cn - min_cn),
                                    'migration_barrier_lower_bound': migration_energy_lower_bound,
                                    'e_above_hull': e_above_hull})

    with open('Mg_HTApproxNEB_results.yaml', 'w') as f:
        f.write(yaml.dump(summary, default_flow_style=False))

    print("mp-id", "pair_index", "pretty_formula", "migration_barrier_lower_bound", "stable_cn", "cn_range", "e_above_hull")

    for mat in summary:
        print(mat['mp-id'], mat["pair_index"], mat['pretty_formula'], mat['migration_barrier_lower_bound'],
              mat["stable_cn"], mat["cn_range"], mat['e_above_hull'])
