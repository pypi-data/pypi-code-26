"""
Module containing tensor related functions
"""

import numpy as np


def get_einsum_path(indices_list, optimize='optimal'):
    contr = []
    for indices in indices_list:
        arr = np.random.random((3,)*len(indices))
        contr.append(arr)
        contr.append(list(indices))
    path = np.einsum_path(*contr, optimize=optimize)
    return path[0]


def rotate_tensor(T, R):
    """Equivalent to T_abc... = T_ijk... R_ia R_jb R_kc ... """
    order = len(T.shape)
    einsum_input = [T, list(range(order))]
    for i in range(order):
        einsum_input.append(R)
        einsum_input.append([i, order + i])
    return np.einsum(*einsum_input)


def rotation_to_cart_coord(R, cell):
    """Return the rotation matrix in cart coord given a cell metric """
    return np.dot(np.dot(cell.T, R), np.linalg.inv(cell.T))
