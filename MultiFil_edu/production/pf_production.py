#!/usr/bin/env python

from fireworks import LaunchPad
from MultiFil_edu.path_finder.pf_workflow import multifil_wf
from pymatgen import Element
from MultiFil_edu.settings.environ import FIREWORKS_LAUNCHPAD_FILE

__author__ = 'Shaun Rong'
__version__ = '0.1'
__maintainer__ = 'Shaun Rong'
__email__ = 'rongzq08@gmail.com'

if __name__ == '__main__':
    # input params, input file, moving cation and the database collection for inserting calculation results
    input_file = 'Mg_PF_example.txt'
    moving_cation = 'Mg'
    col = 'Mg_MV'

    lp = LaunchPad.from_file(FIREWORKS_LAUNCHPAD_FILE)
    with open(input_file, 'r') as f:
        cathode_list = f.readlines()
    entry_number = 0
    for battery in cathode_list:
        mp_id = battery.split()[0]
        try:
            wf = multifil_wf(mp_id, Element(input_file), col)
            if wf:
                entry_number += 1
                print(entry_number, mp_id)
                lp.add_wf(wf)
        except:
            pass