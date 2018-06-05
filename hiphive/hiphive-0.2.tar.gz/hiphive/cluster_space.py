"""
Contains the ClusterSpace object central to hiPhive
"""

import numpy as np
import tarfile

from ase.data import chemical_symbols
from collections import OrderedDict
from copy import deepcopy

from .core.cluster_space_builder import build_cluster_space
from .core.atoms import Atoms
from .core.orbit import Orbit
from .io.logging import logger
from .io.read_write_files import (add_items_to_tarfile_pickle,
                                  add_items_to_tarfile_custom,
                                  add_list_to_tarfile_custom,
                                  read_items_pickle,
                                  read_list_custom)
from .cluster_filter import Cutoffs, CutoffMaximumBody

logger = logger.getChild('ClusterSpace')


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

        self._atom_list = None
        self._cluster_list = None
        self._symmetry_dataset = None
        self._permutations = None
        self._prim = None
        self._orbits = None

        self._constraint_vectors = None
        # TODO: How to handle the constraint matrices? Should they even be
        # stored?
        self._constraint_matrices = None
        # Is this the best way or should the prim be instantiated separately?

        build_cluster_space(self, prototype_structure)

    # TODO: Should everything here be properties? deepcopy/ref etc.?
    # TODO: Docstrings for properties
    @property
    def number_of_dofs(self):
        """int : number of free parameters in the model

        If the sum rules are not enforced the number of DOFs is the same as
        the total number of eigentensors in all orbits.
        """
        return self._get_number_of_dofs()

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
    def primitive_structure(self):
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
                types.append(self.primitive_structure.numbers[atom.site])
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

    def _get_number_of_dofs(self):
        """ Returns the number of degrees of freedom. """
        return self._cvs.shape[1]

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

        # basic information
        prototype = orders[list(orders.keys())[-1]]
        n = max(len(str_order(prototype)), 54)
        s = []
        s.append(' Cluster Space '.center(n, '='))
        data = [('Spacegroup',               self.spacegroup),
                ('symprec',                  self.symprec),
                ('Sum rules',                self.sum_rules),
                ('Length scale',             self.length_scale),
                ('Cutoffs',                  self.cutoffs),
                ('Cell',                     self.primitive_structure.cell),
                ('Basis',                    self.primitive_structure.basis),
                ('Numbers',                  self.primitive_structure.numbers),
                ('Total number of orbits',   len(orbits)),
                ('Total number of clusters',
                 sum([order['num_clusters'] for order in orders.values()])),
                ('Total number of parameters',
                 self._get_number_of_dofs()
                 )]
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
        return s.format(self.primitive_structure, self.cutoffs, self.sum_rules,
                        self.symprec, self.length_scale)

    def _map_parameters(self, parameters):
        """ Maps irreducible parameters to the real parameters associated with
        the eigentensors.
        """
        txt = ('Please provide {} parameters'
               .format(self.number_of_dofs))
        assert len(parameters) == self.number_of_dofs, txt
        return self._cvs.dot(parameters)

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
        items = dict(cvs=self._cvs)
        add_items_to_tarfile_pickle(tar_file, items, 'constraint_vectors')

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
        items = read_items_pickle(tar_file, 'constraint_vectors')
        cs._cvs = items['cvs']

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
