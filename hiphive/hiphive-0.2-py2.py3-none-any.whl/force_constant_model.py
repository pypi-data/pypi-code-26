"""
Contains the force constant modell (FCM) which handles cluster and force
constant information of a super cell object.
"""
import math
import numpy as np

from .cluster_space import ClusterSpace
from .core.atoms import Atom, atom_to_spos, spos_to_atom, align_super_cell
from .core.orbit import Orbit
from .core.orientation_family import OrientationFamily
from .core.tensors import rotation_to_cart_coord, rotate_tensor
from .core.utilities import Progress, BiMap
from .force_constants import ForceConstants
from .io.logging import logger
from .calculators.numba_calc import cluster_force_contribution

logger = logger.getChild('fcm')


class ForceConstantModel:
    """Transfers a cluster space onto a super structure

    Contains the full description of all clusters and the force constants
    within a super cell with periodic boundary conditions.

    Parameters
    ----------
    atoms : ASE atoms object
        configuration to which the cluster space is to be applied
    cs : :class:`ClusterSpace` object
        a cluster space compatible with the structure of the atoms
    """
    def __init__(self, atoms, cs):

        self.atoms = atoms.copy()
        self.orbits = []
        self.cluster_list = BiMap()
        self.cs = cs
        self._populate_orbits(atoms)

    # TODO: refactor
    def _populate_orbits(self, atoms):
        """Map the orbits from the underlying force constant potential onto the
        supercell structure associated with this force constant model.

        """
        # TODO: Comment function
        atom_lookup = {}
        cs = self.cs

        aligned_super_cell, scR, _ = align_super_cell(atoms, cs.prim)
        sc = aligned_super_cell.copy()
        sc.pbc = False
        sc.cell = cs.prim.cell
        atom_list = BiMap()
        for spos in sc.basis:
            atom_list.append(spos_to_atom(spos, cs.prim.basis))
        sorted_cluster_list = BiMap()
        if hasattr(cs, 'rotation_matrices'):
            rotations = []
            for R in cs.rotation_matrices:
                rotations.append(rotation_to_cart_coord(R, cs.prim.cell))

        def get_atom_index(atom):
            tupd_atom = (atom.site, *atom.offset)
            if tupd_atom in atom_lookup:
                return atom_lookup[tupd_atom]
            spos = atom_to_spos(atom, cs.prim.basis)
            pos = np.dot(spos, cs.prim.cell)
            spos = np.dot(pos, np.linalg.inv(aligned_super_cell.cell))
            atom = spos_to_atom(spos, aligned_super_cell.basis)
            atom_lookup[tupd_atom] = atom.site
            return atom.site

        def get_mapped_cluster(cluster, offset):
            new_cluster = []
            for atom_index in cluster:
                atom = cs.atom_list[atom_index]
                translated_atom = Atom(atom.site, np.add(atom.offset, offset))
                index = get_atom_index(translated_atom)
                new_cluster.append(index)
            return new_cluster
        logger.info('Populating orbits')
        bar = Progress(len(cs.orbits))
        for orbit_index, orbit in enumerate(cs.orbits):

            new_orbit = Orbit()
            new_orbit.order = orbit.order

            if len(orbit.eigentensors) > 0:
                ets = []
                for et in orbit.eigentensors:
                    ets.append(rotate_tensor(et, scR))
                new_orbit.eigentensors = ets
                new_orbit.force_constant = np.zeros(ets[0].shape)
            else:
                new_orbit.force_constant = rotate_tensor(orbit.force_constant,
                                                         scR)
            cluster = cs.cluster_list[orbit.prototype_index]
            _, pos, counts = np.unique(np.array(cluster),
                                       return_index=True, return_counts=True)
            new_orbit.positions = pos
            prefactor = -1 / np.prod(list(map(math.factorial, counts)))
            new_orbit.prefactors = np.array([prefactor * c for c in counts])

            for of in orbit.orientation_families:

                new_of = OrientationFamily()
                if len(orbit.eigentensors) > 0:
                    ets = []
                    R_inv = rotations[of.symmetry_index].T
                    for et in orbit.eigentensors:
                        et_of = rotate_tensor(et, R_inv)
                        ets.append(rotate_tensor(et_of, scR))
                    new_of.eigentensors = ets
                    new_of.force_constant = np.zeros(ets[0].shape)
                else:
                    new_of.force_constant = rotate_tensor(of.force_constant,
                                                          scR)

                cluster = cs.cluster_list[of.cluster_indices[0]]
                if isinstance(cs, ClusterSpace):
                    perm = cs.permutations[of.permutation_indices[0]]
                    cluster = [cluster[i] for i in np.argsort(perm)]
                for atom in atom_list:
                    if not atom.site == cs.atom_list[cluster[0]].site:
                        continue
                    offset = atom.offset
                    new_cluster = tuple(get_mapped_cluster(cluster, offset))
                    sorted_new_cluster = tuple(sorted(new_cluster))
                    if sorted_new_cluster in sorted_cluster_list:
                        raise Exception('Found cluster {} twice, check '
                                        'cutoff!'.format(sorted_new_cluster))
                    sorted_cluster_list.append(sorted_new_cluster)
                    self.cluster_list.append(new_cluster)
                    new_cluster_index = len(self.cluster_list) - 1
                    new_of.cluster_indices.append(new_cluster_index)
                new_orbit.orientation_families.append(new_of)
            self.orbits.append(new_orbit)
            bar.tick()
        bar.close()
        if isinstance(cs, ClusterSpace):
            self.parameters = np.zeros(self.cs.number_of_dofs)

    def get_force_constants(self):
        """Obtain the force constants of the super cell

        The force constants are given in a dict-like format and can be used to
        set up for example a :class:`calculator` object.

        Returns
        -------
        force constants : ForceConstants obj
            the complete set of force constants
        """

        fcs = []
        clusters = []
        for orbit in self.orbits:
            for of in orbit.orientation_families:
                fc = of.force_constant
                fcs.append(fc.copy())
                of_clusters = []
                for cluster_index in of.cluster_indices:
                    cluster = self.cluster_list[cluster_index]
                    of_clusters.append(tuple(cluster))
                clusters.append(of_clusters)
        return ForceConstants(
            cluster_groups=clusters, fc_list=fcs, atoms=self.atoms)

    def set_parameters(self, parameters):
        """ Sets the parameters of the model

        Parameters
        ----------
        parameters : list
        """
        # TODO: Property of this?
        self.parameters = parameters
        mapped_parameters = self.cs._map_parameters(parameters)
        p = 0
        for orb in self.orbits:
            fc_is_zero = np.allclose(orb.force_constant, 0)
            params_is_zero = np.allclose(
                mapped_parameters[p: p+len(orb.eigentensors)], 0)
            if fc_is_zero and params_is_zero:
                p += len(orb.eigentensors)
                continue
            orb.force_constant *= 0
            if not params_is_zero:
                for et, a in zip(orb.eigentensors, mapped_parameters[p:]):
                    orb.force_constant += et * a
            for of in orb.orientation_families:
                of.force_constant *= 0
                if not params_is_zero:
                    for et, a in zip(of.eigentensors, mapped_parameters[p:]):
                        of.force_constant += et * a
            p += len(orb.eigentensors)

    def get_parameters(self):
        # TODO: Property of this?
        return self.parameters

    def get_forces(self, displacements):
        """ Return the forces in the system given displacements.

        The parameters of the model must be set to get any result

        Paramters
        ---------
        displacements : (N, 3) ndarray
            The displacements of each atom in the supercell
        """
        F = np.zeros(displacements.shape)
        f = np.zeros(3)
        for orbit in self.orbits:
            if np.allclose(orbit.force_constant, 0):
                continue
            order = orbit.order
            positions = orbit.positions
            prefactors = orbit.prefactors
            for of in orbit.orientation_families:
                fc = of.force_constant.flatten()
                fc_tmp = fc.copy()
                for cluster_index in of.cluster_indices:
                    cluster = self.cluster_list[cluster_index]
                    cluster_force_contribution(
                            positions, prefactors, len(prefactors),
                            fc_tmp, fc, order,
                            displacements,
                            cluster, f, F)
        return F

    def get_fit_matrix(self, displacements):
        """ Returns the matrix used to fit the parameters.

        Represent the linear relation between the parameters and the forces

        Paramters
        ---------
        displacements : (N, 3) ndarray
            The displacements of each atom in the supercell
        """

        M = np.zeros((displacements.shape[0] * 3,
                      len(self.parameters)))
        bar = Progress(len(self.parameters))
        for i in range(len(self.parameters)):
            bar.tick()
            parameters = np.zeros(len(self.parameters))
            parameters[i] = 1.0
            self.set_parameters(parameters)
            M[:, i] = self.get_forces(displacements).flatten()
        bar.close()
        return M
