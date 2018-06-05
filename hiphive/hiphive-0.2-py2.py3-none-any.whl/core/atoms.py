"""
Collection of functions and classes for handling information concerning atoms
and structures, including the relationship between primitive cell and
supercells that are derived thereof.
"""

import numbers
import pickle
from ase import Atoms as aseAtoms
import numpy as np
from .relate_structures import relate_structures
from ..io.logging import logger

# TODO: Rename logger
logger = logger.getChild('align_supercell')


class Atom:
    # TODO: This class should inherit some immutable to make it clear that
    # there is no reference to any other obj
    """Unique representation of an atom in a lattice with a basis

    Class for storing information about the position of an atom in a supercell
    relative to the origin of the underlying primitive cell. This class is used
    for handling the relationship between a primitive cell and supercells
    derived thereof.
    Initialize self

    Parameters
    ----------
    site/offset:
        An Atom object can be initialized by providing either

        * four elements, which are interpreted as
          `site`, `offset_x`, `offset_y`, `offset_z`
        * a list with four elements, which is interpreted as
          [`site`, `offset_x`, `offset_y`, `offset_z`], or
        * a list with two elements, which is interpreted as
          [`site`, [`offset_x`, `offset_y`, `offset_z`]].

        where all of the elements are integers. Here, `site` indicates the
        index of a site in the primitive basis and `offset` describes the
        translation of the atom position in the supercell relative to the
        origin in units of the primitive cell vectors.

    Examples
    --------
    The three following commands yield identical results

    >>> atom = Atom(1, 0, 0, 3)
    >>> atom = Atom(1, [0, 0, 3])
    >>> atom = Atom([1, 0, 0, 3])
    """
    def __init__(self, *args):
        # TODO: Decide how to docstring classes!
        # TODO: Explicit init rather than implicit init.
        # If only one argument it must be a list (#3 in examples)
        if len(args) == 1:
            site = args[0][0]
            offset = tuple(args[0][1:])
        # If two arguments it must be a site and an offset array (#2)
        elif len(args) == 2:
            site = args[0]
            offset = tuple(args[1])
        # If four arguments it must be (#3)
        elif len(args) == 4:
            site = args[0]
            offset = tuple(args[1:])
        else:
            raise TypeError

        assert isinstance(site, numbers.Integral)
        assert all(isinstance(i, numbers.Integral) for i in offset)
        assert len(offset) == 3
        assert site >= 0

        self._site = site
        self._offset = offset

    @property
    def site(self):
        """int : index of corresponding site in the primitive basis"""
        return self._site

    @property
    def offset(self):
        """list of ints : translational offset of the supercell site relative
        to the origin of the primitive cell in units of primitive lattice
        vectors"""
        return self._offset

    def __repr__(self):
        return 'Atom({}, {})'.format(self.site, self.offset)

    def spos(atom, basis):
        return np.add(basis[atom.site], atom.offset)

    def pos(atom, basis, cell):
        spos = atom.spos(basis)
        return np.dot(spos, cell)

    @staticmethod
    def spos_to_atom(spos, basis, tol=None):
        if not tol:
            # TODO: Link to config file
            tol = 1e-4
        for site, base in enumerate(basis):
            offset = np.subtract(spos, base)
            diff = offset - np.round(offset, 0)
            if np.linalg.norm(diff) < tol:
                offset = np.round(offset, 0).astype(int)
                atom = Atom(site, offset)
                assert np.linalg.norm(spos - atom.spos(basis)) < tol, (
                    '{} with basis {} != {}'.format(atom, basis, spos))
                return atom

        s = '{} not compatible with {} and tolerance {}'
        raise Exception(s.format(spos, basis, tol))

    def __hash__(self):
        return hash((self._site, *self.offset))

    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False
        return self.site == other.site and self.offset == other.offset


class Atoms(aseAtoms):
    """Minimally augmented version of the ASE Atoms class suitable for handling
    primitive cell information.

    Saves and loads by pickle.

    """
    @property
    def basis(self):
        """NumPy array : scaled coordinates of the sites in the primitive basis
        """
        return self.get_scaled_positions()

    def write(self, f):
        """ Write the object to file.

        Note: Only the cell, basis and numbers are stored!

        Parameters
        ----------
        f : str or file object
            name of input file (str) or stream to write to (file object)
        """
        data = {}
        data['cell'] = self.cell
        data['basis'] = self.basis
        data['numbers'] = self.numbers
        if isinstance(f, str):
            pickle.dump(data, open(f, 'wb'))
        else:
            try:
                pickle.dump(data, f)
            except Exception:
                raise Exception('Failed writing to file.')

    @staticmethod
    def read(f):
        """ Load an hiPhive Atoms object from file.

        Parameters
        ----------
        f : str or file object
            name of input file (str) or stream to load from (file object)

        Returns
        -------
        hiPhive Atoms object
        """
        if isinstance(f, str):
            data = pickle.load(open(f, 'rb'))
        else:
            try:
                data = pickle.load(f)
            except Exception:
                raise Exception('Failed loading from file.')
        atoms = aseAtoms(numbers=data['numbers'],
                         scaled_positions=data['basis'],
                         cell=data['cell'],
                         pbc=True)
        return Atoms(atoms)


def atom_to_spos(atom, basis):
    """Helper function for obtaining the position of a supercell atom in scaled
    coordinates.

    Parameters
    ----------
    atom : hiPhive Atom object
        supercell atom
    basis : list
        positions of sites in the primitive basis

    Returns
    -------
    array : NumPy array
        scaled coordinates of an atom in a supercell
    """
    return np.add(atom.offset, basis[atom.site])


def spos_to_atom(spos, basis, tol=1e-4):
    """Helper function for transforming a supercell position to the primitive
    basis.

    Parameters
    ----------
    spos : list
        scaled coordinates of an atom in a supercell
    basis : list
        positions of sites in the primitive basis
    tol : float
        a general tolerance

    Returns
    -------
    hiPhive Atom object
         supercell atom
    """
    # TODO: Fix tolerance
    # Loop over all sites in the basis
    for site, base in enumerate(basis):
        # If the scaled position belongs to this site, the offset is the
        # difference in scaled coordinates and should be integer
        offset = np.subtract(spos, base)
        # The diff is the difference between the offset vector and the nearest
        # integer vector.
        diff = offset - np.round(offset, 0)
        # It should be close to the null vector if this is the correct site.
        if np.linalg.norm(diff) < tol:
            # If the difference is less than the tol make the offset integers
            offset = np.round(offset, 0).astype(int)
            # This should be the correct atom
            atom = Atom(site, offset)
            # Just to be sure we check that the atom actually produces the
            # input spos given the input basis
            s = ('Atom=[{},{}] with basis {} != {}'
                 .format(atom.site, atom.offset, basis, spos))
            assert np.linalg.norm(spos - atom_to_spos(atom, basis)) < tol, s
            return atom
    # If no atom was found we throw an error
    s = '{} not compatible with {} and tolerance {}'.format(spos, basis, tol)
    # TODO: Should we throw more explicit error?
    raise Exception(s)


def align_super_cell(sc, prim, symprec=None):
    """Rotate and translate a supercell configuration such that it is aligned
    with the target primitive cell.

    Parameters
    ----------
    sc : ASE Atoms object
        supercell configuration
    prim : ASE Atoms object
        target primitive configuration
    symprec : float
        precision parameter forwarded to spglib

    Returns
    -------
    tuple of ASE Atoms object, NumPy (3,3) array, 3-dimensional vector
        The method returns the aligned supercell configuration as well as the
        rotation matrix and the translation vector that related the input to
        the aligned supercell configuration.
    """

    # TODO: Make sure the input is what we expect

    R, T = relate_structures(sc, prim)

    # Create the aligned system
    aligned_sc = Atoms(sc.copy())
    aligned_sc.pbc = False
    aligned_sc.positions = np.dot(R, aligned_sc.positions.T).T + T
    aligned_sc.cell = np.dot(R, sc.cell.T).T
    aligned_sc.pbc = True
    aligned_sc.wrap()

    return aligned_sc, R, T
