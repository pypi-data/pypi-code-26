"""
The ``eigentensor_symmetrizer`` module contains the main function and helper
functions for calculating the eigentensors of a force constant given the
eigensymmetries. The main function is called symmetrize_tensor.
"""

import numpy as np
import itertools
import sympy

from .core_config import core_config
from .tensors import rotate_tensor
from ..io.logging import logger

config = core_config.eigensymmetries

# TODO: give better name
logger = logger.getChild('eigensymmetries')  # This is the module logger


def symmetrize_tensor(rotations, permutations, prototype):
    # TODO: Sane check inputs?
    """Takes eigensymmeries for a cluster and returns eigentensors.

    # TODO: Write short description and fix thesis so it can be used as ref

    Parameters
    ----------
    rotations : list of 3x3 numpy ndarrays
        list of the cartesian rotation matrices belonging to each
        eigensymmetry.
    permutations : list of arrays
        list of permutation vectors belonging to each eigensymmetry
    prototype : list of integers
        A list representing the atoms in the cluster. Used to deduce the
        atom label permutation symmetries. Must be sorted and integer.

    TODO
    ----
    Reference the thesis

    Returns
    -------
    eigentensors : list of ndarrays
        A list of eigentensors represented as ndarrays
    """

    logger.debug('Symmetrizing tensor')

    # If the rotation matrices are integer matrices, change type to int

    rotations = prepare_rotations(rotations)
    # TODO: Should the rotation matrices be double checked here?

    method = config.method
    args = (rotations, permutations, prototype)
    if method == 'iterative':
        return iterative_symmetrization(*args)
    else:
        raise NotImplementedError('method {} not implemented'.format(method))


def prepare_rotations(rotations):
    """Checks if the rotations are close to integer matrices and if so changes
    type to int
    """
    logger.debug('Preparing rotations')
    # The maximum element diff between the rotation and the nearest integer
    # matrix
    max_diff = 0.0
    for R in rotations:
        max_diff = max(np.max(np.abs(R - R.round(0))), max_diff)
    # compare with the tolerance in the config to determine if the rotations
    # are integer or not.
    integer_tol = config.rotation_integer_tolerance
    integer_rotations = max_diff < integer_tol
    logger.debug('Integer rotations: {}, max diff: {}, config tolerance: {}'
                 .format(integer_rotations, max_diff, integer_tol))
    if integer_rotations:
        rotations = [R.round(0).astype(np.int64) for R in rotations]
        for i, R1 in enumerate(rotations):
            for R2 in rotations[i+1:]:
                assert not np.allclose(R1, R2)
    else:
        assert all(R.dtype == np.float64 for R in rotations)
    return rotations


def iterative_symmetrization(rotations, permutations, prototype):
    ets = init_ets_from_label_symmetry(prototype)
    if not config.crystal_symmetries:
        return ets
    for R, perm in zip(rotations, permutations):
        if np.allclose(R, np.eye(3)) and list(perm) == sorted(perm):
            continue
        ets = apply_symmetry_to_ets(ets, R, perm)
        if not ets:
            return ets
    return ets


def init_ets_from_label_symmetry(cluster):
    order = len(cluster)
    assert sorted(cluster) == list(cluster)
    multiplicities = np.unique(cluster, return_counts=True)[1]
    ets = {}
    # Loop over all elements, represented by multi indices
    for multi_index in itertools.product([0, 1, 2], repeat=order):
        # Sort the multi index based on the multiplicities
        # e.g. cluster [1 1 2]
        # -> [z y x] == [y z x]
        sorted_multi_index = []
        j = 0
        for m in multiplicities:
            sorted_multi_index.extend(sorted(multi_index[j:j + m]))
            j += m
        sorted_multi_index = tuple(sorted_multi_index)
        if sorted_multi_index not in ets:
            ets[sorted_multi_index] = np.zeros([3]*order, dtype=np.int64)
        ets[sorted_multi_index][multi_index] = 1
    return list(ets.values())


def apply_symmetry_to_ets(ets, R, p):
    # TODO: Add logging
    conf = config.iterative
    order = len(p)
    dim = 3**order
    # integer mode or not?
    if ets[0].dtype == np.float64 or R.dtype == np.float64:
        dtype = np.float64
    else:
        dtype = np.int64
    M = np.zeros((dim, len(ets)), dtype=dtype)

    # This is the matrix
    for i, et in enumerate(ets):
        tmp = rotate_tensor(et, R.T).transpose(p)
        tmp = et - tmp
        M[:, i] = tmp.flatten()

    # Remove small elements
    M[np.abs(M) < conf.zero_tolerance] = 0

    # Create sympy matrix to solve
    M_sym = sympy.SparseMatrix.zeros(*M.shape)

    # If float use sympys simplify
    # TODO: simplify is also in sympy.Matrix.nullspace()
    if dtype is np.float64:
        tol = conf.simplify_tolerance
        for i, j in zip(*M.nonzero()):
            M_sym[i, j] = sympy.nsimplify(M[i, j], tolerance=tol)
    elif dtype is np.int64:
        for i, j in zip(*M.nonzero()):
            M_sym[i, j] = M[i, j]

    # This is currently the only method
    if conf.method == 'symbolic':
        nullspace = M_sym.nullspace()
        new_ets = []
        for col in nullspace:
            eigvec = np.zeros(dim)
            for i, num in enumerate(col):
                eigvec[i] = np.float64(num)
            new_et = np.zeros(ets[0].shape)
            for i, et in zip(eigvec, ets):
                new_et += i * et
            new_ets.append(new_et)
    else:
        raise NotImplementedError

    integer = True
    for i, et in enumerate(new_ets):
        if not np.allclose(et - et.round(0), 0):
            integer = False
            break
    if integer:
        for i, et in enumerate(new_ets):
            new_ets[i] = et.round(0).astype(np.int64)

    return new_ets


def _nsimplify(M, tol=None):
    """ Simplifies a matrix with sympy.
    """
    # TODO: Fix tolerance handling
    # TODO: Docstrings?
    M_simplify = sympy.SparseMatrix(*M.shape, 0)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            M_simplify[i, j] = sympy.nsimplify(M[i, j], tolerance=tol)
    # Returns sympy matrix ofc
    return M_simplify
