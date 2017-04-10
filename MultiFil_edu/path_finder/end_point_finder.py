#!/usr/bin/env python
from collections import defaultdict

import numpy as np
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

__author__ = 'Shaun Rong'
__version__ = '0.1'
__maintainer__ = 'Shaun Rong'
__email__ = 'rongzq08@gmail.com'


class EndPointFinder(object):
    def __init__(self, struct, specie):
        """
        This class digest a structure and the moving cation species, and output the most possible diffusion end points
        in the structure
        :param struct: a pymatgen.core.structure.Structure object
        :param specie: the moving cation species, a pymatgen.core.periodic_table.Element object
        """
        self._struct = struct
        self._specie = specie

    def get_gamma_struct(self, struct, sites):
        """
        Take two end sites out of the structure (or super structure constructed), be noticed that the sites come from a
        2 * 2 * 2 supercell of the API struct, thus have to first examine the coordinations of the sites to see if the
        API struct needs to be expanded.
        :param struct: the structure from API
        :param site: the site being taken out, needs to be one of the end points
        :return: structure for later gamma point calculations.
        """
        supercell_matrix = [1, 1, 1]
        for i in range(3):
            temp_coord_0 = sites[0].frac_coords[i]
            temp_coord_1 = sites[1].frac_coords[i]
            if temp_coord_0 > 0.5 or temp_coord_1 > 0.5:
                supercell_matrix[i] = 2

        struct.make_supercell(supercell_matrix)

        struct_s1 = struct.copy()
        removed_indices_s1 = []
        struct_s2 = struct.copy()
        removed_indices_s2 = []
        struct_gamma = struct.copy()
        removed_indices_gamma = []

        scale = np.divide(np.ones(3, dtype=float) * 2, np.array(supercell_matrix))
        frac_coord_0 = np.multiply(sites[0].frac_coords, scale)
        #debug
        #print "frac_coord_0 is " + str(frac_coord_0)
        frac_coord_1 = np.multiply(sites[1].frac_coords, scale)
        #debug
        #print "frac_coord_1 is " + str(frac_coord_1)
        for s in range(len(struct.sites)):
            site_fc = struct.sites[s].frac_coords
            if struct.sites[s].specie == sites[0].specie:
                removed_indices_gamma.append(s)
                if not EndPointFinder.periodic_equal(site_fc, frac_coord_0):
                    removed_indices_s1.append(s)
                if not EndPointFinder.periodic_equal(site_fc, frac_coord_1):
                    removed_indices_s2.append(s)

        struct_s1.remove_sites(removed_indices_s1)
        struct_s2.remove_sites(removed_indices_s2)
        struct_gamma.remove_sites(removed_indices_gamma)

        return struct_s1, struct_s2, struct_gamma

    def get_empty_lattice_neb_init_structs(self, struct, sites):
        supercell_matrix = [1, 1, 1]
        for i in range(3):
            temp_coord_0 = sites[0].frac_coords[i]
            temp_coord_1 = sites[1].frac_coords[i]
            if temp_coord_0 > 0.5 or temp_coord_1 > 0.5:
                supercell_matrix[i] = 2

        struct.make_supercell(supercell_matrix)

        struct_s1 = struct.copy()
        struct_s2 = struct.copy()

        scale = np.divide(np.ones(3, dtype=float) * 2, np.array(supercell_matrix))
        frac_coord_0 = np.multiply(sites[0].frac_coords, scale)
        frac_coord_1 = np.multiply(sites[1].frac_coords, scale)

        struct_s1.remove_species([self._specie])
        struct_s2.remove_species([self._specie])

        struct_s1.insert(0, sites[0].specie, frac_coord_0)
        struct_s2.insert(0, sites[1].specie, frac_coord_1)

        return (struct_s1, struct_s2)

    def get_vancancy_lattice_neb_init_structs(self, struct, sites):
        supercell_matrix = [1, 1, 1]
        for i in range(3):
            temp_coord_0 = sites[0].frac_coords[i]
            temp_coord_1 = sites[1].frac_coords[i]
            if temp_coord_0 > 0.5 or temp_coord_1 > 0.5:
                supercell_matrix[i] = 2

        struct.make_supercell(supercell_matrix)

        struct_s1 = struct.copy()
        removed_indices = []
        struct_s2 = struct.copy()

        scale = np.divide(np.ones(3, dtype=float) * 2, np.array(supercell_matrix))
        frac_coord_0 = np.multiply(sites[0].frac_coords, scale)
        frac_coord_1 = np.multiply(sites[1].frac_coords, scale)

        for s in range(len(struct.sites)):
            site_fc = struct.sites[s].frac_coords
            if struct.sites[s].specie == sites[0].specie:
                if EndPointFinder.periodic_equal(site_fc, frac_coord_0) or EndPointFinder.periodic_equal(site_fc,
                                                                                                         frac_coord_1):
                    removed_indices.append(s)

        struct_s1.remove_sites(removed_indices)
        struct_s1.insert(0, sites[1].specie, sites[1].frac_coords)
        struct_s2.remove_sites(removed_indices)
        struct_s2.insert(0, sites[0].specie, sites[0].frac_coords)

        return (struct_s1, struct_s2)

    def get_end_point_pairs(self):
        """
        will change self._struct into supercell structure if necessary
        the distinct sites in list should be less than 4.
        :return: a list of end points pairs for diffusion
        """
        self._struct.make_supercell([2, 2, 2])
        moving_cation = []

        #Get symmetric equivalent sites
        analyzed_struct = SpacegroupAnalyzer(self._struct)
        analyzed_struct = analyzed_struct.get_symmetrized_structure()
        equivalent_sites = analyzed_struct.equivalent_sites
        #Debug
        #print len(equivalent_sites)

        for site in self._struct.sites:
            if site.specie == self._specie:
                moving_cation.append(site)
        #Debug
        #print len(moving_cation)

        distance = 100 * np.ones((len(moving_cation), len(moving_cation)), dtype=float)
        for i in range(len(moving_cation)):
            for j in range(i):
                distance[i][j] = moving_cation[i].distance(moving_cation[j])

        min_distance = np.amin(distance)
        min_distance_pairs = []

        for i in range(len(moving_cation)):
            for j in range(i):
                if distance[i][j] < min_distance * 1.15:
                    min_distance_pairs.append([i, j])
        #Debug
        #print min_distance_pairs
        #print len(min_distance_pairs)

        cation_group_num = []
        for group in range(len(equivalent_sites)):
            if equivalent_sites[group][0].specie == self._specie:
                cation_group_num.append(group)

        group_pair = {}
        for i in range(len(cation_group_num)):
            for j in range(i+1):
                group_pair[(cation_group_num[i], cation_group_num[j])] = []

        for pair in min_distance_pairs:
            for group in range(len(equivalent_sites)):
                if moving_cation[pair[0]] in equivalent_sites[group]:
                    group_i = group
                if moving_cation[pair[1]] in equivalent_sites[group]:
                    group_j = group
            (group_i, group_j) = EndPointFinder._reorder(group_i, group_j)

            if moving_cation[pair[0]] in equivalent_sites[group_i]:
                group_pair[(group_i, group_j)].append([moving_cation[pair[0]], moving_cation[pair[1]]])
            else:
                group_pair[(group_i, group_j)].append([moving_cation[pair[1]], moving_cation[pair[0]]])

        end_point_pair = []
        for pairs in group_pair.values():
            if pairs:
                selected_pair = pairs[0]
                coordin_sum = 10
                for pair in pairs:
                    if np.sum(pair[0].frac_coords) + np.sum(pair[1].frac_coords) < coordin_sum:
                        selected_pair = pair
                        coordin_sum = np.sum(pair[0].frac_coords) + np.sum(pair[1].frac_coords)
                end_point_pair.append(selected_pair)

        return end_point_pair

    def get_shortest_equiv_pairs(self):
        self._struct.make_supercell([2, 2, 2])
        moving_cation = []

        #Get symmetric equivalent sites
        analyzed_struct = SpacegroupAnalyzer(self._struct)
        analyzed_struct = analyzed_struct.get_symmetrized_structure()
        equivalent_sites = analyzed_struct.equivalent_sites
        #Debug
        #print len(equivalent_sites)

        for site in self._struct.sites:
            if site.specie == self._specie:
                moving_cation.append(site)
        #Debug
        #print len(moving_cation)

        distance = 100 * np.ones((len(moving_cation), len(moving_cation)), dtype=float)
        for i in range(len(moving_cation)):
            for j in range(i):
                distance[i][j] = moving_cation[i].distance(moving_cation[j])

        min_distance = np.amin(distance)
        min_distance_pairs = []

        for i in range(len(moving_cation)):
            for j in range(i):
                if distance[i][j] < min_distance * 1.20:
                    min_distance_pairs.append([i, j])
        #Debug
        #print min_distance_pairs
        #print len(min_distance_pairs)

        cation_group_num = []
        for group in range(len(equivalent_sites)):
            if equivalent_sites[group][0].specie == self._specie:
                cation_group_num.append(group)

        group_pair = defaultdict(lambda: [])

        for pair in min_distance_pairs:
            for group in range(len(equivalent_sites)):
                if moving_cation[pair[0]] in equivalent_sites[group]:
                    group_i = group
                if moving_cation[pair[1]] in equivalent_sites[group]:
                    group_j = group

            if group_i == group_j:
                group_pair[(group_i, group_j)].append([moving_cation[pair[0]], moving_cation[pair[1]]])

        end_point_pair = []
        for pairs in group_pair.values():
            if pairs:
                selected_pair = pairs[0]
                coordin_sum = 10
                for pair in pairs:
                    if np.sum(pair[0].frac_coords) + np.sum(pair[1].frac_coords) < coordin_sum:
                        selected_pair = pair
                        coordin_sum = np.sum(pair[0].frac_coords) + np.sum(pair[1].frac_coords)
                end_point_pair.append(selected_pair)

        return end_point_pair

    @staticmethod
    def _reorder(group_i, group_j):
        if group_i >= group_j:
            return tuple([group_i, group_j])
        else:
            return tuple([group_j, group_i])

    @staticmethod
    def periodic_equal(frac_coord_1, frac_coord_2):
        if type(frac_coord_1) != np.ndarray or type(frac_coord_2) != np.ndarray:
            raise TypeError("Input fractional coordinates are not numpy arrays.")
        if len(frac_coord_1) != 3 or len(frac_coord_2) != 3:
            raise ValueError("Coordinates array are not 3-dimensional.")
        diff = abs(frac_coord_1 - frac_coord_2)
        compare = False
        possible_equals = [np.array([1, 1, 1]), np.array([0, 0, 0]), np.array([1, 0, 0]),
                           np.array([0, 1, 0]), np.array([0, 0, 1]), np.array([1, 1, 0]),
                           np.array([1, 0, 1]), np.array([0, 1, 1])]
        for array in possible_equals:
            if np.allclose(diff, array, atol=1e-3):
                compare = True
        return compare