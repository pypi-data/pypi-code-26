# Contains the get_orbits function which categorizes clusters into orbits and
# orientation families

from .utilities import BiMap
from .atoms import Atom
from .orbit import Orbit, get_geometrical_radius, get_maximum_distance
from .orientation_family import OrientationFamily
from ..io.logging import logger

import numpy as np

logger = logger.getChild('get_orbits')


# This is the interface accessible for cluster_space
def get_orbits(cluster_list, atom_list, rotation_matrices, translation_vectors,
               permutations, prim):
    """Generate a list of the orbits for the clusters in a supercell
    configuration.

    This method requires as input a list of the clusters in a supercell
    configuration as well as a set of symmetry operations (rotations and
    translations). From this information it will generate a list of the orbits,
    i.e. the set of symmetry inequivalent clusters each associated with its
    respective set of equivalent clusters.

    Parameters
    ----------
    cluster_list : BiMap object
        a list of clusters
    atom_list : BiMap object
        a list of atoms in a supercell
    rotation_matrices : list of NumPy (3,3) arrays
        rotational symmetries to be imposed (e.g., from spglib)
    translation_vectors : list of NumPy (3) arrays
        translational symmetries to be imposed (e.g., from spglib)
    permutations : list of permutations
        lookup table for permutations
    prim : hiPhive Atoms object
        primitive structure

    Returns
    -------
    list of Orbits objs
        orbits associated with the list of input clusters

    """

    logger.debug('Preparing input...')
    atoms = prepare_atoms(atom_list)
    clusters = prepare_clusters(cluster_list)
    rotations = prepare_rotations(rotation_matrices)
    translations = prepare_translations(translation_vectors)
    permutations = prepare_permutations(permutations)
    cell = prim.cell
    basis = prim.get_scaled_positions()

    logger.debug('Creating permutation map...')
    permutation_map, extended_atoms = \
        get_permutation_map(atoms, rotations, translations, basis)

    logger.debug('Creating orbits...')
    orbits = _get_orbits(permutation_map, extended_atoms, clusters, basis,
                         cell, rotations, permutations)

    return orbits


# All prepares are in case we changes some interface stuff

def prepare_permutations(permutations):
    perms = BiMap()
    for p in permutations:
        perms.append(tuple(p))
    return perms


def prepare_atoms(atom_list):
    atoms = BiMap()
    for atom in atom_list:
        atoms.append(atom)
    return atoms


def prepare_clusters(cluster_list):
    clusters = BiMap()
    for cluster in cluster_list:
        clusters.append(tuple(cluster))
    return clusters


def prepare_rotations(rotation_matrices):
    return rotation_matrices


def prepare_translations(translation_vectors):
    return translation_vectors


def get_permutation_map(atoms, rotations, translations, basis):

    extended_atoms = atoms.copy()

    permutation_map = np.zeros((len(atoms), len(rotations)), dtype=int)

    scaled_positions = [atom.spos(basis) for atom in extended_atoms]

    for sym_index, (R, T) in enumerate(zip(rotations, translations)):
        for atom_index, spos in enumerate(scaled_positions):

            new_spos = np.dot(R, spos) + T
            new_atom = Atom.spos_to_atom(new_spos, basis)

            if new_atom not in extended_atoms:
                extended_atoms.append(new_atom)

            mapped_atom_index = extended_atoms.index(new_atom)
            permutation_map[atom_index, sym_index] = mapped_atom_index

    return permutation_map, extended_atoms


# The internal function doing the outer loop over orbits
def _get_orbits(permutation_map, extended_atoms, clusters,
                basis, cell,
                rotations, permutations):
    cluster_is_found = [False] * len(clusters)
#    with ProgressManager(len(clusters)) as bar:
    orbits = []
    for cluster_index, cluster in enumerate(clusters):
        if cluster_is_found[cluster_index]:
            continue

        orbit = Orbit()

        cluster_atoms = [extended_atoms[i] for i in cluster]

        positions = [atom.pos(basis, cell) for atom in cluster_atoms]
        orbit.radius = get_geometrical_radius(positions)
        orbit.maximum_distance = get_maximum_distance(positions)
        orbit.order = len(cluster)

        populate_orbit(orbit, permutations, clusters,
                       cluster,
                       permutation_map, extended_atoms,
                       cluster_is_found)
        orbits.append(orbit)

#            bar.tick()
    return orbits


# Takes a cluster and generates all equivalent, translated clusters
def generate_translated_clusters(cluster, extended_atoms):
    transformed_cluster_atoms = [extended_atoms[i] for i in cluster]
    tested_offsets = set()
    for atom in transformed_cluster_atoms:
        offset = atom.offset
        if offset in tested_offsets:
            continue
        else:
            tested_offsets.add(offset)
        translated_cluster = []
        for atom in transformed_cluster_atoms:
            new_offset = np.subtract(atom.offset, offset)
            new_atom = Atom(atom.site, new_offset)
            translated_cluster.append(extended_atoms.index(new_atom))
        yield tuple(translated_cluster)


# Here is the actual categorization
def populate_orbit(orbit, permutations, clusters,
                   cluster,
                   permutation_map, extended_atoms,
                   cluster_is_found):
    for sym_index in range(permutation_map.shape[1]):

        of = OrientationFamily(sym_index)

        transformed_cluster = permutation_map[cluster, sym_index]

        for translated_cluster in generate_translated_clusters(
                transformed_cluster, extended_atoms):

            argsort = tuple(np.argsort(translated_cluster))
            perm_index = permutations.index(argsort)

            translated_cluster = tuple(sorted(translated_cluster))
            translated_cluster_index = clusters.index(translated_cluster)

            if cluster == translated_cluster:
                if (sym_index, perm_index) not in orbit.eigensymmetries:
                    orbit.eigensymmetries.append((sym_index, perm_index))

            if not cluster_is_found[translated_cluster_index]:
                cluster_is_found[translated_cluster_index] = True
                of.cluster_indices.append(translated_cluster_index)
                of.permutation_indices.append(perm_index)

        if len(of.cluster_indices) > 0:
            orbit.orientation_families.append(of)

    return orbit
