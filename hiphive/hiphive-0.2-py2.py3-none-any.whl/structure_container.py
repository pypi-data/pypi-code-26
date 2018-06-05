"""
This module provides functionality for storing structures and their fit
matrices together with target forces and displacements
"""

import tarfile
import numpy as np
from collections import OrderedDict
from ase.calculators.singlepoint import SinglePointCalculator

from .io.read_write_files import (add_items_to_tarfile_hdf5,
                                  add_items_to_tarfile_pickle,
                                  add_items_to_tarfile_custom,
                                  add_list_to_tarfile_custom,
                                  read_items_hdf5,
                                  read_items_pickle,
                                  read_list_custom)

from .cluster_space import ClusterSpace
from .force_constant_model import ForceConstantModel
from .io.logging import logger
logger = logger.getChild('structure_container')


class StructureContainer:
    """
    This class serves as a container for structures as well as associated
    fit properties and fit matrices.

    Parameters
    -----------
    cs : ClusterSpace object
        cluster space that is the basis for the container
    fit_structure_list : list of FitStructure objects (optional)
         structures to be added to the container
    """

    def __init__(self, cs, fit_structure_list=None):
        """
        Attributes
        -----------
        _cs : ClusterSpace object
            ClusterSpace object which is the basis for the container
        _structure_list : list
            List of FitStructure objects
        _previous_fcm : ForceConstantModel object
            FCM object used for last fit matrix calculation
        _previous_atoms: ASE Atoms object
            atoms object used in last fit_matrix calculation; it is used to
            decided if the previous FCM can be used for a new structure or not,
            which often enables a considerable speed-up
        """
        self._cs = cs.copy()

        self._previous_fcm = None
        self._previous_atoms = None

        # Add atoms from atoms_list
        self._structure_list = []
        if fit_structure_list is not None:
            for fit_structure in fit_structure_list:
                if not isinstance(fit_structure, FitStructure):
                    raise TypeError('Can only add FitStructures')
                self._structure_list.append(fit_structure)

    def __len__(self):
        return len(self._structure_list)

    def __getitem__(self, ind):
            return self._structure_list[ind]

    @property
    def data_shape(self):
        """ tuple : tuple of integers representing the shape of the fit data
        matrix """
        n_cols = self._cs.number_of_dofs
        n_rows = sum(len(fs) * 3 for fs in self if fs.fit_ready)
        if n_rows == 0:
            return None
        return n_rows, n_cols

    @property
    def cluster_space(self):
        """ ClusterSpace object : copy of the cluster space the structure
        container is based on"""
        return self._cs.copy()

    def get_structure_indices(self, user_tag):
        """ Get structure indices via user tag.

        Parameters
        ----------
        user_tag : string
            user tag used for selecting structures

        Returns
        -------
        list
            list of structures with specified user tag
        """
        return [i for i, s in enumerate(self) if s.user_tag == user_tag]

    @staticmethod
    def read(fileobj, read_fit_matrices=True):
        """Restore a StructureContainer object from file.

        Parameters
        ----------
        f : string or file object
            name of input file (string) or stream to load from (file object)
        read_fit_matrices : bool
            Whether or not to load the fit matrices.
        """
        if isinstance(fileobj, str):
            tar_file = tarfile.open(mode='r', name=fileobj)
        else:
            tar_file = tarfile.open(mode='r', fileobj=fileobj)

        # Read clusterspace
        f = tar_file.extractfile('cluster_space')
        cs = ClusterSpace.read(f)

        # Read fitstructures
        fit_structure_list = read_list_custom(
            tar_file, 'fit_structure', FitStructure.read,
            read_fit_matrix=read_fit_matrices)

        return StructureContainer(cs, fit_structure_list)

    def write(self, f):
        """Write a StructureContainer instance to a file.

        Parameters
        ----------
        f : str or file object
            name of input file (str) or stream to write to (file object)
        """

        if isinstance(f, str):
            tar_file = tarfile.open(mode='w', name=f)
        else:
            tar_file = tarfile.open(mode='w', fileobj=f)

        # save cs
        custom_items = dict(cluster_space=self._cs)
        add_items_to_tarfile_custom(tar_file, custom_items)

        # save fit structures
        add_list_to_tarfile_custom(tar_file, self._structure_list,
                                   'fit_structure')

        tar_file.close()

    def add_structure(self, atoms, user_tag=None, compute_fit_matrix=True):
        """Add a structure to the container.

        Note that custom information about the atoms object may not be stored
        inside, for example a SinglePointCalculator will not be kept.

        Parameters
        ----------
        atoms : ASE Atoms object
            the structure to be added; the Atoms object must contain
            supplementary per-atom arrays with displacements and forces
        user_tag : string
            custom user tag to identify structure
        compute_fit_matrix : boolean
            if True the fit matrix of the structure is computed
        """

        atoms_copy = atoms.copy()

        # atoms object must contain displacements and forces
        if 'displacements' not in atoms_copy.arrays.keys():
            logger.warning('Skipping structure; no displacements found')
            return
        if 'forces' not in atoms_copy.arrays.keys():
            if isinstance(atoms.calc, SinglePointCalculator):
                atoms_copy.new_array('forces', atoms.get_forces())
            else:
                logger.warning('Skipping structure; no forces found')
                return

        # check if an identical atoms object already exists in the container
        for i, structure in enumerate(self._structure_list):
            if atoms_equals(atoms_copy, structure.atoms):
                logger.warning('Skipping structure; is equal to structure'
                               ' {}'.format(i))
                return

        logger.info('Adding structure')
        structure = FitStructure(atoms_copy, user_tag)
        if compute_fit_matrix:
            M = self._compute_fit_matrix(structure.atoms)
            structure.set_fit_matrix(M)
        self._structure_list.append(structure)

    def update_fit_data(self):
        """Compute the fit matrices for structures for which they are not yet
        available."""
        for structure in self._structure_list:
            if not structure.fit_ready:
                M = self._compute_fit_matrix(structure.atoms)
                structure.set_fit_matrix(M)

    def get_fit_data(self, structures=None):
        """Return fit data for structures. The fit matrices and target forces
        for the structures are stacked into NumPy arrays.

        Parameters
        ----------
        structures: list, tuple
            list of integers corresponding to structure indices. Defaults to
            None and in that case returns all fit data available.

        Returns
        -------
        NumPy array, NumPy array
            stacked fit matrices, stacked target forces for the structures
        """
        if structures is None:
            M_list = [s.fit_matrix
                      for s in self._structure_list if s.fit_ready]
            f_list = [s.forces.flatten()
                      for s in self._structure_list if s.fit_ready]
        else:
            M_list, f_list = [], []
            for i in structures:
                if not self._structure_list[i].fit_ready:
                    raise ValueError('Structure {} is not fit ready'.format(i))
                M_list.append(self._structure_list[i].fit_matrix)
                f_list.append(self._structure_list[i].forces.flatten())

        if len(M_list) == 0:
            logger.warning('No available fit data for {}'.format(structures))
            return None
        return np.vstack(M_list), np.hstack(f_list)

    def print_cluster_space(self, include_orbits=False):
        """Print information concerning the cluster space this structure
        container is based on.

        Parameters
        ----------
        include_orbits : boolean
            if True also print the list of orbits associated with the
            cluster space
        """
        print(self._cs)
        if include_orbits:
            self._cs.print_orbits()

    def __str__(self):
        if len(self._structure_list) > 0:
            return self._get_str_structure_list()
        else:
            return 'Empty StructureContainer'

    def __repr__(self):
        return 'StructureContainer({!r}, {!r})'.format(
            self._cs, self._structure_list)

    def _get_str_structure_list(self):
        """ Return formatted string of the structure list """
        def str_structure(index, structure):
            fields = OrderedDict([
                ('index',     '{:^4}'.format(index)),
                ('user-tag',  '{:^16}'.format(structure.user_tag)),
                ('num-atoms', '{:^5}'.format(len(structure))),
                ('fit-ready', '{:^5}'.format(str(structure.fit_ready))),
                ('avg-disp',  '{:7.4f}'.format(
                    np.mean(np.abs(structure.displacements)))),
                ('avg-force', '{:7.4f}'.format(
                    np.mean(np.abs(structure.forces))))])
            s = []
            for name, value in fields.items():
                n = max(len(name), len(value))
                if index < 0:
                    s += ['{s:^{n}}'.format(s=name, n=n)]
                else:
                    s += ['{s:^{n}}'.format(s=value, n=n)]
            return ' | '.join(s)

        # table width
        dummy = self._structure_list[0]
        n = len(str_structure(-1, dummy))

        # table header
        s = []
        s.append(' Structure Container '.center(n, '='))
        s += ['{:22} : {}'.format('Total number of structures', len(self))]
        s.append(''.center(n, '-'))
        s.append(str_structure(-1, dummy))
        s.append(''.center(n, '-'))

        # table body
        for i, structure in enumerate(self._structure_list):
            s.append(str_structure(i, structure))
        s.append(''.center(n, '='))
        return '\n'.join(s)

    def _compute_fit_matrix(self, atoms):
        """ Compute fit matrix for a single atoms object """
        logger.info('Computing fit matrix')
        if atoms != self._previous_atoms:
            logger.info('  Building new FCM object')
            self._previous_atoms = atoms.copy()
            self._previous_fcm = ForceConstantModel(atoms, self._cs)
        else:
            logger.info('  Reusing old FCM object')
        return self._previous_fcm.get_fit_matrix(
                                     atoms.get_array('displacements'))


class FitStructure:
    """This class holds a structure with displacements and forces as well as
    the fit matrix.

    Parameters
    ----------
    atoms : ASE Atoms object
        supercell structure
    user_tag : string
        custom user tag
    fit_matrix : NumPy array
        fit matrix; NumPy (N, M) array with `N = 3 * len(atoms)`
    """

    def __init__(self, atoms, user_tag=None, fit_matrix=None):
        self._fit_ready = False
        self._atoms = atoms
        self._user_tag = user_tag
        self.set_fit_matrix(fit_matrix)

    @property
    def fit_matrix(self):
        """NumPy array : the fit matrix"""
        return self._fit_matrix

    @property
    def atoms(self):
        """ASE Atoms object : supercell structure"""
        return self._atoms

    @property
    def forces(self):
        """NumPy array : forces"""
        return self._atoms.get_array('forces')

    @property
    def displacements(self):
        """NumPy array : atomic displacements"""
        return self._atoms.get_array('displacements')

    @property
    def fit_ready(self):
        """boolean : True if the structure is prepared for fitting, i.e. the
        fit matrix is available"""
        return self._fit_ready

    @property
    def user_tag(self):
        return str(self._user_tag)

    def set_fit_matrix(self, fit_matrix):
        """Set the fit matrix.

        Parameters
        ----------
        fit_matrix : NumPy array
            fit matrix for this structure; NumPy (N, M) array with
            `N = 3 * len(atoms)`
        """
        if fit_matrix is not None:
            if fit_matrix.shape[0] == len(self._atoms) * 3:
                self._fit_matrix = fit_matrix
                self._fit_ready = True
            else:
                logger.warning('fit matrix not compatible with atoms')
        else:
            self._fit_matrix = None
            self._fit_ready = False

    def __len__(self):
        return len(self._atoms)

    def __str__(self):
        s = []
        s.append('atoms: {}'.format(self.atoms))
        s.append('user_tag: {}'.format(self.user_tag))
        s.append('fit_ready: {}'.format(self.fit_ready))
        return '\n'.join(s)

    def __repr__(self):
        return 'FitStructure({!r}, {!r})'.format(self.atoms, self.user_tag)

    def write(self, fileobj):
        if isinstance(fileobj, str):
            tar_file = tarfile.open(name=fileobj, mode='w')
        else:
            tar_file = tarfile.open(fileobj=fileobj, mode='w')

        items_pickle = dict(atoms=self._atoms, user_tag=self.user_tag,
                            fit_ready=self.fit_ready)
        items_hdf5 = dict(fit_matrix=self.fit_matrix)

        add_items_to_tarfile_pickle(tar_file, items_pickle, 'items.pickle')
        if self.fit_ready:
            add_items_to_tarfile_hdf5(tar_file, items_hdf5, 'fit_matrix.hdf5')

        tar_file.close()

    @staticmethod
    def read(fileobj, read_fit_matrix=True):
        if isinstance(fileobj, str):
            tar_file = tarfile.open(mode='r', name=fileobj)
        else:
            tar_file = tarfile.open(mode='r', fileobj=fileobj)

        items = read_items_pickle(tar_file, 'items.pickle')
        if items['fit_ready'] and read_fit_matrix:
            fit_matrix = read_items_hdf5(
                tar_file, 'fit_matrix.hdf5')['fit_matrix']
        else:
            fit_matrix = None

        return FitStructure(items['atoms'], user_tag=items['user_tag'],
                            fit_matrix=fit_matrix)


def atoms_equals(atoms1, atoms2, tol=1e-10):
    """ Compare if two atoms are equals within some tolerance

    Parameters
    ----------
    atoms1 : ASE Atoms object
        atoms object 1
    atoms2 : ASE Atoms object
        atoms object 2

    Returns
    -------
    bool
        True if atoms are equal, else False
    """

    # pbc
    if not all(atoms1.pbc == atoms2.pbc):
        return False

    # cell
    if not np.allclose(atoms1.cell, atoms2.cell, atol=tol, rtol=0.0):
        return False

    # arrays
    if not len(atoms1.arrays.keys()) == len(atoms2.arrays.keys()):
        return False
    for key, array1 in atoms1.arrays.items():
        if key not in atoms2.arrays.keys():
            return False
        if not np.allclose(array1, atoms2.arrays[key], atol=tol, rtol=0.0):
            return False

    # passed all test, atoms must be equal
    return True
