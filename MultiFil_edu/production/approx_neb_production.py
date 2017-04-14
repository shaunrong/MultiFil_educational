#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fireworks import LaunchPad

from MultiFil_edu.approx_neb.point_energy_wf import end_point_wf
from pymatgen import Element
from MultiFil_edu.settings.environ import FIREWORKS_LAUNCHPAD_FILE

__author__ = 'Ziqin (Shaun) Rong'
__version__ = '0.1'
__maintainer__ = 'Ziqin (Shaun) Rong'
__email__ = 'rongzq08@gmail.com'


if __name__ == '__main__':
    # Parameters
    moving_cation = Element('Mg')
    calculated_images = [0, 4]  # This is 1st phase screening
    # calculated_images = range(0, 9) # This is 2nd phase MEP calculation
    input_file = 'Mg_approx_neb_example.txt'
    collection_name = 'Mg_MV'

    lp = LaunchPad.from_file(FIREWORKS_LAUNCHPAD_FILE)

    wf_idx = []

    with open(input_file, 'r') as f:
        data = f.readlines()

    for i, content in enumerate(data):
        data[i] = content.split()

    for doc in data:
        wf_idx.append((doc[0], int(doc[1]),))

    for idx in wf_idx:
        for i in calculated_images:
            try:
                wf = end_point_wf(idx[0], idx[1], i, moving_cation, collection_name)
                if wf:
                    lp.add_wf(wf)
                else:
                    print("The calculation has already been done")
            except KeyError as e:
                print(idx)
                print(e)
