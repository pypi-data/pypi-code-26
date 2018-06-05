import itertools
import numpy as np
import spglib as spg
from . import atoms as atoms_module
from ..io.logging import logger

logger = logger.getChild('relate_structures')


def relate_structures(reference, target):
    """Finds rotation and translation operations that align two structures with
    periodic boundary conditions.

    The rotation and translation in Cartesian coordinates will map the
    reference structure onto the target

    Parameters
    ----------
    reference : ASE Atoms
        The reference structure to be mapped
    target : ASE Atoms
        The target structure

    Returns
    -------
    R : NumPy (3, 3) array
        The rotation matrix in Cartesian coordinates
    T : NumPy (3) array
        The translation vector in Cartesian coordinates
    """

    logger.debug('Reference atoms:')
    _debug_log_atoms(reference)

    reference_primitive_cell = get_primitive_cell(reference)

    logger.debug('Reference primitive cell')
    _debug_log_atoms(reference_primitive_cell)

    logger.debug('Target atoms:')
    _debug_log_atoms(target)

    target_primitive_cell = get_primitive_cell(target)

    logger.debug('Target primitive cell')
    _debug_log_atoms(target_primitive_cell)

    logger.debug('Sane check that primitive cells can match...')
    _assert_numbers_match(reference_primitive_cell.numbers,
                          target_primitive_cell.numbers)
    _assert_volume_match(reference_primitive_cell.cell,
                         target_primitive_cell.cell)

    logger.debug('Finding rotations...')
    rotations = _find_rotations(reference_primitive_cell.cell,
                                target_primitive_cell.cell)

    logger.debug('Finding transformations...')
    for R in rotations:
        rotated_reference_primitive_cell = \
            rotate_atoms(reference_primitive_cell, R)
        T = _find_translation(rotated_reference_primitive_cell,
                              target_primitive_cell)
        if T is not None:
            break
    else:
        raise Exception(('Found no translation!\n'
                         'Reference primitive cell basis:\n'
                         '{}\n'
                         'Target primitive cell basis:\n'
                         '{}')
                        .format(reference_primitive_cell.basis,
                                target_primitive_cell.basis))

    logger.debug(('Found rotation\n'
                  '{}\n'
                  'and translation\n'
                  '{}')
                 .format(R, T))

    return R, T


def is_rotation(R, cell_metric=None):
    """Checks if rotation matrix is orthonormal

    A cell metric can be passed of the rotation matrix is in scaled coordinates

    Parameters
    ----------
    R : Numpy 3x3 matrix
        The rotation matrix
    cell_metric: Numpy 3x3 matrix
        Optinal cell metric if the rotation is in scaled coordinates
    """
    if not cell_metric:
        cell_metric = np.eye(3)

    V = cell_metric
    V_inv = np.linalg.inv(V)
    lhs = np.linalg.multi_dot([V_inv, R.T, V, V.T, R, V_inv.T])

    return np.allclose(lhs, np.eye(3), atol=1e-4)  # TODO: tol


def _find_rotations(reference_cell_matric, target_cell_matric):
    """Generate all proper and improper rotations aligning two cell metrics"""

    rotations = []
    for perm in itertools.permutations([0, 1, 2]):
        R = np.dot(target_cell_matric.T,
                   np.linalg.inv(reference_cell_matric[perm, :].T))
        # Make sure the improper rotations are included
        for inv in itertools.product([1, -1], repeat=3):
            R = np.dot(R, np.diag(inv))
            # Make sure the rotation is orthonormal
            if is_rotation(R):
                for R_tmp in rotations:
                    if np.allclose(R, R_tmp):  # TODO: tol
                        break
                else:
                    rotations.append(R)

    assert rotations, ('Found no rotations! Reference cell metric:\n'
                       '{}\n'
                       'Target cell metric:\n'
                       '{}').format(reference_cell_matric, target_cell_matric)

    logger.debug('Found {} rotations'.format(len(rotations)))

    return rotations


def _assert_numbers_match(reference_numbers, target_numbers):
    """ Asserts that two configurations contain the same number and types of
    atoms. """
    reference_numbers = sorted(reference_numbers)
    target_numbers = sorted(target_numbers)
    assert_text = ('Atom species do not match.\n'
                   'Reference: {}\n'
                   'Target: {}').format(reference_numbers, target_numbers)

    assert reference_numbers == target_numbers, assert_text


def _assert_volume_match(reference_cell, target_cell):
    """Assert cell sizes are equal"""
    reference_volume = np.linalg.det(reference_cell)
    target_volume = np.linalg.det(target_cell)
    assert_text = ('Cell sizes do not match. Check lattice constants!\n'
                   'Reference volume: {}, primitive cell metric:\n{}\n'
                   'Target colume: {}, primitive cell metric:\n{}'
                   .format(reference_volume, reference_cell,
                           target_volume, target_cell))
    # TODO: tol
    assert np.isclose(reference_volume, target_volume), assert_text


# TODO: tol
def get_primitive_cell(atoms, to_primitive=True, no_idealize=True):
    """Get primitive cell from spglib

    Parameters
    ----------
    atoms: ASE Atoms object
    to_primitive: bool
        passed to spglib
    no_idealize: bool
        passed to spglib
    """
    spg_primitive_cell = spg.standardize_cell(atoms, to_primitive=True,
                                              no_idealize=True)
    primitive_cell = atoms_module.Atoms(cell=spg_primitive_cell[0],
                                        scaled_positions=spg_primitive_cell[1],
                                        numbers=spg_primitive_cell[2],
                                        pbc=True)
    return primitive_cell


def _debug_log_atoms(atoms):
    logger.debug('cell:\n{}'.format(atoms.cell))
    logger.debug('spos:\n{}'.format(atoms.get_scaled_positions()))
    logger.debug('pos:\n{}'.format(atoms.positions))
    logger.debug('numbers:\n{}'.format(atoms.numbers))


def rotate_atoms(atoms, rotation):
    """Rotates the cell and positions of Atoms and returns a copy

    Parameters
    ----------
    atoms : ASE Atoms object
    rotation: Numpy 3x3 matrix
    """

    cell = np.dot(rotation, atoms.cell.T).T
    positions = np.dot(rotation, atoms.positions.T).T
    return atoms_module.Atoms(cell=cell, positions=positions,
                              numbers=atoms.numbers, pbc=atoms.pbc)


def _find_translation(reference, target):
    """Given two compatible atoms returns the translation

    I.e. the two atoms obj must describe the same structure when infinitely
    repeated but differ by a translation
    """

    atoms = atoms_module.Atoms(cell=target.cell,
                               positions=reference.positions,
                               numbers=reference.numbers,
                               pbc=True)
    atoms.wrap()

    atoms_atom_0 = atoms[0]
    for atom in target:
        if atoms_atom_0.symbol != atom.symbol:
            continue
        T = atom.position - atoms_atom_0.position
        atoms_copy = atoms.copy()
        atoms_copy.positions += T
        if atoms_equal(atoms_copy, target):
            return T
    return None


def atoms_equal(atoms_1, atoms_2):
    """Compares two configurations with periodic boundary conditions.

    The atoms should have the same
    * cell
    * elements
    * scaled positions (mod 1)
    * pbc

    Compared to Atoms.__eq__ the order of the atoms does not matter
    """
    nAtoms = len(atoms_1)
    # TODO: tol
    if not (np.allclose(atoms_1.cell, atoms_2.cell, atol=1e-4) and
            nAtoms == len(atoms_2) and
            sorted(atoms_1.numbers) == sorted(atoms_2.numbers) and
            all(atoms_1.pbc == atoms_2.pbc)):
        return False
    new_cell = (atoms_1.cell + atoms_2.cell) / 2
    pos = [a.position for a in atoms_1] + [a.position for a in atoms_2]
    num = [a.number for a in atoms_1] + [a.number for a in atoms_2]
    s3 = atoms_module.Atoms(cell=new_cell, positions=pos, numbers=num,
                            pbc=True)
    for i in range(nAtoms):
        for j in range(nAtoms, len(s3)):
            d = s3.get_distance(i, j, mic=True)
            if abs(d) < 1e-4:  # TODO: tol
                if s3[i].number != s3[j].number:
                    return False
                break
        else:
            return False
    return True
