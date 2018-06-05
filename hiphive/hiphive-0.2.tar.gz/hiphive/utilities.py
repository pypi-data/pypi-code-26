"""
This module contains various support/utility functions.
"""
import numpy as np
from ase.geometry import find_mic


def get_wrapped_displacements(positions, ideal_positions, cell):
    """Compute the smallest possible displacements from positions and
    ideal_positions given cell.

    Notes
    -----
    * uses `find_mic` from ASE
    * assumes `pbc=[True, True, True]`.

    Parameters
    ----------
    positions : array
        positions array
    ideal_positions : array
        ideal positions from which displacements are computed
    cell : array
        cell with shape (3,3)

    Returns
    -------
    array
        array with wrapped displacements
    """

    displacements = []
    for pos, ideal_pos in zip(positions, ideal_positions):
        v_ij = np.array([pos - ideal_pos])
        displacements.append(find_mic(v_ij, cell, pbc=True)[0][0])
    return np.array(displacements)
