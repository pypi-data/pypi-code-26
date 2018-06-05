"""Contains a calculator which given an arbitrary list of clusters and
associated force constants can calculate the energy and forces of a displaced
system
"""
import numpy as np
import math

from ase.calculators.calculator import Calculator, all_changes
from ase.geometry import find_mic

from .numba_calc import cluster_force_contribution


class ForceConstantCalculator(Calculator):
    """This class provides an ASE calculator that can be used in conjunction
    with integrators and optimizers with the `atomic simulation environment
    (ASE) <https://wiki.fysik.dtu.dk/ase/index.html>`_. To initialize an object
    of this class one must provide the ideal atomic configuration along with a
    compatible force constant model.

    Parameters
    -----------
    atoms_ideal : ASE Atoms object
        ideal (reference) configuration (i.e. without displacements)
    fcs: ForceConstants object
        the ForceConstants object must be compatible with the ideal
        (reference) configuration
    """

    implemented_properties = ['energy', 'forces']

    def __init__(self, fcs):
        Calculator.__init__(self)

        if fcs.atoms is None:
            raise ValueError('ForceConstants has no atoms object')
        self.atoms_ideal = fcs.atoms.copy()

        # Nearest neighbor distance used as maximum displacement allowed,
        # stops exploding MD simulations.
        self.max_allowed_disp = 2 * np.min(sorted(np.unique(
            self.atoms_ideal.get_all_distances(mic=True).round(4)))[1])

        self.force_constants = []
        self.unique_representation = []
        self.multiplicities = []
        self.clusters = []
        # The main idea is to precompute the prefactor and multiplicities of
        # belonging to each cluster
        for cluster, fc in fcs.get_fc_dict().items():
            self.clusters.append(tuple(cluster))
            assert fc.shape == (3,) * len(cluster)
            self.force_constants.append(fc)
            unique = np.unique(cluster, return_index=True, return_counts=True)
            self.unique_representation.append(unique)
            multiplicity = np.prod(list(map(math.factorial, unique[2])))
            self.multiplicities.append(multiplicity)

    def calculate(self, atoms=None, properties=['energy'],
                  system_changes=all_changes):
        Calculator.calculate(self, atoms, properties, system_changes)
        self._check_atoms()
        self._compute_displacements()

        if 'forces' in properties or 'energy' in properties:
            E, forces = self.compute_energy_and_forces()
            self.results['forces'] = forces
            self.results['energy'] = E

    def _check_atoms(self):
        """Check that the atomic configuration, with which the calculator is
        associated, is compatible with the ideal configuration provided during
        initialization."""
        assert len(self.atoms) == len(self.atoms_ideal)
        assert all(self.atoms.numbers == self.atoms_ideal.numbers)

    def _compute_displacements(self):
        """Evaluate the atomic displacements between the current and the ideal
        (reference) configuration."""
        displacements = []
        for pos, ideal_pos in zip(self.atoms.positions,
                                  self.atoms_ideal.positions):
            v_ij = np.array([pos - ideal_pos])
            displacements.append(find_mic(v_ij, self.atoms.cell,
                                          pbc=True)[0][0])
        self.displacements = np.array(displacements)

        # sanity check that displacements are not too large
        max_disp = np.max(np.linalg.norm(self.displacements, axis=1))
        if max_disp > self.max_allowed_disp:
            raise ValueError(
                'Displacement {:.5f} larger than maximum allowed displacement'
                ' {:.5f}'.format(max_disp, self.max_allowed_disp))

    def compute_energy_and_forces(self):
        """Compute energy and forces.

        Returns
        -------
        float, list of 3-dimensional vectors
            energy and forces
        """

        E = 0.0
        forces = np.zeros((len(self.atoms), 3))
        f = np.zeros(3)  # Temporary storage of single force
        forces_tmp = np.zeros(forces.shape)
        for unique_repr, fc, multiplicity, cluster in \
                zip(self.unique_representation, self.force_constants,
                    self.multiplicities, self.clusters):
            order = len(cluster)
            fc = fc.flatten()
            fc_tmp = np.zeros(len(fc))
            indices, positions, counts = unique_repr
            prefactors = np.array([-count/multiplicity for count in counts])
            forces_tmp *= 0
            cluster_force_contribution(positions, prefactors, len(prefactors),
                                       fc_tmp, fc, order,
                                       self.displacements,
                                       cluster, f, forces_tmp)
            for i in set(cluster):
                E += - np.dot(self.displacements[i], forces_tmp[i]) / order
            forces += forces_tmp
        return E, forces

    def __repr__(self):
        fc_dict_str = '{{{}: {}, ...}}'.format(
            self.clusters[0], self.force_constants[0])
        fcs_str = 'ForceConstants(fc_dict={}, atoms={!r})'.format(
            fc_dict_str, self.atoms_ideal)
        return 'ForceConstantCalculator({})'.format(fcs_str)
