import itertools
import numpy as np
import spglib as spg
from collections import defaultdict
from ase.neighborlist import NeighborList

from .atoms import Atom, Atoms
from .get_clusters import get_clusters
from .get_orbits import get_orbits
from ..io.logging import logger
from .eigentensors import create_eigentensors as _create_eigentensors
from .constraints import create_constraint_map as _create_constraint_map
from .tensors import rotate_tensor
from .utilities import BiMap


# TODO: Add longer description of each step
# TODO: Be careful with side effects
# TODO: Preferably the functions should not take the cs as input
def build_cluster_space(cluster_space, prototype_structure):

    """ The permutation list is an indexed fast lookup table for permutation
    vectors.
    """
    logger.debug('Populate permutation list')
    _create_permutations(cluster_space)

    """ The primitive cell is calcualted by spglib and contains the cell
    metric, basis and atomic numbers. After this the prototype structure is
    disposed.
    """
    logger.debug('Get primitive cell')
    _create_primitive_cell(cluster_space, prototype_structure)

    """ The symmetries are calculated by spglib and the main information is the
    rotation matrices and translation vectors for each symmetry in scaled
    coordinates.
    """
    logger.debug('Get symmetries')
    _create_symmetry_dataset(cluster_space)

    """ The neigbor atoms to the center cell are stored in an indexed list. The
    list contains all atoms within the maximum cutoff specified.
    """
    logger.debug('Find neighbors')
    _create_atom_list(cluster_space)

    """ Clusters are generated as combinations of the indices of the atoms in
    the atom_list. If the cluster is to be included or not depends on the
    specification of valid clusters in the cutoffs object. Often all atoms must
    be within some distance from each other which may depend on both expansion
    order and number of atoms in the cluster
    """
    logger.debug('Starting generating clusters')
    _create_cluster_list(cluster_space)
    logger.debug('Finished generating clusters')

    """ The clusters are categorized into orbits and the eigensymmetries are
    stored in each orbit.
    """
    logger.info('Starting categorizing clusters')
    _create_orbits(cluster_space)
    logger.debug('Finished categorizing clusters')

    """ The eigensymmetries from the previous step is used to generate valid
    eigentensors
    """
    logger.info('Starting finding eigentensors')
    _create_eigentensors(cluster_space)
    logger.debug('Finished finding eigentensors')

    """ If some orbits can't have a force constant due to symmetry they are
    dropped from the _orbits attribute but kept in a separate list named
    _dropped_orbits
    """
    logger.debug('Dropping orbits...')
    _drop_orbits(cluster_space)

    """ Each orientation family gets populated with its rotated version of the
    orbits eigentensors.
    """
    logger.debug('Rotating eigentensors into ofs...')
    _populate_ofs_with_ets(cluster_space)

    """ The matrix describing the mapping which preserves the global symmetries
    is created (translational and rotational symmetry).
    """
    logger.debug('Constructing constraint map')
    _create_constraint_map(cluster_space)

    """  The eigentensors are rescaled depending on order to create a more well
    behaved system for fitting. NOTE! In here the constratints are rescaled too
    """
    logger.debug('Rescale eigentensors')
    _rescale_eigentensors(cluster_space)

    logger.debug('Normalize constraints')
    _normalize_constraint_vectors(cluster_space)

    logger.debug('Rotate tensors to Carteesian coordinates')
    _rotate_eigentensors(cluster_space)


# TODO: Actual input could be just the maximum order
# TODO: No side effects, returns only the permutation BiMap
def _create_permutations(cs):
    orders = cs.cutoffs.orders

    permutations = BiMap()
    for order in orders:
        for permutation in itertools.permutations(range(order)):
            permutations.append(permutation)

    cs._permutations = permutations


# TODO: tolerances must be fixed in a coherent way. Prefarably via a config
# object
# TODO: Add kw prim to CS init. To use the supplied primitive cell instead of
# having spglib return a funky rotated cell
# TODO: Does the basis check need to be done? There might not be a problem that
# it is close to 1 instead of 0 anymore. If thats the case it is better to keep
# it as spglib returns it
# TODO: Add good debug
# TODO: Assert spos dot cell == pos. Sometimes the positions can be outside of
# the cell and then there is a mismatch between wath is returned by
# get_sclad_positions, positions and what spos dot cell gives (it should give
# the position
# TODO: Check basis to see if it can be represented by sympy. (in preparation
# for rotational sum rules)
# TODO: general function -> break out into utility function
# TODO: Send the tolerance as a parameter instef of the whole cs.
def _create_primitive_cell(cs, prototype_structure):

    spgPrim = spg.standardize_cell(prototype_structure, no_idealize=True,
                                   to_primitive=True, symprec=cs.symprec)

    basis = spgPrim[1]
    if np.any(spgPrim[1] > (0.99)):
        logger.debug('Found basis close to 1:\n' +
                     ' {}'.format(str(spgPrim[1])))
        basis = spgPrim[1].round(8) % 1
        logger.debug('Wrapping to:\n' +
                     ' {}'.format(str(basis)))

    prim = Atoms(cell=spgPrim[0],
                 scaled_positions=basis,
                 numbers=spgPrim[2], pbc=True)

    logger.debug('Cell:\n{}'.format(prim.cell))
    logger.debug('Basis:\n{}'.format(prim.basis))
    logger.debug('Numbers: {}'.format(prim.numbers))

    cs._prim = prim


# TODO: Fix how the tolerance is handled
# TODO: Look over properties to acccess symmetry_dataset. Especially rotation,
# translation and wyckoff
# TODO: Sen prim and symprec as parameters
def _create_symmetry_dataset(cs):

    prim = cs._prim

    symmetry_dataset = spg.get_symmetry_dataset(prim, symprec=cs.symprec)

    cs._symmetry_dataset = symmetry_dataset

    logger.info('Spacegroup: {}'.format(cs.spacegroup))
    logger.info('Unique atoms: {}'.format(len(set(cs.wyckoff_sites))))
    logger.info('Symmetry operations: {}'.format(len(cs.rotation_matrices)))


# TODO: Fix how the tolerance is handled
# TODO: Refactor the two runs of finding the neighbors
# TODO: The bug that the cutoff is exactly on a shell might be a non issue.
# TODO: It is possible to check that the clusters map out the orbits completely
# TODO: Send in prim, cutoff and config and return atom_list instead
def _create_atom_list(cs):

    tol = cs.symprec

    atom_list = BiMap()

    # Populating the atom list with the center atoms
    for i in range(len(cs._prim)):
        atom_list.append(Atom(i, [0, 0, 0]))

    logger.info('Maximum cutoff: {}'.format(cs.cutoffs.max_cutoff))
    # Find all the atoms which is neighbors to the atoms in the center cell
    # The pair cutoff should be larger or equal than the others
    cutoffs = [(cs.cutoffs.max_cutoff - tol) / 2] * len(cs._prim)
    nl = NeighborList(cutoffs=cutoffs, skin=0, self_interaction=True,
                      bothways=True)
    nl.update(cs._prim)
    for i in range(len(cs._prim)):
        for index, offset in zip(*nl.get_neighbors(i)):
            atom = Atom(index, offset)
            if atom not in atom_list:
                atom_list.append(atom)

    nl = NeighborList(
        cutoffs=[(cs.cutoffs.max_cutoff + tol) / 2] *
        len(cs._prim), skin=0, self_interaction=True,
        bothways=True)
    nl.update(cs._prim)
    distance_from_cutoff = tol
    for i in range(len(cs._prim)):
        for index, offset in zip(*nl.get_neighbors(i)):
            atom = Atom(index, offset)
            # ... and check that no new atom is found
            if atom not in atom_list:
                pos = atom.pos(cs._prim.basis, cs._prim.cell)
                distance = min(np.linalg.norm(pos - atom.position)
                               for atom in cs._prim) - cs.cutoffs.max_cutoff
                distance_from_cutoff = min(distance, distance_from_cutoff)

    assert distance_from_cutoff == tol, \
        'Maximum cutoff close to neighbor shell! Change cutoff!'

    # TODO: Fix this mess
    logger.info('Found {0} center atom{3}'
                ' with {1} images'
                ' totaling {2} atoms'
                .format(len(cs._prim),
                        len(atom_list) - len(cs._prim),
                        len(atom_list),
                        's' if len(cs._prim) > 1 else ''))

    cs._atom_list = atom_list


# TODO: add atoms property to cs
# TODO: Only inputs are prim, atom_list and cutoffs
def _create_cluster_list(cs):

    # Convert the atom list from site/offset to scaled positions
    spos = [a.spos(cs._prim.basis) for a in cs._atom_list]
    # Make an atoms object out of the scaled positions
    atoms = Atoms(cell=cs._prim.cell,
                  scaled_positions=spos,
                  pbc=False)

    cs._cluster_list = get_clusters(atoms, cs.cutoffs, len(cs._prim))

    counter = defaultdict(lambda: 0)
    for c in cs._cluster_list:
        counter[len(c)] += 1
    logger.info('Number of force constants: {}'.format(dict(counter)))

    counter = defaultdict(lambda: 0)
    for c in cs._cluster_list:
        counter[len(set(c))] += 1
    logger.info('Number of clusters: {}'.format(dict(counter)))


def _create_orbits(cs):
    # TODO: Check scaled/cart
    cs._orbits = get_orbits(cs._cluster_list,
                            cs._atom_list,
                            cs.rotation_matrices,
                            cs.translation_vectors,
                            cs.permutations,
                            cs._prim)

    counter = defaultdict(lambda: 0)
    for orb in cs._orbits:
        counter[orb.order] += 1
    logger.info('Number of orbits: {}'.format(dict(counter)))


def _drop_orbits(cs):
    orbits_to_drop = []
    for i, orbit in enumerate(cs.orbits):
        if not orbit.eigentensors:
            orbits_to_drop.append(i)

    reduced_orbits = []
    cs._dropped_orbits = []

    for i in range(len(cs.orbits)):
        if i in orbits_to_drop:
            cluster = cs._cluster_list[cs.orbits[i].prototype_index]
            logger.info('  Dropping orbit {}: {}'.format(i, cluster))
            cs._dropped_orbits.append(cs.orbits[i])
        else:
            reduced_orbits.append(cs.orbits[i])
    cs._orbits = reduced_orbits

    logger.info('Found {} orbits after drop'.format(len(cs.orbits)))

    n_ets = dict()
    for order in cs.cutoffs.orders:
        n_ets[order] = sum(len(orb.eigentensors) for orb in cs.orbits
                           if orb.order == order)
    logger.info('Found {} eigentensors'.format(n_ets))


def _populate_ofs_with_ets(cs):

    for orbit_index, orbit in enumerate(cs.orbits):
        for of in orbit.orientation_families:
            R = cs.rotation_matrices[of.symmetry_index]
            R_inv_tmp = np.linalg.inv(R)
            R_inv = R_inv_tmp.astype(np.int64)
            assert np.allclose(R_inv, R_inv_tmp), (R_inv, R_inv_tmp)
            of.eigentensors = []
            for et in orbit.eigentensors:
                rotated_et = rotate_tensor(et, R_inv)
                assert rotated_et.dtype == np.int64
                of.eigentensors.append(rotated_et)


def _rotate_eigentensors(cs):
    V_invT = np.linalg.inv(cs._prim.cell.T)
    for orb in cs.orbits:
        orb.eigentensors = \
            [rotate_tensor(et, V_invT) for et in orb.eigentensors]
        for of in orb.orientation_families:
            of.eigentensors = \
                [rotate_tensor(et, V_invT) for et in of.eigentensors]


def _normalize_constraint_vectors(cs):
    M = cs._cvs
    norms = np.zeros(M.shape[1])
    for c, v in zip(M.col, M.data):
        norms[c] += v**2
    for i in range(len(norms)):
        norms[i] = np.sqrt(norms[i])
    for i, c in enumerate(M.col):
        M.data[i] /= norms[c]


def _rescale_eigentensors(cs):
    for orbit in cs.orbits:
        norm = cs.length_scale**orbit.order
        ets = orbit.eigentensors
        for i, et in enumerate(ets):
            ets[i] = et.astype(np.float64)
            ets[i] /= norm
        for of in orbit.orientation_families:
            ets = of.eigentensors
            for i, et in enumerate(ets):
                ets[i] = et.astype(np.float64)
                ets[i] /= norm

    orders = []
    for orbit in cs.orbits:
        for et in orbit.eigentensors:
            orders.append(orbit.order)

    M = cs._cvs
    for i, r in enumerate(M.row):
        M.data[i] *= cs.length_scale**orders[r]
