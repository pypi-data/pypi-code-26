"""
This module introduces the ForceConstantPotential object which acts as the
finalized force constant model.
"""

import pickle
import numpy as np
from collections import Counter

from .force_constant_model import ForceConstantModel
from .core.orbit import Orbit
from .core.orientation_family import OrientationFamily
from .core.tensors import rotation_to_cart_coord, rotate_tensor


# TODO: Docstring
# TODO: Fix the relation with cluster space
class ForceConstantPotential:
    """ A finalized force constant model. Can produce force constants for any
    structure compatible with the structure for which the model was set up.

    Parameters
    ----------
    cs : ClusterSpace object
        The cluster space the model is based upon
    parameters : array
        The fitted paramteres
    """

    def __init__(self, cs, parameters):

        self.prim = cs.prim.copy()
        self.cluster_list = cs.cluster_list.copy()
        self.atom_list = cs.atom_list.copy()
        self.orbits = []
        self.spacegroup = cs.spacegroup

        # Extract the eigentensors from the cluster space and use the paramters
        # to construct the finalized force constants
        parameters = cs._map_parameters(parameters)
        p = 0
        for orb in cs.orbits:
            new_orbit = Orbit()
            fc = np.zeros(orb.eigentensors[0].shape)
            for et, a in zip(orb.eigentensors, parameters[p:]):
                fc += et * a
            new_orbit.force_constant = fc
            new_orbit.order = orb.order
            new_orbit.radius = orb.radius
            new_orbit.maximum_distance = orb.maximum_distance
            for of in orb.orientation_families:
                new_of = OrientationFamily()
                new_of.cluster_indices = of.cluster_indices.copy()
                sym_ind = of.symmetry_index
                R = rotation_to_cart_coord(cs.rotation_matrices[sym_ind],
                                           cs.prim.cell)
                fc = rotate_tensor(new_orbit.force_constant, R.T)
                perm = cs.permutations[of.permutation_indices[0]]
                new_of.force_constant = fc.transpose(perm)
                new_orbit.orientation_families.append(new_of)
            self.orbits.append(new_orbit)
            p += len(orb.eigentensors)

    @staticmethod
    def read(f):
        """Load a ForceConstantPotential object from a pickle file.

        Parameters
        ----------
        f : str or file object
            name of input file (str) or stream to load from (file object)

        Returns
        -------
        ForceConstantPotential object
            the original object as stored in the file
        """
        if isinstance(f, str):
            return pickle.load(open(f, 'rb'))
        else:
            try:
                return pickle.load(f)
            except Exception:
                raise Exception('Failed loading from file.')

    def write(self, f):
        """Write a ForceConstantPotential instance to a pickle file.

        Parameters
        ----------
        f : str or file object
            name of input file (str) or stream to write to (file object)
        """
        if isinstance(f, str):
            pickle.dump(self, open(f, 'wb'))
        else:
            try:
                pickle.dump(self, f)
            except Exception:
                raise Exception('Failed writing to file.')

    @property
    def orbit_data(self):
        """ list : list of dictionaries containing detailed information for
                   each orbit, e.g. cluster radius and force constant
        """
        data = []
        for orbit_index, orbit in enumerate(self.orbits):
            d = {}
            d['index'] = orbit_index
            d['order'] = orbit.order
            d['radius'] = orbit.radius
            d['maximum_distance'] = orbit.maximum_distance
            d['number_of_clusters'] = len(orbit.orientation_families)

            types = []
            for atom_ind in self.cluster_list[orbit.prototype_index]:
                types.append(self.prim.numbers[self.atom_list[atom_ind].site])
            d['prototype_cluster'] = self.cluster_list[orbit.prototype_index]
            d['prototype_atom_types'] = types

            d['geometrical_order'] = len(set(d['prototype_cluster']))
            d['force_constant'] = orbit.force_constant
            d['force_constant_norm'] = np.linalg.norm(orbit.force_constant)
            data.append(d)
        return data

    def get_force_constants(self, atoms):
        """ Return the force constants of a compatible structure.

        Parameters
        ----------
        atoms : ASE Atoms object
            input structure

        Returns
        -------
        ForceConstants object
        """
        return ForceConstantModel(atoms, self).get_force_constants()

    def __str__(self):
        orbits = self.orbit_data
        orbit_counts = Counter([orbit['order'] for orbit in orbits])
        cluster_counts = Counter()
        for orbit in orbits:
            cluster_counts[orbit['order']] += orbit['number_of_clusters']

        n = 54
        s = []
        s.append(' ForceConstantPotential '.center(n, '='))
        s.append('Spacegroup {}'.format(self.spacegroup))
        s.append('Cell:\n{}'.format(self.prim.cell))
        s.append('Basis:\n{}'.format(self.prim.basis))
        s.append('Numbers: {}'.format(self.prim.numbers))
        for order in sorted(orbit_counts.keys()):
            s.append('Order {}, #orbits {}, #cluster {}'.format(
                     order, orbit_counts[order], cluster_counts[order]))
        s.append('Total number of orbits: {} '.format(len(orbits)))
        s.append('total number of clusters: {} '
                 .format(sum(cluster_counts.values())))
        s.append(''.center(n, '='))
        return '\n'.join(s)

    def __repr__(self):
        return 'ForceConstantPotential(ClusterSpace({!r}, ...), [...])'.format(
            self.prim)
