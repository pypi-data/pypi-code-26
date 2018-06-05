"""
Contains the ClusterSpace object central to hiPhive
"""

import itertools
import numpy as np
import spglib as spg
import tarfile

from ase.neighborlist import NeighborList
from ase.data import chemical_symbols
from collections import Counter, OrderedDict
from copy import deepcopy
from scipy.linalg import lu

from .core import core_config
from .core.atoms import Atom, Atoms
from .core.utilities import BiMap
from .core.get_clusters import get_clusters
from .core.get_orbits import get_orbits
from .core.eigentensor_symmetrizer import symmetrize_tensor
from .core.orbit import Orbit
from .core.tensors import rotation_to_cart_coord, rotate_tensor
from .io.logging import logger, Progress
from .io.read_write_files import (add_items_to_tarfile_hdf5,
                                  add_items_to_tarfile_pickle,
                                  add_items_to_tarfile_custom,
                                  add_list_to_tarfile_custom,
                                  read_items_hdf5,
                                  read_items_pickle,
                                  read_list_custom)
from .cluster_filter import Cutoffs, CutoffMaximumBody


try:
    import sympy
except ImportError:
    logger.warning('Sympy not present')

logger = logger.getChild('cs')  # TODO: Give better name?


class ClusterSpace:
    # TODO: Inherit from base class to ease the use of FCP
    # TODO: Is this type of docstring correct?
    # TODO: Fix cutoffs parameter when new Cutoffs objects is implemented
    """Primitive object handling cluster and force constants for a structure.

    Parameters
    ----------
    prototype_struture : ASE Atoms object
        prototype structure; spglib will be used to find a suitable cell based
        on this structure.
    cutoffs : list or Cutoffs obj
        cutoff radii for different orders starting with second order
    sum_rules : bool
        If True the aucostic sum rules will be enforced by constraining the
        parameters.
    symprec : float
        numerical precision that will be used for analyzing the symmetry (this
        parameter will be forwarded to
        `spglib <https://atztogo.github.io/spglib/>`_)
    length_scale : float
        This will be used as a normalization constant for the eigentensors

    Examples
    --------
    To instantiate a ClusterSpace object one has to specify a prototype
    structure and cutoff radii for each cluster order that should be included.
    For example the following snippet will set up a ClusterSpace object for a
    BCC structure including second order terms up to a distance of 5 A and
    third order terms up to a distance of 4 A.

    >>> from ase.build import bulk
    >>> prim = bulk('W')
    >>> cs = ClusterSpace(prim, [5.0, 4.0])
    """
    # TODO: This class probably need some more documentation and a reference to
    # the thesis
    # TODO: Fix doc for n-body cutoff

    def __init__(self, prototype_structure, cutoffs,
                 sum_rules=True, symprec=1e-5, length_scale=0.1):

        if isinstance(cutoffs, Cutoffs):
            self._cutoffs = cutoffs
        if isinstance(cutoffs, list):
            self._cutoffs = CutoffMaximumBody(cutoffs, len(cutoffs) + 1)

        self._symprec = symprec
        self._length_scale = length_scale
        self._sum_rules = sum_rules

        self._atom_list = BiMap()
        self._cluster_list = None
        self._symmetry_dataset = None
        self._permutations = []
        self._prim = None
        self._orbits = []

        self._constraint_vectors = None
        # TODO: How to handle the constraint matrices? Should they even be
        # stored?
        self._constraint_matrices = None
        # Is this the best way or should the prim be instantiated separately?

        self._build(prototype_structure)

    # TODO: Should everything here be properties? deepcopy/ref etc.?
    # TODO: Docstrings for properties
    @property
    def number_of_dofs(self):
        """int : number of free parameters in the model

        If the sum rules are not enforced the number of DOFs is the same as
        the total number of eigentensors in all orbits.
        """
        return sum(self._get_number_of_dofs(order) for order in
                   self.cutoffs.orders)

    @property
    def cutoffs(self):
        """ Cutoffs object : cutoffs used for constructing the cluster space
        """
        return deepcopy(self._cutoffs)

    @property
    def symprec(self):
        """ float : symprec value used when constructing the cluster space
        """
        return self._symprec

    @property
    def sum_rules(self):
        """ bool : True if sum rules are enforced """
        return self._sum_rules

    @property
    def length_scale(self):
        """ float : normalization constant of the force constants """
        return self._length_scale

    @property
    def prim(self):
        """ ASE Atoms object : structure of the lattice """
        return self._prim.copy()

    @property
    def spacegroup(self):
        """ str : space group of the lattice structure obtained from spglib """
        return self._symmetry_dataset['international'] + ' ({})'.format(
            self._symmetry_dataset['number'])

    @property
    def wyckoff_sites(self):
        """ list : wyckoff sites in the primitive cell"""
        return self._symmetry_dataset['equivalent_atoms']

    @property
    def rotation_matrices(self):
        """ list of 3x3 matrices : symmetry elements representing rotations """
        return self._symmetry_dataset['rotations'].copy()

    @property
    def translation_vectors(self):
        """ list of 3-vectors : symmetry elements representin translations """
        # TODO: bug incoming!
        return (self._symmetry_dataset['translations'] % 1).copy()

    @property
    def permutations(self):
        """ list of vectors : lookup for permutation references """
        return deepcopy(self._permutations)

    @property
    def atom_list(self):
        """ BiMap object : atoms inside the cutoff relative to the of the
                           center cell """
        return self._atom_list

    @property
    def cluster_list(self):
        """ BiMap object : clusters possible within the cutoff """
        return self._cluster_list

    @property
    def orbits(self):  # TODO: add __getitem__ method
        """ list of Orbit objects : orbits associated with the lattice
                                    structure. """
        return self._orbits

    @property
    def orbit_data(self):
        """ list : list of dictionaries containing detailed information for
                   each orbit, e.g., cluster radius and atom types.
        """
        data = []
        p = 0
        for orbit_index, orbit in enumerate(self.orbits):
            d = {}
            d['index'] = orbit_index
            d['order'] = orbit.order
            d['radius'] = orbit.radius
            d['maximum_distance'] = orbit.maximum_distance
            d['number_of_clusters'] = len(orbit.orientation_families)
            d['eigentensors'] = orbit.eigentensors
            d['number_of_parameters'] = len(d['eigentensors'])

            types, wyckoff_sites = [], []
            for atom_index in self.cluster_list[orbit.prototype_index]:
                atom = self.atom_list[atom_index]
                types.append(self.prim.numbers[atom.site])
                wyckoff_sites.append(self.wyckoff_sites[atom.site])
            d['prototype_cluster'] = self.cluster_list[orbit.prototype_index]
            d['prototype_atom_types'] = tuple(types)
            d['prototype_wyckoff_sites'] = tuple(wyckoff_sites)

            d['geometrical_order'] = len(set(d['prototype_cluster']))
            d['parameter_indices'] = np.arange(p, p + len(orbit.eigentensors))

            p += len(orbit.eigentensors)
            data.append(d)

        return data

    def print_orbits(self):
        """ Prints a list of all orbits. """
        orbits = self.orbit_data

        def str_orbit(index, orbit):
            elements = ' '.join(chemical_symbols[n] for n in
                                orbit['prototype_atom_types'])
            fields = OrderedDict([
                ('index',        '{:^3}'.format(index)),
                ('order',        '{:^3}'.format(orbit['order'])),
                ('elements',     '{:^18}'.format(elements)),
                ('radius',       '{:^8.4f}'.format(orbit['radius'])),
                ('prototype',    '{:^18}'
                 .format(str(orbit['prototype_cluster']))),
                ('clusters',     '{:^4}'.format(orbit['number_of_clusters'])),
                ('parameters',   '{:^3}'.format(len(orbit['eigentensors']))),
                ])

            s = []
            for name, value in fields.items():
                n = max(len(name), len(value))
                if index < 0:
                    s += ['{s:^{n}}'.format(s=name, n=n)]
                else:
                    s += ['{s:^{n}}'.format(s=value, n=n)]
            return ' | '.join(s)

        # table header
        width = max(len(str_orbit(-1, orbits[-1])),
                    len(str_orbit(0, orbits[-1])))
        print(' List of Orbits '.center(width, '='))
        print(str_orbit(-1, orbits[0]))
        print(''.center(width, '-'))

        # table body
        for i, orbit in enumerate(orbits):
            print(str_orbit(i, orbit))
        print(''.center(width, '='))

    def _get_number_of_dofs(self, order):
        """ Returns the number of degrees of freedom per order. """
        if self.sum_rules:
            return len(self._constraint_vectors[order])
        else:
            return sum((len(orb.eigentensors) for orb in self.orbits
                        if orb.order == order))

    def __str__(self):

        def str_order(order, header=False):
            formats = {'order':        '{:2}',
                       'num_orbits':   '{:5}',
                       'num_params':   '{:5}',
                       'num_clusters': '{:5}'}
            s = []
            for name, value in order.items():
                str_repr = formats[name].format(value)
                n = max(len(name), len(str_repr))
                if header:
                    s += ['{s:^{n}}'.format(s=name, n=n)]
                else:
                    s += ['{s:^{n}}'.format(s=str_repr, n=n)]
            return ' | '.join(s)

        # collect data
        orbits = self.orbit_data
        orders = OrderedDict(
            (order, OrderedDict(order=order)) for order in self.cutoffs.orders)
        for orbit in orbits:
            k = orbit['order']
            orders[k]['num_orbits'] = orders[k].get('num_orbits', 0) + 1
            orders[k]['num_clusters'] = orders[k].get('num_clusters', 0) + \
                orbit['number_of_clusters']
        for order, order_summary in orders.items():
            order_summary['num_params'] = self._get_number_of_dofs(order)

        # basic information
        prototype = orders[list(orders.keys())[-1]]
        n = max(len(str_order(prototype)), 54)
        s = []
        s.append(' Cluster Space '.center(n, '='))
        data = [('Spacegroup',                 self.spacegroup),
                ('symprec',                    self.symprec),
                ('Sum Rules',                  self.sum_rules),
                ('Length scale',               self.length_scale),
                ('Cutoffs',                    self.cutoffs),
                ('Cell',                       self.prim.cell),
                ('Basis',                      self.prim.basis),
                ('Numbers',                    self.prim.numbers),
                ('Total number of orbits',     len(orbits)),
                ('Total number of clusters',
                 sum([order['num_clusters'] for order in orders.values()])),
                ('Total number of parameters',
                 sum([order['num_params'] for order in orders.values()]))]
        for field, value in data:
            if str(value).count('\n') > 1:
                s.append('{:26} :\n{}'.format(field, value))
            else:
                s.append('{:26} : {}'.format(field, value))

        # table header
        s.append(''.center(n, '-'))
        s.append(str_order(prototype, header=True))
        s.append(''.center(n, '-'))
        for order in orders.values():
            s.append(str_order(order).rstrip())
        s.append(''.center(n, '='))
        return '\n'.join(s)

    def __repr__(self):
        s = 'ClusterSpace({!r}, {!r}, {!r}, {!r}, {!r})'
        return s.format(self.prim, self.cutoffs, self.sum_rules, self.symprec,
                        self.length_scale)

    # TODO: Fix this mess
    def _build(self, prototype_structure):
        """Builds the cluster space.

        The steps are
        1. Populate the permutation list
        2. Find the primitive cell
        3. Find the neighborhood
        4. Find all possible clusters
        5. Get all symmetries with spglib
        6. Categorize the orbits
        7. Finding the eigentensors of the orbits

        Todo
        ----
        Fill in the rest and link to thesis
        """

        # TODO: state the difference between this and the permutation map
        logger.debug('Populating permutation list...')
        # Populate a list with all the different permutations possible from
        # order 2 up to the maximum order. Used as a lookup.
        for order in self.cutoffs.orders:
            for permutation in itertools.permutations(range(order)):
                self._permutations.append(list(permutation))

        # TODO: Make new function of this
        logger.debug('Finding primitive cell...')
        # Uses spglib to find the standardized primitive cell of the structure
        spgPrim = spg.standardize_cell(prototype_structure,
                                       no_idealize=True, to_primitive=True,
                                       symprec=self.symprec)
        # Make sure that spglib does not give a strange primitive cell
        # TODO: This is the same as a function in atoms.py
        # (relate_structures)
        basis = spgPrim[1]
        if np.any(spgPrim[1] > (0.99)):
            logger.debug('Found basis close to 1:\n' +
                         ' {}'.format(str(spgPrim[1])))
            basis = spgPrim[1].round(8) % 1
            logger.debug('Wrapping to:\n' +
                         ' {}'.format(str(basis)))
        self._prim = Atoms(cell=spgPrim[0],
                           scaled_positions=basis,
                           numbers=spgPrim[2], pbc=True)

        logger.debug('Finding symmetry dataset with spglib...')
        self._symmetry_dataset = spg.get_symmetry_dataset(self.prim,
                                                          symprec=self.symprec)
        logger.info('Found Spacegroup: {}'.format(self.spacegroup))
        logger.debug('Cell:\n{}'.format(self._prim.cell))
        logger.debug('Basis: {}'.format(self._prim.basis))
        logger.debug('Numbers: {}'.format(self._prim.numbers))
        logger.info('Found {} symmetry operations'
                    ''.format(len(self.rotation_matrices)))

        # Populating the atom list with the center atoms
        for i in range(len(self.prim)):
            self._atom_list.append(Atom(i, [0, 0, 0]))

        # TODO: Large scope, refactor!
        logger.info('Starting finding neighbors')
        logger.info('Using cutoffs\n{}'.format(self.cutoffs))
        # Find all the atoms which is neighbors to the atoms in the center cell
        # The pair cutoff should be larger or equal than the others
        # TODO: fix how cutoffs access larges cutoff
        cutoffs = [self.cutoffs.max_cutoff / 2] * len(self.prim)
        nl = NeighborList(cutoffs=cutoffs, skin=0, self_interaction=True,
                          bothways=True)
        nl.update(self.prim)
        for i in range(len(self.prim)):
            for index, offset in zip(*nl.get_neighbors(i)):
                atom = Atom(index, offset)
                # Make sure a common neighbor is not added twice
                # TODO: Can nl be initialized so this doesn't happen? Should
                # atom_list take care of this i.g. atom_set
                if atom not in self._atom_list:
                    self._atom_list.append(atom)
        # Do an extra run to see if near a new shell and throw warning if so
        # TODO: Also why this should be refactored
        # TODO: Fix random tol 0.01
        nl = NeighborList(
            cutoffs=[(self.cutoffs.max_cutoff + 0.01) / 2] *
            len(self.prim), skin=0, self_interaction=True,
            bothways=True)  # TODO: Fix these ugly lines
        nl.update(self.prim)
        # TODO: Get rid of breaks and continues
        # Do the same thing again...
        for i in range(len(self.prim)):
            for index, offset in zip(*nl.get_neighbors(i)):
                atom = Atom(index, offset)
                # ... and check that no new atom is found
                if atom not in self._atom_list:
                    logger.warning('Found atoms within 0.01 of cutoff')
                    break
            else:
                continue
            break
        logger.info('Finished finding neighbors')
        logger.info('Found {0} center atom{3}'
                    ' with {1} images'
                    ' totaling {2} atoms'
                    .format(len(self.prim),
                            len(self._atom_list) - len(self.prim),
                            len(self._atom_list),
                            's' if len(self.prim) > 1 else ''))

        logger.debug('Creating cluster list...')
        # Convert the atom list from site/offset to scaled positions
        spos = [a.spos(self.prim.basis) for a in self._atom_list]
        # Make an atoms obect out of the scaled positions
        atoms = Atoms(cell=self.prim.cell,
                      scaled_positions=spos,
                      pbc=False)

#        positions = atoms.positions
#        argsort_z = np.argsort(positions[:, 2], kind='merge')
#        positions = positions[argsort_z]
#        argsort_y = np.argsort(positions[:, 1], kind='merge')
#        positions = positions[argsort_y]
#        argsort_x = np.argsort(positions[:, 0], kind='merge')
#        positions = positions[argsort_x]
#
#        spos = np.array(spos)
#        spos = spos[argsort_z]
#        spos = spos[argsort_y]
#        spos = spos[argsort_x]
#
#        atoms = Atoms(cell=self.prim.cell,
#                      scaled_positions=spos,
#                      pbc=False)
#
#        new_order = np.arange(len(atoms), dtype=int)
#        new_order = new_order[argsort_z]
#        new_order = new_order[argsort_y]
#        new_order = new_order[argsort_x]
#
#        distance_to_center_atoms = np.zeros((len(self.prim), len(atoms)))
#        for i in range(len(self.prim)):
#            j = new_order.tolist().index(i)
#            distance_to_center_atoms[i, :] = atoms.get_distances(j, [...])
#        distance_to_center_atoms = np.min(distance_to_center_atoms, axis=0)
#        argsort_d = np.argsort(distance_to_center_atoms, kind='merge')
#
#        new_order = new_order[argsort_d]
#
#        new_atom_list = AtomList()
#        for i in new_order:
#            new_atom_list.append(self._atom_list[i])
#        self._atom_list = new_atom_list
#
#        spos = [atom_to_spos(a, self.prim.basis) for a in self._atom_list]
#
#        # Make an atoms obect out of the scaled positions
#        atoms = Atoms(cell=self.prim.cell,
#                      scaled_positions=spos,
#                      pbc=False)
#
#        # TODO: Assert sorting

        # Pass atoms and cutoffs to function which generates the clusters
        logger.info('Starting generating clusters')
        self._cluster_list = get_clusters(atoms, self.cutoffs, len(self.prim))
        logger.info('Finished generating clusters')

#        new_cluster_list = []
#        for c in self._cluster_list:
#            new_cluster_list.append(tuple(c))
#        new_cluster_list.sort(
#                key=lambda c: get_maximum_distance(atoms.positions[c, :]))
#        new_cluster_list.sort(key=lambda c: len(c))
#
#        self._cluster_list = ClusterList()
#        for c in new_cluster_list:
#            self._cluster_list.append(c)

        # TODO: This functionality could be implemented in the cluster list
        count = Counter([len(c) for c in self._cluster_list])
        logger.info('Found {} clusters'.format(dict(count)))

        logger.info('Starting categorizing clusters')
        # I.e. categorize the clusters
        self._orbits = get_orbits(self._cluster_list,
                                  self._atom_list,
                                  self.rotation_matrices,
                                  self.translation_vectors,
                                  self.permutations,
                                  self.prim)
        # The count is used later too
        logger.info('Finished categorizing clusters')
        count = Counter([orbit.order for orbit in self.orbits])
        logger.info('Found {} orbits'.format(dict(count)))

        logger.info('Starting finding eigentensors')
        # Some orbits may not be allowed due to symmetry. However we still want
        # to keep them for the sake for completeness
        orbits_to_drop = []
        # TODO: Refactor
        # For each order...
        for order in self.cutoffs.orders:
            logger.info('Order {}:'.format(order))
            # Init the progress bar
            bar = Progress(count[order])
            # ... loop over all orbits
            for orbit_index, orbit in enumerate(self.orbits):
                # skip the orbits not in the present order
                # (They should be in order) TODO: Assert this perhaps?
                if orbit.order != order:
                    continue
                # Now assemble the lists with rotation matrices and
                # permutations vectors
                R_list = []
                p_list = []
                for eigensymmetry in orbit.eigensymmetries:
                    scaled_R = self.rotation_matrices[eigensymmetry[0]]
                    R = rotation_to_cart_coord(scaled_R, self.prim.cell)
                    R_list.append(R)
                    p_list.append(self._permutations[eigensymmetry[1]])
                cluster = self._cluster_list[orbit.prototype_index]
                # Send in the eigensymmetries for the cluster and get the
                # eigentensors
                ets = symmetrize_tensor(R_list, p_list, cluster)
                orbit.eigentensors = ets
                # If the returned eigentensor list is empty, add the orbit to
                # the drop list
                if not ets:
                    orbits_to_drop.append(orbit_index)
                # Update the progress bar
                bar.tick()
            # Close the progress bar (and print time)
            bar.close()
        # Temporary list of orbits to store the ones not to drop
        reduced_orbits = []
        self._dropped_orbits = []  # This list will keep the dropped orbits
        # TODO: refactor
        # Loop over the orbits and notify the user if it will be dropped
        for i in range(len(self.orbits)):
            if i in orbits_to_drop:
                cluster = self._cluster_list[self.orbits[i].prototype_index]
                logger.info('  Dropping orbit {}: {}'.format(i, cluster))
                # Either it is archived
                self._dropped_orbits.append(self.orbits[i])
            else:
                # or kept
                reduced_orbits.append(self.orbits[i])
        # TODO: refactor and log
        # Check if the eigentensors became integer tensors. Assume yes
        integer_ets = True
        for orbit in self.orbits:
            for et in orbit.eigentensors:
                # Check that the et is close to it's rounded value
                if not np.allclose(et, et.round(0)):
                    # If not set flag to False
                    integer_ets = False
                    # TODO: break in a nice way
        # If the eigentensors are integer we make them explicit integer
        # ndarrays
        if integer_ets:
            for orb in self.orbits:
                for i, et in enumerate(orb.eigentensors):
                    orb.eigentensors[i] = np.int64(et.round(0))

        self._orbits = reduced_orbits
        logger.info('Finished finding eigentensors')
        if orbits_to_drop:
            logger.info('Found {} orbits after drop'.format(len(self.orbits)))

        n_ets = dict()
        for order in self.cutoffs.orders:
            n_ets[order] = sum(len(orb.eigentensors) for orb in self.orbits
                               if orb.order == order)
        logger.info('Found {} eigentensors'.format(n_ets))

        # If the sum rules should be enforced calculate the constraint matrices
        # and find their null space to give the constraint vectors
        if self.sum_rules:
            logger.info('Starting constructing constraint matrices')
            M = self.get_sum_rule_constraint_matrices()
            self._constraint_matrices = M
            logger.info('Finished constructing constraint matrices')

            logger.info('Starting constructing constraint vectors')
            cvs = self._get_constraint_vectors(M)
            self._constraint_vectors = cvs

            # Normalize cv by L1 in place
            for cv in cvs.values():
                for i, row in enumerate(cv):
                    cv[i, :] /= sum(abs(row))

            logger.info('Finished constructing constraint vectors')
        # Here is the rescaling.
        # TODO: refactor
        ets_is_integer = True
        for orbit in self.orbits:
            for et in orbit.eigentensors:
                if et.dtype == np.float64:
                    ets_is_integer = False
                    break
            else:
                continue
            break
        if ets_is_integer:
            for orbit in self.orbits:
                rescale = self.length_scale**(orbit.order - 1)
                for et in orbit.eigentensors:
                    assert np.allclose(et, et.round())
                    assert et.dtype == np.int64
                    et *= max(round(1/rescale), 1)
                if self.sum_rules:
                    for of in orbit.orientation_families:
                        for et in of.eigentensors:
                            assert np.allclose(et, et.round())
                            assert et.dtype == np.int64
                            et *= max(round(1/rescale), 1)
        else:
            for orbit in self.orbits:
                rescale = self.length_scale**(orbit.order - 1)
                for et in orbit.eigentensors:
                    et = et.astype(np.float64)
                    et /= rescale
                if self.sum_rules:
                    for of in orbit.orientation_families:
                        for et in of.eigentensors:
                            et = et.astype(np.float64)
                            et /= rescale

        n_dofs = {order: self._get_number_of_dofs(order) for order in
                  self.cutoffs.orders}
        logger.info('Number of degrees of freedom: {}'.format(n_dofs))

    # TODO: refactor
    # TODO: fix how we want to use the config
    # TODO: fix translational, rotational etc
    # TODO: Make internal
    def get_sum_rule_constraint_matrices(self, symbolic=True,
                                         rotational=False):
        """Returns the constraint matrices needed for imposing the
        (acoustic=translational) sum rule.

        Returns
        -------
        dict
            dictionary of constraint matrices, where the key is the order of
            the respective constraint matrix
        """

        compress_mode = core_config.sum_rule_constraint_mode
        simplify = core_config.sum_rule_constraint_simplify
        tol = core_config.integer_tolerance

        if compress_mode == 'symbolic':
            logger.debug('Using symbolic mode for sum rules')
            import sympy

        # First we need the rotations in cartesian coordinates
        R_cart = []
        for R in self.rotation_matrices:
            R_rot = rotation_to_cart_coord(R, self.prim.cell)
            assert np.allclose(np.dot(R_rot, R_rot.T), np.eye(3)), R_rot
            R_cart.append(R_rot)
        integer_rotations = True
        max_diff = 0
        for R in R_cart:
            max_diff = max(np.max(np.abs(R - R.round(0))), max_diff)
        integer_rotations = True if max_diff < tol else False
        if integer_rotations:
            logger.debug('Rotations close to int, changing type to int64')
            for i in range(len(R_cart)):
                R_cart[i] = np.int64(R_cart[i].round(0))

        # Create a lookup dict to store the eigentensors for each cluster
        lookup = {}
        integer_ets = True
        for orbit_index, orbit in enumerate(self.orbits):
            for of in orbit.orientation_families:
                R = R_cart[of.symmetry_index]
                of.eigentensors = []
                # Transform the eigentensors to cart. coord.
                for et in orbit.eigentensors:
                    rotated_et = et.copy()
                    if not np.allclose(rotated_et, rotated_et.round(0)):
                        integer_ets = False
                    rotated_et = rotate_tensor(rotated_et, R.T)
#                    for i in range(orbit.order):
#                        rotated_et = np.tensordot(rotated_et, R.T,
#                                                  axes=((0,), (0,)))

                    of.eigentensors.append(rotated_et)
                # Loop over all the cluster, permute the indices of the
                # ofs eigentensor and store the result in the lookup
                for cluster_index, perm_index in zip(of.cluster_indices,
                                                     of.permutation_indices):
                    cluster = self._cluster_list[cluster_index]
                    perm = self._permutations[perm_index]
                    lookup[tuple(cluster)] = [et.transpose(perm) for et in
                                              of.eigentensors], orbit_index

        # Make sure the orbits are sorted by order
        previous_order = 2
        for orbit in self.orbits:
            assert orbit.order >= previous_order
            previous_order = orbit.order

        # This is not the parameters but a mapping from order/index
        params = {}
        for orbit_index, orbit in enumerate(self.orbits):
            order = orbit.order
            if order not in params:
                params[order] = {}
                nParams = 0
            nParams_in_orbit = len(orbit.eigentensors)
            params[order][orbit_index] = \
                list(range(nParams, nParams + nParams_in_orbit))
            nParams += nParams_in_orbit
        M = {}

        if integer_rotations and integer_ets:
            dtype = np.int64
        else:
            dtype = np.float64
        if simplify:
            from .core.eigentensor_symmetrizer import _nsimplify

        # This is better described in the documentation
        for order in params.keys():
            nParams = max(params[order][max(params[order])]) + 1
            if compress_mode == 'symbolic':
                M[order] = sympy.SparseMatrix(nParams, nParams, 0)
            else:
                M[order] = np.zeros((nParams, nParams), dtype=dtype)
            logger.info('Order {}: '.format(order))
            prefix_list = []
            if order == 2:
                for i in np.unique(self.wyckoff_sites):
                    prefix_list.append([i])
            else:
                for orbit in self.orbits:
                    if orbit.order != order - 1:
                        continue
                    if (orbit.maximum_distance >
                            np.max(self.cutoffs._cutoff_matrix[:, order - 2])):
                        continue
                    prefix = list(self.cluster_list[orbit.prototype_index])
                    prefix_list.append(prefix)
                for orbit in self._dropped_orbits:
                    if orbit.order != order - 1:
                        continue
                    if (orbit.maximum_distance >
                            np.max(self.cutoffs._cutoff_matrix[:, order - 2])):
                        continue
                    prefix = list(self.cluster_list[orbit.prototype_index])
                    prefix_list.append(prefix)
            bar = Progress(len(prefix_list))
            for prefix in prefix_list:
                bar.tick()
                M_aco = np.zeros((3**order, nParams), dtype=dtype)
                cluster = list(prefix) + [None]
                for i in range(len(self._atom_list)):
                    cluster[-1] = i
                    try:
                        ets, orbit_index = lookup[tuple(sorted(cluster))]
                    except KeyError:
                        continue
                    inv_argsort = np.argsort(np.argsort(cluster))
                    ets = [et.transpose(inv_argsort) for et in ets]
                    for et, col in zip(ets, params[order][orbit_index]):
                        M_aco[:, col] += et.flatten()
                M_aco[np.abs(M_aco) < tol] = 0
                if dtype is np.int64:
                    assert np.allclose(M_aco, M_aco.round(0))
                if compress_mode == 'symbolic':
                    if simplify:
                        M_aco = _nsimplify(M_aco)
                    M_aco = sympy.SparseMatrix(M_aco)
                    M[order] = sympy.SparseMatrix.vstack(M[order], M_aco)
                    M[order] = sympy.SparseMatrix.rref(M[order])[0]
                else:
                    M[order] = np.vstack((M[order], M_aco))
                    M[order] = lu(M[order])[2]
            bar.close()
        if compress_mode == 'symbolic':
            M_dict = {}
            for order in sorted(M):
                M_tmp = np.zeros(M[order].shape)
                for i in range(M[order].shape[0]):
                    for j in range(M[order].shape[1]):
                        M_tmp[i, j] = np.float64(M[order][i, j])
                M_dict[order] = M_tmp
            M = M_dict
        return M

    # TODO: This can be refactored to a new module since it is general
    def _get_constraint_vectors(self, constraint_matrices, tol=1e-11):
        """ Constructs the map from irreducible parameters to the real
        parameters.
        """
        simplify_before_compress = \
            core_config.constraint_vectors_simplify_before_compress
        compress_mode = core_config.constraint_vectors_compress_mode
        simplify_before_solve = \
            core_config.constraint_vectors_simplify_before_solve
        solve_mode = core_config.constraint_vectors_solve_mode
        cvs = {}
        for order, M in constraint_matrices.items():
            bar = Progress(tot=None, estimate_remaining=False)
            logger.info('Order {}:'.format(order))
            cvs[order] = []
            dim = M.shape[1]
            M[np.abs(M) < tol] = 0
            if simplify_before_compress:
                from .core.eigentensor_symmetrizer import _nsimplify
                M = _nsimplify(M)
            if compress_mode == 'symbolic':
                M = sympy.SparseMatrix(M)
                M = sympy.SparseMatrix.rref(M)[0]
            elif compress_mode == 'numeric':
                M = lu(M)[2]
            if simplify_before_solve:
                from .core.eigentensor_symmetrizer import _nsimplify
                M = _nsimplify(M)
            if solve_mode == 'symbolic':
                M = sympy.SparseMatrix(M)
                nullspace = M.nullspace()
                eig_vecs = []
                for col in nullspace:
                    tmp = np.zeros(dim)
                    for i, num in enumerate(col):
                        tmp[i] = np.float64(num)
                    eig_vecs.append(tmp)
                eig_vals = np.zeros(len(eig_vecs))
            elif solve_mode == 'numeric':
                _, eig_vals, eig_vecs = np.linalg.svd(M)
            for i, (eig_val, eig_vec) in enumerate(zip(eig_vals, eig_vecs)):
                if abs(eig_val) < tol:
                    cvs[order].append(eig_vec)
            cvs[order] = np.array(cvs[order])
            for i, j in itertools.combinations(range(len(cvs[order])), 2):
                norm = np.linalg.norm(cvs[order][i] - cvs[order][j])
                txt = 'Diff norm of cv {} and cv {} of order {} is {}'\
                      .format(i, j, order, norm)
                assert norm > tol, txt
                dot = np.dot(cvs[order][i], cvs[order][j])
                norm_i = np.linalg.norm(cvs[order][i])
                norm_j = np.linalg.norm(cvs[order][j])
                txt = 'cv {} and cv {} is not orthogonal, dot={}'\
                      .format(i, j, dot)
                assert abs(dot/(norm_i * norm_j)) < 1 - tol, txt
            bar.close()
        return cvs

    def _map_parameters(self, parameters):
        """ Maps irreducible parameters to the real parameters associated with
        the eigentensors.
        """
        txt = ('Please provide {} parameters'
               .format(self.number_of_dofs))
        assert len(parameters) == self.number_of_dofs, txt
        if self.sum_rules:
            parameters_tmp = []
            n = 0
            for order in sorted(self._constraint_vectors):
                cv = self._constraint_vectors[order]
                params = parameters[n:n + cv.shape[0]]
                n += cv.shape[0]
                parameters_tmp.extend(np.dot(params, cv))
            parameters = parameters_tmp
        return parameters.copy()

    def copy(self):
        return deepcopy(self)

    def write(self, fileobj):
        """ Saves to file or to a file-like object.

        The instance is saved into a custom format based on tar-files. The
        resulting file will be a valid tar file and can be browsed by by a tar
        reader. The included objects are themself either pickles, npz or other
        tars.

        Parameters
        ----------
        fileobj : str or file-like object
            If the input is a string a tar archive will be created in the
            current directory. Otherwise the input must be a valid file
            like object.
        """
        # Create a tar archive
        if isinstance(fileobj, str):
            tar_file = tarfile.open(name=fileobj, mode='w')
        else:
            tar_file = tarfile.open(fileobj=fileobj, mode='w')

        # Attributes in pickle format
        pickle_attributes = ['_symprec', '_length_scale', '_sum_rules',
                             '_symmetry_dataset', '_permutations',
                             '_atom_list', '_cluster_list']
        items_pickle = dict()
        for attribute in pickle_attributes:
            items_pickle[attribute] = self.__getattribute__(attribute)
        add_items_to_tarfile_pickle(tar_file, items_pickle, 'attributes')

        # Constraint matrices and vectors in hdf5 format
        if self.sum_rules:
            items = {str(k): v for k, v in self._constraint_matrices.items()}
            add_items_to_tarfile_hdf5(tar_file, items, 'constraint_matrices')
            items = {str(k): v for k, v in self._constraint_vectors.items()}
            add_items_to_tarfile_hdf5(tar_file, items, 'constraint_vectors')

        # Cutoffs and prim with their builtin write/read functions
        items_custom = {'_cutoffs': self._cutoffs, '_prim': self._prim}
        add_items_to_tarfile_custom(tar_file, items_custom)

        # Orbits
        add_list_to_tarfile_custom(tar_file, self._orbits, 'orbits')
        add_list_to_tarfile_custom(tar_file, self._dropped_orbits,
                                   'dropped_orbits')

        # Done!
        tar_file.close()

    def read(f):
        """ Reads a ClusterSpace instance from file.

        Parameters
        ----------
        f : string or file object
            name of input file (string) or stream to load from (file object)
        """

        # Instantiate empty cs obj.
        cs = ClusterSpace.__new__(ClusterSpace)

        # Load from file on disk or file-like
        if type(f) is str:
            tar_file = tarfile.open(mode='r', name=f)
        else:
            tar_file = tarfile.open(mode='r', fileobj=f)

        # Attributes
        attributes = read_items_pickle(tar_file, 'attributes')
        for name, value in attributes.items():
            cs.__setattr__(name, value)

        # Load the constraint matrices into their dict
        if cs.sum_rules:
            items = read_items_hdf5(tar_file, 'constraint_matrices')
            cs._constraint_matrices = {int(k): v for k, v in items.items()}
            items = read_items_hdf5(tar_file, 'constraint_vectors')
            cs._constraint_vectors = {int(k): v for k, v in items.items()}

        # Cutoffs and prim via custom save funcs
        fileobj = tar_file.extractfile('_cutoffs')
        cs._cutoffs = Cutoffs.read(fileobj)

        fileobj = tar_file.extractfile('_prim')
        cs._prim = Atoms.read(fileobj)

        # Orbits are stored in a separate archive
        cs._orbits = read_list_custom(tar_file, 'orbits', Orbit.read)
        cs._dropped_orbits = read_list_custom(
            tar_file, 'dropped_orbits', Orbit.read)

        return cs
