#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from MultiFil_edu.settings.db_singleton import MyDB

__author__ = 'Ziqin (Shaun) Rong'
__maintainer__ = 'Ziqin (Shaun) Rong'
__email__ = 'rongzq08@gmail.com'

"""
This is a demo script that mupdates the file path of ApproxNEB calculation after migrating the calculation 
files to vega.
"""


if __name__ == '__main__':
    # The collection you want to run this script over
    col = 'Mg_MV'

    db = MyDB.db_access()
    db.connect()
    col = db.collection(col)

    vega_dir = 'vega:/userhome/rongzq/Vesta_backup/Mg_HTApproxNEB'
    for doc in col.find({'status': 'success'}):
        if 'MEP_energy' in doc.keys():
            MEP_energy = doc['MEP_energy']
            for i in range(0, 9):
                if "image_{}".format(i) in MEP_energy.keys():
                    file_path_l = MEP_energy['image_{}'.format(i)]['file_path'].split('/')
                    new_file_path_l = [vega_dir, file_path_l[-2], file_path_l[-1]]
                    new_file_path = '/'.join(new_file_path_l)
                    MEP_energy['image_{}'.format(i)]['file_path'] = new_file_path
            col.update({"mp-id": doc["mp-id"], "pair_index": doc["pair_index"]},
                       {"$set": {"MEP_energy": MEP_energy}})

    db.close()
