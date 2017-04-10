#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from pymatgen.io.vasp import Poscar
from MultiFil_edu.settings.db_singleton import MyDB

__author__ = 'Ziqin (Shaun) Rong'
__version__ = '0.1'
__maintainer__ = 'Ziqin (Shaun) Rong'
__email__ = 'rongzq08@gmail.com'


# This script runs on Remote servers where we keep the backed-up calculated files

if __name__ == '__main__':
    # The collection you want to run this script over
    col = 'Mg_MV'

    db = MyDB.db_access()
    db.connect()
    collection = db.collection(col)

    for doc in collection.find({"status": "success"}):
        if "MEP_energy" in doc.keys():
            MEP_energy = doc["MEP_energy"]
            for i in range(0, 9):
                if "image_{}".format(i) in doc["MEP_energy"].keys():
                    try:
                        file_path = doc["MEP_energy"]["image_{}".format(i)]["file_path"].split(':')[1]
                        contcar_struct = Poscar.from_file(os.path.join(file_path, "CONTCAR")).structure
                        MEP_energy["image_{}".format(i)]["CONTCAR_struct"] = contcar_struct.as_dict()
                    except OSError:
                        print("mp-id {}, pair_index {}, image {} has no calculation file".format(doc['mp-id'],
                                                                                                 doc['pair_index'],
                                                                                                 i))
                    except ValueError:
                        print("mp-id {}, pair_index {}, image {} has no empty POSCAR file".format(doc['mp-id'],
                                                                                                  doc['pair_index'],
                                                                                                  i))
            collection.update({"mp-id": doc["mp-id"], "pair_index": doc["pair_index"]},
                              {"$set": {"MEP_energy": MEP_energy}})

    db.close()
