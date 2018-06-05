"""
Contains the Orbit class which hold onformation about equivalent clusters.
"""

import numpy as np
import tarfile

from .orientation_family import OrientationFamily
from ..io.read_write_files import (add_items_to_tarfile_hdf5,
                                   add_items_to_tarfile_pickle,
                                   add_list_to_tarfile_custom,
                                   read_items_hdf5,
                                   read_items_pickle,
                                   read_list_custom)


class Orbit:
    """
    This class serves as a container for storing data pertaining to an orbit.

    Attributes
    ----------
    orientation_families : list of OrientationFamily objs
        The orientation families of the orbit
    eigensymmetries : list of tuples
        Each eigensymmetry correspond to a pair where the first index is the
        symmetry and the second is the permutation
    eigentensors : list of NumPy arrays
        The decomposition of the force constant into symmetry elements
    """

    # TODO: Make properties of the parameters
    def __init__(self):
        self.orientation_families = []
        self.eigensymmetries = []
        self.eigentensors = []

    @property
    def prototype_index(self):
        """int : index of cluster that serves as prototype for this orbit

        In the code the first symmetry is always the identity so the first
        orientation family should always correspond to the prototype"""
        return self.orientation_families[0].cluster_indices[0]

    def write(self, f):
        """Write a Orbit instance to a file.

        Parameters
        ----------
        f : str or file object
            name of input file (str) or stream to write to (file object)
        """

        if isinstance(f, str):
            tar_file = tarfile.open(mode='w', name=f)
        else:
            tar_file = tarfile.open(mode='w', fileobj=f)

        # add eigentensors as NumPy array
        items_hdf5 = dict(eigentensors=np.array(self.eigentensors),
                          )
        add_items_to_tarfile_hdf5(tar_file, items_hdf5, 'eigentensors')

        # add eigensymmetries as list
        items_pickle = dict(eigensymmetries=self.eigensymmetries,
                            order=self.order, radius=self.radius,
                            maximum_distance=self.maximum_distance)
        add_items_to_tarfile_pickle(tar_file, items_pickle, 'attributes')

        # add orientation families
        add_list_to_tarfile_custom(tar_file, self.orientation_families,
                                   'orientation_families')
        tar_file.close()

    @staticmethod
    def read(f):
        """Load a ClusterSpace from file

        Parameters
        ----------
        f : string or file object
            name of input file (string) or stream to load from (file object)
        """

        orb = Orbit()
        if type(f) is str:
            tar_file = tarfile.open(mode='r', name=f)
        else:
            tar_file = tarfile.open(mode='r', fileobj=f)

        # read eigentensors hdf5
        items_hdf5 = read_items_hdf5(tar_file, 'eigentensors')
        orb.eigentensors = [et for et in items_hdf5['eigentensors']]

        # read attributes pickle
        attributes = read_items_pickle(tar_file, 'attributes')
        for name, value in attributes.items():
            orb.__setattr__(name, value)

        # read orientation families
        ofs = read_list_custom(tar_file, 'orientation_families',
                               OrientationFamily.read)
        orb.orientation_families = ofs
        return orb


def get_geometrical_radius(positions):
    """Compute the geometrical size of a 3-dimensional point cloud. The
    geometrical size is defined as the average distance to the geometric
    center.

    Parameters
    ----------
    positions : list of 3-dimensional vectors
        positions of points in cloud

    Returns
    -------
    float
        geometric size of point cloud
    """
    geometric_center = np.mean(positions, axis=0)
    return np.mean(np.sqrt(np.sum((positions - geometric_center)**2, axis=1)))


def get_maximum_distance(positions):
    """Compute the maximum distance between any two points in a 3-dimensional
    point cloud. This is equivalent to the "size" criterion used when imposing
    a certain (pair) cutoff criterion during construction of a set of clusters.

    Parameters
    ----------
    positions : list of 3-dimensional vectors
        positions of points in cloud

    Returns
    -------
    float
        maximum distance betwee any two points
    """
    if len(positions) == 0:
        return 0.0
    max_distance = 0.0
    for pt1 in positions[:-1]:
        for pt2 in positions[1:]:
            max_distance = max(max_distance, np.linalg.norm(pt1 - pt2))
    return max_distance
