import pickle
import numpy as np
from ase.neighborlist import NeighborList


# TODO: Use another base class to hide internals from user
class Cutoffs:
    """ Contains information about cutoff config

    Contains conventient functionality to be used in the algorithms

    paramters
    ---------
    cutoff_matrix
        cutoff_matrix[i][j] corresponds to the cutoff for order i+2 and
        nbody j+2. Elements where j>i will be ignored.
    """

    def __init__(self, cutoff_matrix):

        self._cutoff_matrix = cutoff_matrix

        for i in range(len(cutoff_matrix) - 1):
            assert max(cutoff_matrix[i, :]) >= max(cutoff_matrix[i+1, :]),\
                   'Make sure cutoffs are in decreasing order'

    @property
    def orders(self):
        return list(range(2, self.max_order + 1))

    def get_cutoff(self, order=None, nbody=None):
        assert order is not None and nbody is not None
        assert order >= nbody and nbody > 1
        return self._cutoff_matrix[nbody - 2, order - 2]

    @property
    def max_cutoff(self):
        max_cutoff = 0
        for i, row in enumerate(self._cutoff_matrix):
            max_cutoff = max(max_cutoff, np.max(row[i:]))
        return max_cutoff

    @property
    def max_nbody(self):
        return self._cutoff_matrix.shape[0] + 1

    @property
    def max_order(self):
        return self._cutoff_matrix.shape[1] + 1

    def max_nbody_cutoff(self, nbody):
        assert nbody > 1
        return np.max(self._cutoff_matrix[nbody - 2, max(0, nbody - 2):])

    def max_nbody_order(self, nbody):
        assert nbody > 1
        arr = self._cutoff_matrix[nbody - 2, max(0, nbody - 2):]
        return np.count_nonzero(arr) + (nbody - 1)

    def write(self, fileobj):
        pickle.dump(self._cutoff_matrix, fileobj)

    def read(fileobj):
        data = pickle.load(fileobj)
        if type(data) is np.ndarray:
            return Cutoffs(data)
        else:
            cutoffs = data['cutoffs']
            return CutoffMaximumBody(cutoffs, len(cutoffs) + 1)

    def __str__(self):
        return str(self._cutoff_matrix)


class CutoffMaximumBody(Cutoffs):
    """ Specify cutoff-list plus maximum body

    Usefull when creating e.g. 6th order expansions but with only 3-body
    interactions.

    Parameters
    ----------
    cutoff_list : list
        list of cutoffs for order 2, 3, etc. Must be in decresing order
    max_nbody : int
        No clusters containing more than max_nbody atoms will be generated
    """

    def __init__(self, cutoff_list, max_nbody):
        cutoff_matrix = np.zeros((max_nbody - 1, len(cutoff_list)))
        for order, cutoff in enumerate(cutoff_list, start=2):
            cutoff_matrix[:, order - 2] = cutoff
        super().__init__(cutoff_matrix)


def is_cutoff_allowed(atoms, cutoff):
    """ Checks if atoms is compatible with cutoff

    Parameters
    ----------
    atoms : ASE Atoms object
        structure used for checking compatibility with cutoff
    cutoff : float
        cutoff to be tested

    Returns
    -------
    bool
        True if cutoff compatible with atoms object, else False
    """
    nbrlist = NeighborList(cutoffs=[cutoff / 2] * len(atoms), skin=0,
                           self_interaction=False, bothways=True)
    nbrlist.update(atoms)

    for i in range(len(atoms)):
        neighbors, _ = nbrlist.get_neighbors(i)
        if i in neighbors:
            return False
        if len(neighbors) != len(set(neighbors)):
            return False
    return True


def estimate_maximum_cutoff(atoms, max_iter=11):
    """ Estimates the maximum possible cutoff given the atoms object

    Parameters
    ----------
    atoms : ASE Atoms object
        structure used for checking compatibility with cutoff
    max_iter : int
        number of iterations in binary search
    """

    # First upper boundary of cutoff
    upper_cutoff = min(np.linalg.norm(atoms.cell, axis=1))

    # generate all possible offsets given upper_cutoff
    nbrlist = NeighborList(cutoffs=[upper_cutoff / 2] * len(atoms), skin=0,
                           self_interaction=False, bothways=True)
    nbrlist.update(atoms)
    all_offsets = []
    for i in range(len(atoms)):
        _, offsets = nbrlist.get_neighbors(i)
        all_offsets.extend([tuple(offset) for offset in offsets])

    # find lower boundary and new upper boundary
    unique_offsets = set(all_offsets)
    unique_offsets.discard((0, 0, 0))
    upper = min(np.linalg.norm(np.dot(offset, atoms.cell))
                for offset in unique_offsets)
    lower = upper / 2.0

    # run binary search between the upper and lower bounds
    for _ in range(max_iter):
        cutoff = (upper + lower) / 2
        if is_cutoff_allowed(atoms, cutoff):
            lower = cutoff
        else:
            upper = cutoff
    return lower
