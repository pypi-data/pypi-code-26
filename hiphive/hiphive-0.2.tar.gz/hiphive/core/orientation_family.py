"""
The ``orientation_family`` module contains the OrientationFamily class, which
acts like a struct that contains information about a set of equal clusters of
equal orientation in space.
"""
import pickle


class OrientationFamily:
    """A container for storing information for a "family of orientations".

    An orbit contains many clusters. Some of the clusters can be tranlsated
    onto each other and other must first be rotated. A set of clusters in the
    orbit which can all be translated onto each other are oriented in the same
    way and belongs to the same orientation family. The family is haracterized
    by the symmetry (rotation) which relates it to the prototype structure of
    the orbit.

    Since the clusters are generally stored sorted the permutation information
    must also be stored.

    Parameters
    ----------
    symmetry_index : int
        The index of the symmetry corresponding to spglibs symmetry

    Attributes
    ----------
    symmetry_index : int
        The index of the symmetry corresponding to spglibs symmetry
    cluster_indices : list of ints
        The indices of the clusters belonging to this family
    permutation_indices : list of ints
        The indices of the permutation vector
    """

    def __init__(self, symmetry_index=None):
        self.symmetry_index = symmetry_index
        self.cluster_indices = []
        self.permutation_indices = []

    def write(self, f):
        """ Write the object to file.

        Parameters
        ----------
        f : str or file object
            name of input file (str) or stream to write to (file object)
        """
        try:
            pickle.dump(self, f)
        except Exception:
            raise Exception('Failed writing to file.')

    @staticmethod
    def read(f):
        """Load a OrientationFamily object from a pickle file.

        Parameters
        ----------
        f : str or file object
            name of input file (str) or stream to load from (file object)

        Returns
        -------
        OrientationFamily object
        """
        try:
            return pickle.load(f)
        except Exception:
            raise Exception('Failed loading from file.')
