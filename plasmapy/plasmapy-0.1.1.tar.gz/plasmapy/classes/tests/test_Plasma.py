import pytest
import numpy as np
import astropy.units as u

from plasmapy.classes import plasma
from plasmapy.utils.exceptions import InvalidParticleError

@pytest.mark.parametrize('grid_dimensions, expected_size', [
    ((100, 1, 1), 100),  # Test 1D setup
    ((128, 128, 1), 16384),  # 2D
    ((64, 64, 64), 262144),  # 3D
])
def test_Plasma3D_setup(grid_dimensions, expected_size):
    r"""Function to test basic setup of the Plasma3D object.

    Tests that a Plasma3D object initiated with a particular
    specification behaves in the correct way.

    Parameters
    ----------
    grid_dimensions : tuple of ints
        Grid size of the Plasma3D object to test. Must be a tuple of
        length 3, indicating length of the grid in x, y, and z
        directions respectively. Directions not needed should have a
        length of 1.

    expected_size : int
        Product of grid dimensions.

    Examples
    --------
    >>> test_Plasma3D_setup((10, 10, 10), 1000)
    >>> test_Plasma3D_setup((100, 10, 1), 1000)
    """
    x, y, z = grid_dimensions
    test_plasma = plasma.Plasma3D(domain_x=np.linspace(0, 1, x) * u.m,
                                  domain_y=np.linspace(0, 1, y) * u.m,
                                  domain_z=np.linspace(0, 1, z) * u.m)

    # Basic grid setup
    assert test_plasma.x.size == x
    assert test_plasma.y.size == y
    assert test_plasma.z.size == z
    assert test_plasma.grid.size == 3 * expected_size

    # Core variable units and shapes
    assert test_plasma.density.size == expected_size
    assert test_plasma.density.si.unit == u.kg / u.m ** 3

    assert test_plasma.momentum.size == 3 * expected_size
    assert test_plasma.momentum.si.unit == u.kg / (u.m ** 2 * u.s)

    assert test_plasma.pressure.size == expected_size
    assert test_plasma.pressure.si.unit == u.Pa

    assert test_plasma.magnetic_field.size == 3 * expected_size
    assert test_plasma.magnetic_field.si.unit == u.T

    assert test_plasma.electric_field.size == 3 * expected_size
    assert test_plasma.electric_field.si.unit == u.V / u.m


# @pytest.mark.parametrize([()])
def test_Plasma3D_derived_vars():
    r"""Function to test derived variables of the Plasma3D class.

    Tests the shapes, units and values of variables derived from core
    variables.  The core variables are set with arbitrary uniform
    values.
    """
    test_plasma = plasma.Plasma3D(domain_x=np.linspace(0, 1, 64) * u.m,
                                  domain_y=np.linspace(0, 1, 64) * u.m,
                                  domain_z=np.linspace(0, 1, 1) * u.m)

    # Set an arbitrary uniform values throughout the plasma
    test_plasma.density[...] = 2.0 * u.kg / u.m ** 3
    test_plasma.momentum[...] = 10.0 * u.kg / (u.m ** 2 * u.s)
    test_plasma.pressure[...] = 1 * u.Pa
    test_plasma.magnetic_field[...] = 0.01 * u.T
    test_plasma.electric_field[...] = 0.01 * u.V / u.m

    # Test derived variable units and shapes
    assert test_plasma.velocity.shape == test_plasma.momentum.shape
    assert (test_plasma.velocity == 5.0 * u.m / u.s).all()

    assert test_plasma.magnetic_field_strength.shape == \
        test_plasma.magnetic_field.shape[1:]
    assert test_plasma.magnetic_field_strength.si.unit == u.T
    assert np.allclose(test_plasma.magnetic_field_strength.value, 0.017320508)

    assert test_plasma.electric_field_strength.shape == \
        test_plasma.electric_field.shape[1:]
    assert test_plasma.electric_field_strength.si.unit == u.V / u.m

    assert test_plasma.alfven_speed.shape == test_plasma.density.shape
    assert test_plasma.alfven_speed.unit.si == u.m / u.s
    assert np.allclose(test_plasma.alfven_speed.value, 10.92548431)


class Test_PlasmaBlobRegimes:
    def test_intermediate_coupling(self):
        r"""
        Method to test for coupling parameter for a plasma.

        Tests against expected value for coupling parameter for a
        plasma in the intermediate coupling regime.

        The input values in this case have no special significance
        and are just to get the desired output.
        """

        T_e = 25 * 15e3 * u.K
        n_e = 1e26 * u.cm ** -3
        Z = 2.0
        particle = 'p'
        blob = plasma.PlasmaBlob(T_e=T_e,
                                 n_e=n_e,
                                 Z=Z,
                                 particle=particle)

        expect_regime = 'Intermediate coupling regime: Gamma = 10.585076050938532.'
        regime, _ = blob.regimes()
        testTrue = regime == expect_regime

        errStr = f"Regime should be {expect_regime}, but got {regime} instead."
        assert testTrue, errStr

    def test_strongly_coupled(self):
        r"""
        Method to test for coupling parameter for a plasma.

        Tests against expected value for coupling parameter for a
        plasma in the strongly coupled regime.

        The input values in this case have no special significance
        and are just to get the desired output.
        """

        T_e = 5 * 15e3 * u.K
        n_e = 1e26 * u.cm ** -3
        Z = 3.0
        particle = 'p'
        blob = plasma.PlasmaBlob(T_e=T_e,
                                 n_e=n_e,
                                 Z=Z,
                                 particle=particle)

        expect_regime = 'Strongly coupled regime: Gamma = 104.02780112828943.'

        regime, _ = blob.regimes()
        testTrue = regime == expect_regime

        errStr = f"Regime should be {expect_regime}, but got {regime} instead."
        assert testTrue, errStr

    def test_weakly_coupled(self):
        r"""
        Method to test for coupling parameter for a plasma.

        Tests against expected value for coupling parameter for a
        plasma in the weakly coupled regime.

        The input values in this case have no special significance
        and are just to get the desired output.
        """

        T_e = 15 * 11e3 * u.K
        n_e = 1e15 * u.cm ** -3
        Z = 2.5
        particle = 'p'
        blob = plasma.PlasmaBlob(T_e=T_e,
                                 n_e=n_e,
                                 Z=Z,
                                 particle=particle)

        expect_regime = 'Weakly coupled regime: Gamma = 0.0075178096952688445.'

        regime, _ = blob.regimes()
        testTrue = regime == expect_regime

        errStr = f"Regime should be {expect_regime}, but got {regime} instead."
        assert testTrue, errStr

    def test_thermal_kinetic_energy_dominant(self):
        r"""
        Method to test for degeneracy parameter for a plasma.

        Tests against expected value for degeneracy parameter for a
        plasma in the thermal degenerate regime.

        The input values in this case have no special significance
        and are just to get the desired output.
        """

        T_e = 10 * 11e3 * u.K
        n_e = 1e20 * u.cm ** -3
        Z = 2.5
        particle = 'p'
        blob = plasma.PlasmaBlob(T_e=T_e,
                                 n_e=n_e,
                                 Z=Z,
                                 particle=particle)

        expect_regime = 'Thermal kinetic energy dominant: Theta = 120.65958493847927'

        _, regime = blob.regimes()
        testTrue = regime == expect_regime

        errStr = f"Regime should be {expect_regime}, but got {regime} instead."
        assert testTrue, errStr

    def test_fermi_quantum_energy_dominant(self):
        r"""
        Method to test for degeneracy parameter for a plasma.

        Tests against expected value for degeneracy parameter for a
        plasma in the Fermi degenerate regime.

        The input values in this case have no special significance
        and are just to get the desired output.
        """

        T_e = 6 * 15e3 * u.K
        n_e = 1e26 * u.cm ** -3
        Z = 3.0
        particle = 'p'
        blob = plasma.PlasmaBlob(T_e=T_e,
                                 n_e=n_e,
                                 Z=Z,
                                 particle=particle)

        expect_regime = 'Fermi quantum energy dominant: Theta = 0.009872147858602853'

        _, regime = blob.regimes()
        testTrue = regime == expect_regime

        errStr = f"Regime should be {expect_regime}, but got {regime} instead."
        assert testTrue, errStr

    def test_both_fermi_and_thermal_energy_important(self):
        r"""
        Method to test for degeneracy parameter for a plasma.

        Tests against expected value for degeneracy parameter for a
        plasma whose both Fermi and thermal energy are important.

        The input values in this case have no special significance
        and are just to get the desired output.
        """

        T_e = 5 * 15e3 * u.K
        n_e = 1e25 * u.cm ** -3
        Z = 2.0
        particle = 'p'
        blob = plasma.PlasmaBlob(T_e=T_e,
                                 n_e=n_e,
                                 Z=Z,
                                 particle=particle)

        expect_regime = 'Both Fermi and thermal energy important: Theta = 0.03818537605355442'

        _, regime = blob.regimes()
        testTrue = regime == expect_regime

        errStr = f"Regime should be {expect_regime}, but got {regime} instead."
        assert testTrue, errStr


class Test_PlasmaBlob:
    @classmethod
    def setup_class(self):
        """initializing parameters for tests """
        self.T_e = 5 * 11e3 * u.K
        self.n_e = 1e23 * u.cm ** -3
        self.Z = 2.5
        self.particle = 'p'
        self.blob = plasma.PlasmaBlob(T_e=self.T_e,
                                      n_e=self.n_e,
                                      Z=self.Z,
                                      particle=self.particle)
        self.couplingVal = 10.468374460435724
        self.thetaVal = 0.6032979246923964

    def test_invalid_particle(self):
        """
        Checks if function raises error for invalid particle.
        """
        with pytest.raises(InvalidParticleError):
            plasma.PlasmaBlob(T_e=self.T_e,
                              n_e=self.n_e,
                              Z=self.Z,
                              particle="cupcakes")

    def test_electron_temperature(self):
        """Testing if we get the same electron temperature we put in """
        testTrue = self.T_e == self.blob.electron_temperature
        errStr = (f"Input electron temperature {self.T_e} should be equal to "
                  f"electron temperature of class "
                  f"{self.blob.electron_temperature}.")
        assert testTrue, errStr

    def test_electron_density(self):
        """Testing if we get the same electron density we put in """
        testTrue = self.n_e == self.blob.electron_density
        errStr = (f"Input electron density {self.n_e} should be equal to "
                  f"electron density of class "
                  f"{self.blob.electron_density}.")
        assert testTrue, errStr

    def test_ionization(self):
        """Testing if we get the same ionization we put in """
        testTrue = self.Z == self.blob.ionization
        errStr = (f"Input ionization {self.Z} should be equal to "
                  f"ionization of class "
                  f"{self.blob.ionization}.")
        assert testTrue, errStr

    def test_composition(self):
        """Testing if we get the same composition (particle) we put in """
        testTrue = self.particle == self.blob.composition
        errStr = (f"Input particle {self.particle} should be equal to "
                  f"composition of class "
                  f"{self.blob.composition}.")
        assert testTrue, errStr

    def test_coupling(self):
        """
        Tests if coupling  method value meets expected value.
        """
        methodVal = self.blob.coupling()
        errStr = (f"Coupling parameter should be {self.couplingVal} "
                  f"and not {methodVal.si.value}.")
        testTrue = np.isclose(methodVal.value,
                              self.couplingVal,
                              rtol=1e-8,
                              atol=0.0)
        assert testTrue, errStr

    def test_quantum_theta(self):
        """
        Tests if degeneracy parameter method value meets expected value.
        """
        methodVal = self.blob.quantum_theta()
        errStr = (f"Degeneracy parameter should be {self.thetaVal} "
                  f"and not {methodVal.si.value}.")
        testTrue = np.isclose(methodVal.value,
                              self.thetaVal,
                              rtol=1e-8,
                              atol=0.0)
        assert testTrue, errStr
