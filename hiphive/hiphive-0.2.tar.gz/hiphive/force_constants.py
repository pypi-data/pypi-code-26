"""
This module provides functionality for storing and handling of force constants
"""
import tarfile
import numpy as np

from ase import units
from itertools import permutations, product
from scipy.linalg import eig
from string import ascii_lowercase, ascii_uppercase

from .io.read_write_files import add_items_to_tarfile_pickle, read_items_pickle


class ForceConstants:
    """Container class for force constants.

    Either specify `fc_dict` or both `cluster_groups` and `fc_list`.

    Parameters
    ----------
    fc_dict : dict
        dict which holds all force constants with clusters as keys and the
        respective force constant as value
    cluster_groups : list
        list of groups of clusters, clusters in the same group should have
        identical force constants.
    fc_list : list
        list of force constants, one force constant for each cluster group
    atoms: ASE Atoms object
        supercell corresponding to the fcs

    Attributes
    ----------
    _fc_dict : dict
        dictionary that holds all force constants with clusters as keys and the
        respective force constant as value
    """

    def __init__(self, fc_dict=None, cluster_groups=None, fc_list=None,
                 atoms=None):

        # setup fc_dict
        if fc_dict is None:
            self._setup_fc_dict(cluster_groups, fc_list)
            self._sparse = True
            self._cluster_groups = cluster_groups
            self._fc_list = fc_list
        else:
            self._fc_dict = fc_dict
            self._sparse = False

        # find which orders are in the fc_dict
        orders = np.unique([len(c) for c in self._fc_dict.keys()])
        self._orders = orders.tolist()

        # setup atoms and allowed_atoms
        self._setup_atoms(atoms)

    def _setup_fc_dict(self, cluster_groups, fc_list):
        """ Setup fc_dict from cluster_groups and fc_list """
        if cluster_groups is None or fc_list is None:
            raise ValueError('Invalid input')
        assert len(cluster_groups) == len(fc_list)

        fc_dict = {}
        for clusters, fc in zip(cluster_groups, fc_list):
            for cluster in clusters:
                permutation = np.argsort(cluster)
                cluster = tuple(sorted(cluster))
                assert cluster not in fc_dict.keys(), 'Duplicate cluster'
                fc_dict[cluster] = fc.transpose(permutation)

        self._fc_dict = fc_dict

    def _setup_atoms(self, atoms):
        """ Setup atoms and sanity check its properties with fc_dict """
        cluster_indices = [ind for c in self._fc_dict.keys() for ind in c]
        natoms = np.max(cluster_indices) + 1
        if atoms is None:
            self._atoms = None
        else:
            self._atoms = atoms.copy()
            assert natoms == len(self.atoms), \
                'Atoms and ForceConstants have different number of atoms'

        self._allowed_atoms = set(range(natoms))
        assert len(self._allowed_atoms - set(cluster_indices)) == 0, \
            'Not all atoms are part of a force constant'

    def get_fc_array(self, order):
        """ Return force constants in array format for specified order.

        Parameters
        ----------
        order : int
            force constants for this order will be returned

        Returns
        -------
        NumPy array
            NumPy array with shape `(N,)*order + (3,)*order` where `N` is
            the number of atoms
        """
        if order not in self.orders:
            raise ValueError('Order not in orders')

        fc_array = np.zeros((self.natoms,)*order + (3,)*order)
        for c, fc in self.get_fc_dict(order=order, permutations=True).items():
            fc_array[c] = fc
        return fc_array

    def get_fc_dict(self, order=None, permutations=False):
        """ Return force constant dictionary for one specific order.

        Parameters
        ----------
        order : int
            fcs returned for this order
        permutations : bool
            if True returns all permutations of cluster, else only force
            constants for sorted cluster

        Returns
        -------
        dict
            dictionary with keys corresponding to clusters and values to the
            respective force constant
         """

        # Return all fcs
        if order is None:
            if not permutations:
                return self._fc_dict
            else:
                fc_dict = {}
                for c, fc in self._fc_dict.items():
                    for c_perm, fc_perm in get_permuted_fcs(c, fc).items():
                        fc_dict[c_perm] = fc_perm
                return fc_dict

        if order not in self.orders:
            raise ValueError('Order not in orders')

        # Return fcs for specific order
        fc_order = {}
        for c, fc in self._fc_dict.items():
            if len(c) == order:
                if permutations:
                    for c_perm, fc_perm in get_permuted_fcs(c, fc).items():
                        fc_order[c_perm] = fc_perm
                else:
                    fc_order[c] = fc
        return fc_order

    def __getitem__(self, cluster):
        if isinstance(cluster, (tuple, list)):
            if len(cluster) not in self.orders:
                raise ValueError('Cluster order not in orders')
            if len(self._allowed_atoms.intersection(set(cluster))) != \
                    len(set(cluster)):
                raise ValueError('Cluster outside range of atomic indices')

            try:
                sorted_cluster = tuple(sorted(cluster))
                if cluster == sorted_cluster:
                    return self._fc_dict[cluster]
                inv_perm = np.argsort(np.argsort(cluster))
                return self._fc_dict[sorted_cluster].transpose(inv_perm)
            except KeyError:
                return np.zeros((3,)*len(cluster))
        else:
            raise ValueError('Cluster must be tuple or list')

    def assert_acoustic_sum_rules(self, order=None, tol=1e-6):
        """ Asserts that acoustic sum rules are enforced for fcs

        Parameters
        ----------
        order : int, Optional
            specifies which order to check, if None all are checked
        tol : float
            numeric tolerance for checking sum rules.

        Asserts
        -------
        This will yield assert error if sum rules are not enforced.
        """

        # setup orders
        if order is None:
            orders = self.orders
        else:
            if order not in self.orders:
                raise ValueError('Order not available in FCS')
            orders = [order]

        atomic_indices = range(self.natoms)
        for order in orders:
            assert_msg = 'Acoustic sum rule order {} not enforced for atom' + \
                ' {}'*(order-1) + ' x'
            for ijk in product(atomic_indices, repeat=order-1):
                fc_sum_ijk = np.zeros((3, )*order)
                for l in atomic_indices:
                    cluster = ijk + (l, )
                    fc_sum_ijk += self[cluster]
                assert np.linalg.norm(fc_sum_ijk) < tol, \
                    assert_msg.format(order, *ijk)

    def __len__(self):
        return len(self._fc_dict)

    @property
    def atoms(self):
        """ ASE Atoms object: supercell corresponding to force constants """
        return self._atoms

    @property
    def natoms(self):
        """ int : Number of atoms (maximum index in a cluster +1) """
        return len(self._allowed_atoms)

    @property
    def orders(self):
        """ list : List of the orders for which force constants exists """
        return self._orders

    @property
    def sparse(self):
        """ bool : If True the object was initialized with sparse data """
        return self._sparse

    @property
    def clusters(self):
        return sorted(self._fc_dict.keys(), key=lambda c: (len(c), c))

    def write(self, f):
        """Write a ForceConstants instance to a file.

        Parameters
        ----------
        f : str or file object
            name of input file (str) or stream to write to (file object)
        """
        if isinstance(f, str):
            tar_file = tarfile.open(mode='w', name=f)
        else:
            tar_file = tarfile.open(mode='w', fileobj=f)

        # add the needed info to recreate the fcs object
        if self.sparse:
            items = dict(cluster_groups=self._cluster_groups,
                         fc_list=self._fc_list, atoms=self.atoms)
            add_items_to_tarfile_pickle(tar_file, items, 'repr')
        else:
            items = dict(fc_dict=self._fc_dict, atoms=self.atoms)
            add_items_to_tarfile_pickle(tar_file, items, 'repr')

        tar_file.close()

    @staticmethod
    def read(f):
        """Load a ForceConstants instance from file

        Parameters
        ----------
        f : string or file object
            name of input file (string) or stream to load from (file object)
        """
        if isinstance(f, str):
            tar_file = tarfile.open(mode='r', name=f)
        else:
            tar_file = tarfile.open(mode='r', fileobj=f)

        items = read_items_pickle(tar_file, 'repr')
        return ForceConstants(**items)

    def print_cluster(self, cluster: tuple):
        """
        Prints ForceConstants[cluster] in a nice format.

        Parameters
        ----------
        cluster : tuple
            tuple of ints indicating the sites belonging to the cluster
        """
        print(self._repr_fc(cluster))

    def __str__(self):
        s = []
        s.append(' ForceConstants '.center(54, '='))
        s.append('Orders: {}'.format(self.orders))
        s.append('Atoms: {}'.format(self.atoms))
        s.append('')
        if len(self) > 10:
            for c in self.clusters[:3]:
                s.append(self._repr_fc(c)+'\n')
            s.append('...')
            for c in self.clusters[-3:]:
                s.append(self._repr_fc(c)+'\n')
        else:
            for c in self.clusters:
                s.append(self._repr_fc(c)+'\n')
        return '\n'.join(s)

    def __repr__(self):
        fc_dict_str = '{{{}: {}, ..., {}: {}}}'.format(
            self.clusters[0], self[self.clusters[0]].round(5),
            self.clusters[-1], self[self.clusters[-1]].round(5))
        return 'ForceConstants(fc_dict={}, atoms={!r})'.format(
            fc_dict_str, self.atoms)

    def _repr_fc(self, cluster: tuple, precision=5, suppress=True) -> str:
        """
        Representation for single cluster and its force constant.

        Parameters
        ----------
        cluster : tuple
            tuple of ints indicating the sites belonging to the cluster
        """
        s = []
        s.append('Cluster: {}'.format(cluster))
        for atom_index in cluster:
            s.append(str(self.atoms[atom_index]))
        s.append('force constant:')
        s.append(np.array_str(self[cluster], precision=precision,
                 suppress_small=suppress))
        return '\n'.join(s)


def get_permuted_fcs(cluster, fc):
    """Generate all permutations of cluster and their force constant given a
    single cluster and its force constant.

    Parameters
    ----------
    cluster : tuple
        tuple of ints indicating the sites belonging to the cluster
    fc : NumPy array
        force constant for cluster

    Returns
    -------
    dict
        dict with keys corresponding to clusters and values to their force
        constant
    """
    fc_dict = {}
    fc = fc.transpose(np.argsort(cluster))
    for perm_cluster in set(permutations(cluster)):
        inv_perm = np.argsort(np.argsort(perm_cluster))
        fc_perm = fc.transpose(inv_perm)
        fc_dict[perm_cluster] = fc_perm
    return fc_dict


def fc_array_to_dict(fc_array, cut_tol=1e-8):
    """Convert a force constant from array to dictionary format.

    Parameters
    ----------
    fc_array : array
        force constant array for one order
    cut_tol : float
        tolerance for which force constants to keep in dict

    Returns
    -------
    dict
        sparse dictionary with keys corresponding to clusters and values to the
        respective force constant
    """

    fc_dict = {}
    Natoms = fc_array.shape[0]
    order = len(fc_array.shape) // 2
    assert fc_array.shape == (Natoms,)*order + (3,)*order

    for cluster in product(*[range(Natoms)]*order):
        if np.linalg.norm(fc_array[cluster]) > cut_tol:
            if cluster == tuple(sorted(cluster)):
                fc_dict[cluster] = fc_array[cluster]
    return fc_dict


def compute_gamma_frequencies(fc2, masses):
    """ Computes gamma frequencies using second order force constants

    Assumes fc2 is in eV/A2

    Parameters
    ----------
    fc2 : ForceConstants object, NumPy array
        Second order force constants
    masses : list
        list of masses for each atom

    Returns
    -------
    gamma_frequencies : NumPy array
        array of gamma frequencies in THz
    """

    # get fc2_array
    if isinstance(fc2, ForceConstants):
        fc2 = fc2.get_fc_array(order=2)

    N = fc2.shape[0]
    assert len(masses) == N, 'masses not compatible with fc2'
    mass_matrix = np.sqrt(np.outer(masses, masses))

    # divide with mass matrix
    fc2_tmp = np.zeros((N, N, 3, 3))
    for pair in product(range(N), repeat=2):
        fc2_tmp[pair] = fc2[pair] / mass_matrix[pair]

    # reshape into matrix and solve eigenvalues
    fc2_tmp = fc2_tmp.transpose([0, 2, 1, 3]).reshape(N * 3, N * 3)
    eigen_vals, _ = eig(fc2_tmp)
    eigen_vals *= 1e20 / units.J * units.kg  # [1/s**2]
    eigen_vals.sort()

    # if negative eigenval, set frequency to negative
    gamma_frequencies = []
    for val in eigen_vals.real:
        if val >= 0:
            gamma_frequencies.append(np.sqrt(val))
        else:
            gamma_frequencies.append(-np.sqrt(np.abs(val)))

    # Sort and convert to THz
    gamma_frequencies = np.array(gamma_frequencies) / 1e12 / (2 * np.pi)
    gamma_frequencies.sort()
    return gamma_frequencies


def symbolize_force_constant(fc, tol=1e-10):
    """Carry out a symbolic symmetrization of a force constant tensor.

    Parameters
    ----------
    fc : NumPy array
        force constant tensor
    tol : float
        tolerance used to decide whether two elements are identical

    Returns
    -------
    NumPy array
        symbolic representation of force constant matrix
    """

    fc_int = np.round(fc / tol).astype(int)

    fc_chars = np.empty(fc_int.shape, dtype=object).flatten()
    all_chars = ascii_lowercase + ascii_uppercase
    lookup_chars = {}
    for i, val in enumerate(fc_int.flatten()):
        if val == 0:
            fc_chars[i] = 0
        elif val in lookup_chars.keys():
            fc_chars[i] = lookup_chars[val]
        elif -val in lookup_chars.keys():
            fc_chars[i] = '-{:}'.format(lookup_chars[-val])
        else:
            lookup_chars[val] = all_chars[len(lookup_chars.keys())]
            fc_chars[i] = lookup_chars[val]
    return fc_chars.reshape(fc_int.shape)
