"""
The ``io.shengBTE`` module provides functions for reading and writing data
files in shengBTE format.

Todo
----
These functions have not really been tested, i.e. write a fc3 with
write_shengBTE_fc3 and pass the file to shengBTE

"""

import numpy as np
from itertools import product
from ase.geometry import wrap_positions

from ..core.atoms import spos_to_atom
from ..force_constants import get_permuted_fcs


def read_shengBTE_fc3(filename, atoms_prim, atoms_super):
    """Parse third order force constants file in shengBTE format.

    Parameters
    -----------
    filename: str
        input file name
    atoms_prim: ASE Atoms object
        primitive configuration (equivalent to ``POSCAR`` file used in the
        shengBTE calculation)
    atoms_super: ASE Atoms object
        supercell configuration (equivalent to ``SPOSCAR`` file used in the
        shengBTE calculation)

    Returns
    --------
    dict
        dictionary with keys corresponding to triplets in `atoms_super` and
        values corresponding to their force constants as a NumPy (3,3,3) array.
        Dictionary is sparse in permutations.
    """

    basis = atoms_prim.positions.copy()

    fc3_dict = {}
    with open(filename, 'r') as f:

        lines = f.readlines()
        num_fcs = int(lines[0])
        line_index = 2
        for i in range(1, num_fcs+1):

            # sanity check
            assert int(lines[line_index]) == i, (int(lines[line_index]), i)

            # find atomic indices in supercell for the three atoms
            cell_pos0 = np.array([0.0, 0.0, 0.0])
            cell_pos1 = np.array([float(fld)
                                 for fld in lines[line_index+1].split()])
            cell_pos2 = np.array([float(fld)
                                 for fld in lines[line_index+2].split()])

            basis_index0, basis_index1, basis_index2 = \
                [int(fld)-1 for fld in lines[line_index+3].split()]

            spos0 = cell_pos0 + basis[basis_index0]
            spos1 = cell_pos1 + basis[basis_index1]
            spos2 = cell_pos2 + basis[basis_index2]

            spos0, spos1, spos2 = wrap_positions([spos0, spos1, spos2],
                                                 atoms_super.cell, pbc=True)

            ind0 = find_pos_in_array(spos0, atoms_super.positions)
            ind1 = find_pos_in_array(spos1, atoms_super.positions)
            ind2 = find_pos_in_array(spos2, atoms_super.positions)

            triplet = (ind0, ind1, ind2)
            if triplet in fc3_dict.keys():
                raise ValueError('Triplet found twice', ind0, ind1, ind2)

            # parse only sorted clusters, potentially dangerous if shengBTE
            # does not enforce permutation symmetry
            if triplet == tuple(sorted(triplet)):
                # parse fc_ijk
                fc3_ijk = np.zeros((3, 3, 3))
                for n in range(27):
                    x, y, z = [int(fld) - 1
                               for fld in lines[line_index+4+n].split()[:3]]
                    fc3_ijk[x, y, z] = float(lines[line_index+4+n].split()[-1])
                fc3_dict[triplet] = fc3_ijk

            line_index += 32

    return fc3_dict


def write_shengBTE_fc3(filename, atoms_prim, atoms_super, fc3_dict):
    """Write third order force constants file in shengBTE format.

    Parameters
    -----------
    filename: str
        input file name
    atoms_prim: ASE Atoms object
        primitive configuration (equivalent to ``POSCAR`` file used in the
        shengBTE calculation)
    atoms_super: ASE Atoms object
        supercell configuration (equivalent to ``SPOSCAR`` file used in the
        shengBTE calculation)
    fc3_dict : dictionary
        third order force constant matrix; the dictionary be sparse in
        permutations

    """

    prim_cell = atoms_prim.cell
    scaled_basis = atoms_prim.get_scaled_positions()

    scaled_positions = np.linalg.solve(prim_cell.T, atoms_super.positions.T).T
    index_offsets = [spos_to_atom(spos, scaled_basis)
                     for spos in scaled_positions]
    cell_positions = [np.dot(atom.offset, prim_cell) for atom in index_offsets]
    basis_indices = [atom.site+1 for atom in index_offsets]

    # Make sparse dict which contains only fcs where atom 0 is in primitive
    fc3_dict_sheng = {}
    for triplet, fc in fc3_dict.items():
        for triplet_perm, fc_perm in get_permuted_fcs(triplet, fc).items():
            if np.linalg.norm(cell_positions[triplet_perm[0]]) > 1e-10:
                continue
            fc3_dict_sheng[triplet_perm] = fc_perm

    with open(filename, 'w') as f:
        f.write('{}\n\n'.format(len(fc3_dict_sheng)))

        for index, ((i, j, k), fc_ijk) in enumerate(fc3_dict_sheng.items()):

            f.write('{:5d}\n'.format(index + 1))

            f.write((3*'{:14.10f}'+'\n').format(*tuple(cell_positions[j])))
            f.write((3*'{:14.10f}'+'\n').format(*tuple(cell_positions[k])))
            f.write((3*'{:5d}'+'\n').format(basis_indices[i],
                                            basis_indices[j],
                                            basis_indices[k]))

            for x, y, z in product(range(3), range(3), range(3)):
                f.write((3*' {:}').format(x+1, y+1, z+1))
                f.write('    {:14.10f}\n'.format(fc_ijk[x, y, z]))
            f.write('\n')


def find_pos_in_array(pos, pos_array, dist_tol=1e-5):
    """Return index of an entry specified by value in a list or an array.

    Parameters
    ----------
    pos : list/NumPy array
        target value
    pos_array : list of lists/NumPy arrays
        list/array to search
    dist_tol : float
        tolerance imposed during testing

    Returns
    -------
    int
        index of matching entry in pos_array; None if no match has been found
    """

    diff = np.abs(pos_array - pos).sum(axis=1)
    ind = np.argmin(diff)
    if diff[ind] < dist_tol:
        return ind
    else:
        print('Could not find pos in array')
        return None
