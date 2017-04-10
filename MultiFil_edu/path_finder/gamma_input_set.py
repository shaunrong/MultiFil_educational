#!/usr/bin/env python

"""
This module contains a set of input parameters for generating a Gamma point run for NEB preconditioning.
Includes a short example usage script.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import


import sys
from pymatgen.io.vasp.inputs import *
from pymatgen.io.vasp.sets import MITGGAVaspInputSet

__author__ = "Daniil Kitchaev, Ziqin Rong"
__version__ = "1.0"
__maintainer__ = "Daniil Kitchaev, Ziqin Rong"
__email__ = "dkitch@mit.edu, rongzq08@mit.edu"
__date__ = "March 6, 2015"


class VaspBulk(object):

    def __init__(self, struct, struct_type='insulator', ggaU=False, base_param_set=None):
        self.struct = Structure.from_sites(struct.get_sorted_structure().sites,
                                           to_unit_cell=False, validate_proximity=True)
        if base_param_set:
            self.base_params = base_param_set
        else:
            self.base_params = MITGGAVaspInputSet(hubbard_off=(not ggaU))
        self.ggaU = ggaU
        self.struct_type = struct_type

    def get_incar(self, cg_algo=False, relax=False):
        incar = self.base_params.get_incar(self.struct)
        #---------------------------------------------------------------------------------------------------------------
        # Basic setup
        #---------------------------------------------------------------------------------------------------------------
        incar['ISYM'] = 0 # Symmetry bad, symmetry go away
        incar["SYMPREC"] = 1e-8
        incar['ISIF'] = 3
        incar['ISMEAR'] = 0
        if self.struct_type == 'insulator':
            incar['SIGMA'] = 0.05
        elif self.struct_type == 'metal':
            incar['SIGMA'] = 0.2
        incar['LREAL'] = 'Auto'
        incar['LVTOT'] = False
        incar['LVHAR'] = False
        incar['LWAVE'] = False
        incar['LCHARG'] = True
        #incar['GGA'] = 'PS' # For turning on PBEsol - here just use normal PBE
        incar['ICHARG'] = 2
        incar['ISTART'] = 0
        incar['LVTOT'] = True
        incar['LVHAR'] = True

        #---------------------------------------------------------------------------------------------------------------
        # Convergence changes
        #---------------------------------------------------------------------------------------------------------------
        if not cg_algo:
            incar['ALGO'] = 'Fast'
        else:
            incar['ALGO'] = 'A'
            incar['LSUBROT'] = False
            incar['TIME'] = 0.2
        incar['AMIX'] = 0.2
        incar['AMIN'] = 0.01
        incar['BMIX'] = 0.0001
        incar['AMIX_MAG'] = 0.8
        incar['BMIX_MAG'] = 0.0001
        incar['LMAXMIX'] = 4
        #incar['LASPH'] = True # Generally should be set as it fixes lots of problems but its inconsistent with the
                               # runs in MP and Matgen so keep it off
        incar['EDIFF'] = 1e-6 * len(self.struct.sites)
        incar['NELMDL'] = -6
        incar['NELMIN'] = 8
        incar['ISIF'] = 2
        # For Vesta
        incar['NPAR'] = 8
        # For Vesta end

        #---------------------------------------------------------------------------------------------------------------
        # Relaxation
        #---------------------------------------------------------------------------------------------------------------
        if relax:
            incar['IBRION'] = 2
            incar['NSW'] = 100
            incar['POTIM'] = 0.25
        else:
            incar["IBRION"] = -1
            incar["NSW"] = 0

        #---------------------------------------------------------------------------------------------------------------
        # Make sure +U is turned off if necessary
        #---------------------------------------------------------------------------------------------------------------
        if not self.ggaU:
            delete_keys = ["LDAU", "LDAUJ", "LDAUL", "LDAUTYPE", "LDAUU"]
            for key in delete_keys:
                if key in incar.keys():
                    del incar[key]

        return incar

    def get_potcar(self):
        potcar = self.base_params.get_potcar(self.struct)
        return potcar

    def get_kpoints(self):
        kpoints = Kpoints.gamma_automatic((1,1,1),shift=(0,0,0))
        return kpoints

    def get_poscar(self):
        structure = self.struct.get_sorted_structure()
        selective_dynamics = np.zeros((structure.num_sites, 3), dtype=bool)
        selective_dynamics = list(selective_dynamics)
        poscar = Poscar(structure, selective_dynamics=selective_dynamics)
        return poscar

if __name__ == "__main__":
    # Call script as python gamma_input_set.py <path to POSCAR of structure>

    # Load structure
    structure = Poscar.from_file(sys.argv[1]).structure

    # Get VASP input files from the parameter set
    params = VaspBulk(structure, ggaU=False)
    incar = params.get_incar(relax=False)
    poscar = params.get_poscar()
    potcar = params.get_potcar()
    kpoints = params.get_kpoints()

    # WRite out VASP input files
    incar.write_file("INCAR")
    poscar.write_file("POSCAR")
    potcar.write_file("POTCAR")
    kpoints.write_file("KPOINTS")
