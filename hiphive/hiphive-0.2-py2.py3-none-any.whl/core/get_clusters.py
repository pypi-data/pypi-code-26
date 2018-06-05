# Contains the get_clusters function which generates clusters

from ase.neighborlist import NeighborList
import numpy as np
import itertools as it
from collections import defaultdict

from .utilities import BiMap
from ..io.logging import logger

logger = logger.getChild('get_clusters')


# TODO: This function could be made a bit more general
def get_clusters(atoms, cutoffs, nPrim, multiplicity=True,
                 use_geometrical_order=False):
    """Generate a list of all clusters in the atoms object which includes the
    center atoms with positions within the cell metric. The cutoff determines
    up to which order and range clusters should be generated.

    With multiplicity set to True clusters like `[0,0]` and `[3,3,4` etc will
    be generated. This is useful when doing force constants but not so much for
    cluster expansions.

    The geometrical order is the total number of different atoms in the
    cluster. `[0,0,1]` would have geometrical order 2 and `[1,2,3,4]` would
    have order 4. If the key word is True the cutoff criteria will be based on
    the geometrical order of the cluster. This is based on the observation that
    many body interactions decrease fast with cutoff but anharmonic
    interactions can be quite long ranged.

    Parameters
    ----------
    atoms : ASE Atoms object
        can be a general atoms object but must have pbc=False.
    cutoffs : dict
        the keys specify the order while the values specify the cutoff radii
    multiplicity : bool
        includes clusters where same atom appears more than once
    geometrical_order : bool
        specifies if the geometrical order should be used as cutoff_order,
        otherwise the normal order of the cluster is used

    Returns
    -------
    list of tuples
        a list of clusters where each entry is a tuple of indices,
        which refer to the atoms in the input supercell
    """

    logger.info('Generating clusters...')
    cluster_dict = defaultdict(list)
    for i in range(nPrim):
        for order in cutoffs.orders:
            cluster = (i,) * order
            cluster_dict[order].append(cluster)
    for nbody in range(2, cutoffs.max_nbody + 1):
        cutoff = cutoffs.max_nbody_cutoff(nbody)
        nbody_clusters, nbody_cutoffs = \
            generate_geometrical_clusters(atoms, nPrim, cutoff, nbody)
        for order in range(nbody, cutoffs.max_nbody_order(nbody) + 1):
            for cluster, cutoff in zip(nbody_clusters, nbody_cutoffs):
                if cutoff < cutoffs.get_cutoff(nbody=nbody, order=order):
                    clusters = extend_cluster(cluster, order)
                    cluster_dict[order].extend(clusters)
    cluster_list = BiMap()
    for key in sorted(cluster_dict):
        for cluster in sorted(cluster_dict[key]):
            cluster_list.append(cluster)
    return cluster_list


def generate_geometrical_clusters(atoms, nPrim, cutoff, order):
    nm, dm = create_neighbor_matrices(atoms, cutoff)
    clusters = []
    cutoffs = []
    i, j = 0, 0
    for tup in it.combinations(range(len(atoms)), r=order):
        if tup[0] >= nPrim:
            break
        if not nm[tup[i], tup[j]]:
            continue
        for i, j in it.combinations(range(order), r=2):
            if not nm[tup[i], tup[j]]:
                break
        else:
            clusters.append(tup)
            cutoffs.append(np.max(dm[tup, :][:, tup]))
    return clusters, cutoffs


def create_neighbor_matrices(atoms, cutoff):
    atoms = atoms.copy()
    atoms.pbc = False
    nAtoms = len(atoms)
    nl = NeighborList([cutoff / 2] * nAtoms, skin=0, bothways=True)
    nl.update(atoms)
    neighbor_matrix = np.eye(nAtoms, dtype=bool)
    distance_matrix = np.zeros((nAtoms, nAtoms))
    for i in range(nAtoms):
        indices, _ = nl.get_neighbors(i)
        neighbor_matrix[i, indices] = True
        distance_matrix[i, indices] = atoms.get_distances(i, indices)
    return neighbor_matrix, distance_matrix


def extend_cluster(cluster, order):
    clusters = []
    cluster = tuple(cluster)
    nbody = len(cluster)
    r = order - nbody
    for tup in it.combinations_with_replacement(cluster, r):
        new_cluster = sorted(cluster + tup)
        clusters.append(tuple(new_cluster))
    return clusters
