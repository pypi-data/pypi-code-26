"""
Module for generating rattled structures. Rattle refers to displacing atoms
with a normal distribution with zero mean and some standard deviation.
"""

import numpy as np
from scipy.special import erf
from ase.neighborlist import NeighborList


def generate_rattled_structures(atoms, n_structures, rattle_std, seed=42):
    """ Return list of rattled configurations.

    Displacements are drawn from normal distributions in x,y,z directions for
    each atom independently.

    Warning
    -------
    Repeatedly calling this function *without* providing different seeds will
    yield identical or correlated results to avoid this please specify a
    different seed for each call in such a case.

    Parameters
    ----------
    atoms : ASE Atoms object
        prototype ase atoms object
    n_structures : int
        number of structures to generate
    rattle_std : float
        rattle amplitude (standard deviation in normal distribution)
    seed : int
        seed for setting up NumPy random state from which random numbers are
        generated
    """
    rs = np.random.RandomState(seed)
    N = len(atoms)
    atoms_list = []
    for _ in range(n_structures):
        atoms_tmp = atoms.copy()
        displacements = rs.normal(0.0, rattle_std, (N, 3))
        atoms_tmp.positions += displacements
        atoms_list.append(atoms_tmp)
    return atoms_list


def generate_mc_rattled_structures(atoms, n_configs, rattle_std, d_min,
                                   seed=42, **kwargs):
    """ Return list of Monte Carlo rattled configurations.

    Rattling atom `i` is a Monte Carlo move and is accepted with a probability
    that is determined from the minimum interatomic distance `d_ij`.
    If `min(d_ij)` is smaller than `d_min` the move is only accepted with a low
    probability.

    This process is repeated for each atom a number of times meaning the
    magnitude of the final displacements are not connected to `rattle_std`.

    Warning
    -------
    Repeatedly calling this function *without* providing different seeds will
    yield identical or correlated results to avoid this please specify a
    different seed for each call in such a case.

    Notes
    ------
    Note that this might not generate a symmetric distribution for the
    displacements
    kwargs will be forwarded to mc_rattle (see doc for this function for
    detailed explanation)

    Parameters
    ----------
    atoms : ASE Atoms object
        prototype ase atoms object
    n_structures : int
        number of structures to generate
    rattle_std : float
        rattle amplitude (standard deviation in normal distribution). Note this
        value is not connected to the final average displacement for the
        structures.
    d_min : float
        interatomic distance used for computing the probability for each rattle
        move.
    seed : int
        seed for setting up NumPy random state from which random numbers are
        generated
    """
    rs = np.random.RandomState(seed)
    atoms_list = []
    for _ in range(n_configs):
        atoms_tmp = atoms.copy()
        seed = rs.randint(1, 1000000000)
        displacements = mc_rattle(atoms_tmp, rattle_std, d_min, seed=seed,
                                  **kwargs)
        atoms_tmp.positions += displacements
        atoms_list.append(atoms_tmp)
    return atoms_list


def _probability_mc_rattle(d, d_min, width):
    """ Monte Carlo probability function as an error function.

    Parameters
    ----------
    d_min : float
        center value for the error function
    width : float
        width of error function
    """

    return (erf((d-d_min)/width) + 1.0) / 2


def mc_rattle(atoms, rattle_std, d_min, width=0.1, N_iter=10,
              max_attempts=5000, max_disp=2.0, active_atoms=None, seed=42):
    """ Generate displacements using the Monte Carlo rattle method

    Parameters
    ----------
    atoms : ASE Atoms object
        prototype ase atoms object
    rattle_std : float
        rattle amplitude (standard deviation in normal distribution)
    d_min : float
        interatomic distance used for computing the probability for each rattle
        move. Center position of the error function
    width : float
        width of the error function
    N_iter : int
        Number of Monte Carlo cycle
    max_disp : float
        rattle moves that yields a displacement larger than max_disp will
        always be rejected. This rarley occurs and is more used as a safety net
        for not generating structures where two or more have swapped positions.
    max_attempts : int
        limit for how many attempted rattle moves are allowed a single atom.
        If this limit is reached an `Exception` is raised.
    active_atoms : list
        list of which atomic indices should undergo Monte Carlo rattling
    seed : int
        seed for setting up NumPy random state from which random numbers are
        generated
    """
    rs = np.random.RandomState(seed)

    if active_atoms is None:
        active_atoms = range(len(atoms))

    atoms_rattle = atoms.copy()
    reference_positions = atoms_rattle.get_positions()
    nbr_list = NeighborList([d_min]*len(atoms_rattle), skin=0.0,
                            self_interaction=False, bothways=True)
    nbr_list.update(atoms_rattle)

    # run Monte Carlo
    for _ in range(N_iter):
        for i in active_atoms:
            i_nbrs = np.setdiff1d(nbr_list.get_neighbors(i)[0], [i])
            for n in range(max_attempts):
                delta_disp = rs.normal(0.0, rattle_std, 3)
                atoms_rattle.positions[i] += delta_disp
                disp_i = atoms_rattle.positions[i] - reference_positions[i]
                if np.linalg.norm(disp_i) > max_disp:
                    continue
                min_distance = np.min(atoms_rattle.get_distances(i, i_nbrs,
                                                                 mic=True))
                if _probability_mc_rattle(min_distance, d_min, width) > \
                        rs.rand():  # accept disp_i
                    break
                else:  # revert disp_i
                    atoms_rattle[i].position -= delta_disp
            else:
                raise Exception('Maxmium attempts for atom {}'.format(i))
    displacements = atoms_rattle.positions - reference_positions
    return displacements
