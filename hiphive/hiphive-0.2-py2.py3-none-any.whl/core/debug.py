# TODO: Docstring all functions
""" This module aims to collect debug functions for various parts of the core

"""
from ase.build import bulk
from ase.calculators.emt import EMT
from ase.neighborlist import NeighborList

from matplotlib import pyplot as plt
import itertools
import numpy as np
import spglib as spg

from .atoms import atom_to_spos
from .get_clusters import get_clusters
from .force_constant_model import ForceConstantModel
from .cluster_space import ClusterSpace


def debug_fcm_clusters(fcm, atoms, cutoffs):
    fcm_cluster_list = fcm.cluster_list
    debug_cluster_list = get_clusters(atoms, cutoffs, len(atoms))
#    assert len(fcm_cluster_list) == len(debug_cluster_list), \
#            (len(fcm_cluster_list), len(debug_cluster_list))
    for i, c_fcm in enumerate(fcm_cluster_list):
        c_fcm = sorted(c_fcm)
        if c_fcm not in debug_cluster_list:
            assert False, str(c_fcm) + ' not in debug list'
        for j, c_fcm2 in enumerate(fcm_cluster_list):
            c_fcm2 = sorted(c_fcm2)
            if i == j:
                continue
            assert c_fcm != c_fcm2, (i, j)
    print('All clusters seem to be found!')


def simple_test():
    prim = bulk('Al')
    cs = ClusterSpace(prim, [5, 5])
    atoms = bulk('Al', cubic=True).repeat(3)
    fcm = ForceConstantModel(atoms=atoms, cs=cs)
    atoms.calc = EMT()
    pos = atoms.positions.copy()
    atoms.rattle(0.01)
    disps = atoms.positions - pos
    F = atoms.get_forces().flatten()
    M = fcm.compute_fit_matrix(disps)
    a = np.linalg.lstsq(M, F)[0]
    plt.plot(F, np.dot(M, a),  '.')
    plt.savefig('test.pdf')


def validate_cs(cs):

    # Use spglib to try to find a primitive cell
    spg_prim = spg.standardize_cell(cs.prim, no_idealize=True,
                                    to_primitive=True, symprec=cs.symprec)

    # is the cell a valid cell?
    det = np.linalg.det(cs.prim.cell.T)
    assert det > 1e-12

    # is the cell the same size as spglibs?
    assert np.isclose(det, np.linalg.det(spg_prim[0].T))

    # is the basis compatible?
    assert sorted(cs.prim.numbers) == sorted(spg_prim[2])

    assert cs.spacegroup == spg.get_spacegroup(cs.prim, symprec=cs.symprec)

    # Is the prim spos within prim cell?
    for spos in cs.prim.basis:
        for s in spos:
            assert s >= 0 and s < 1-1e-4

    # Did the cs find the correct amount of atoms?
    cutoff = cs.cutoffs[2]
    nl = NeighborList([cutoff/2] * len(cs.prim), skin=0, self_interaction=True,
                      bothways=True)
    nl.update(cs.prim)
    atom_list = []
    for i in range(len(cs.prim)):
        for site, offset in zip(*nl.get_neighbors(i)):
            atom = (site, *offset)
            if atom not in atom_list:
                atom_list.append(atom)
    assert len(cs.atom_list) == len(atom_list)
    for atom in atom_list:
        assert atom in cs.atom_list
    for atom in cs.atom_list:
        assert tuple(atom) in atom_list

    # Is the first atoms in the atom list the center atoms?
    for i in range(len(cs.prim)):
        atom = cs.atom_list[i]
        assert atom.site == i and tuple(atom.offset) == (0, 0, 0)

    # Does all clusters contain any of the center atoms?
    prim_set = set(range(len(cs.prim)))
    for cluster in cs.cluster_list:
        assert not prim_set.isdisjoint(cluster)

    # Does the clusters obey the cutoff
    spos = [atom_to_spos(atom, cs.prim.basis) for atom in cs.atom_list]
    pos = [np.dot(spos, cs.prim.cell) for sp in spos]
    for cluster in cs.cluster_list:
        order = len(cluster)
        cutoff = cs.cutoffs[order]
        for i, j in itertools.combinations(set(cluster), r=2):
            assert np.linalg.norm(pos[i] - pos[j]) < cutoff

    for orbit in cs.orbits:
        prototype_index = orbit.prototype_index
        prototype_cluster = cs.cluster_list[prototype_index]
        order = len(prototype_cluster)
        assert orbit.order == order
        prototype_distances = []
        for i, j in itertools.combinations(set(prototype_cluster), r=2):
            distance = np.linalg.norm(pos[i] - pos[j])
            assert distance < orbit.maximum_distance
            prototype_distances.append(distance)
        prototype_distances = sorted(prototype_distances)
        for of in orbit.orientation_families:
            cluster_index = of.cluster_indices[0]
            cluster = cs.cluster_list[cluster_index]
            order = len(cluster)
            assert orbit.order == order
            distances = []
            for i, j in itertools.combinations(set(cluster), r=2):
                distance = np.linalg.norm(pos[i] - pos[j])
                assert distance < orbit.maximum_distance
                distances.append(distance)
            distances = sorted(distances)
            assert np.allclose(distances, prototype_distances)

    nirred = cs.num_degrees_of_freedom
    irred = np.random.random(nirred)
    params = cs._map_parameters(irred)
#    params = []
#    for order in sorted(cs.cutoffs.keys()):
#       params.extend(list(cs._constraint_vectors[order][0]))
    i = 0
    for orb in cs.orbits:
        for of in orb.orientation_families:
            fc = np.zeros([3]*orb.order)

            for j, et in enumerate(of.eigentensors):
                fc += et * params[i+j]
            of.force_constant = fc
        i += len(orb.eigentensors)

    previous_cluster_prefix = None
    for order in sorted(cs.cutoffs):
        for cluster in cs.cluster_list:
            if len(cluster) != order:
                continue
            if cluster[:-1] == previous_cluster_prefix:
                continue
            else:
                previous_cluster_prefix = cluster[:-1]
            FC = np.zeros([3] * order)
            for i in range(len(cs.atom_list)):
                cluster = (*cluster[:-1], i)
                argsort = np.argsort(cluster)
                try:
                    cluster_index = cs.cluster_list.index(sorted(cluster))
                except ValueError:
                    continue
                fc = np.zeros([3] * order)
                for orbit in cs.orbits:
                    for of in orbit.orientation_families:
                        if cluster_index in of.cluster_indices:
                            ind = of.cluster_indices.index(cluster_index)
                            perm = cs.permutations[of.permutation_indices[ind]]
                            fc = of.force_constant.transpose(perm)
                fc = fc.transpose(np.argsort(argsort))
                if not np.any(fc):
                    continue
                FC += fc
            assert np.allclose(FC, 0), (cluster, FC)
