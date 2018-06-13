#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of the lite version of the SalvusMesher package intended to
produce meshes for AxiSEM3D. If you are looking for the full version head
over to http://mondaic.com.

:copyright:
    Copyright (C) 2016-2018 Salvus Development Team <www.mondaic.com>,
                            ETH Zurich
:license:
    GNU General Public License, Version 3 [academic use only]
    (http://www.gnu.org/copyleft/gpl.html)
"""
from __future__ import division, print_function
import inspect
import numpy as np
import os
import pytest
from .. import model

# Most generic way to get the data directory.
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe()))), "data")


def test_built_in():
    m = model.built_in('prem_ani')
    hmax = m.get_edgelengths(dominant_period=50., elements_per_wavelength=1.5)

    disc_ref = np.array([0., 0.19172814, 0.54622508, 0.56976927, 0.87898289,
                         0.89483598, 0.90582326, 0.93721551, 0.96546853,
                         0.9874431, 0.99617015, 0.99764558, 1.])
    hmax_ref = np.array([0.01833516, 0.04219641, 0.03800921, 0.03265003,
                         0.03110501, 0.02886003, 0.02580697, 0.02429708,
                         0.02306718, 0.02300016, 0.02040496, 0.01674253])

    np.testing.assert_array_almost_equal(m.discontinuities, disc_ref)
    np.testing.assert_array_almost_equal(hmax, hmax_ref)


def test_layered():
    model_file = os.path.join(DATA_DIR, '1dmodel_axisem.bm')
    m = model.layered(model_file)
    hmax = m.get_edgelengths(dominant_period=50., elements_per_wavelength=1.5)

    disc_ref = np.array([0., 0.19172814, 0.54622508, 0.56976927, 0.87898289,
                         0.89483598, 0.90582326, 0.93721551, 0.96546853,
                         0.9874431, 0.99617015, 0.99764558, 1.])
    hmax_ref = np.array([0.01833516, 0.04219641, 0.03800921, 0.03265003,
                         0.03110501, 0.02886003, 0.02580697, 0.02429708,
                         0.02306718, 0.02300016, 0.02040496, 0.01674253])

    np.testing.assert_array_almost_equal(m.discontinuities, disc_ref)
    np.testing.assert_array_almost_equal(hmax, hmax_ref, decimal=4)


def test_deck():
    model_file = os.path.join(DATA_DIR, 'prem_noocean.txt')
    m = model.deck(model_file)
    hmax = m.get_edgelengths(dominant_period=50., elements_per_wavelength=1.5)

    disc_ref = np.array([0., 0.19172814, 0.54622508, 0.56976927, 0.87898289,
                         0.89483598, 0.90582326, 0.93721551, 0.96546853,
                         0.9874431, 0.99617015, 0.99764558, 0.99952912, 1.])
    hmax_ref = np.array([0.01833469, 0.04219531, 0.03800895, 0.03264998,
                         0.03110516, 0.02886004, 0.02580699, 0.02429708,
                         0.02306718, 0.02300016, 0.02040496, 0.01674253,
                         0.01674253])

    np.testing.assert_array_almost_equal(m.discontinuities, disc_ref)
    np.testing.assert_array_almost_equal(hmax, hmax_ref, decimal=4)


def test_init():
    name = 'test'
    model_type = 'layered'
    anelastic = False
    anisotropic = False
    nregions = 6
    discontinuities = np.linspace(0., 1., nregions)
    elastic_parameters_fct = {}
    scale = 1.

    is_fluid = np.zeros(nregions, dtype='bool')
    is_fluid[1] = True
    m = model(name, model_type, anelastic, anisotropic, nregions,
              discontinuities, is_fluid, elastic_parameters_fct, scale)
    np.testing.assert_allclose(m.get_solid_fluid_boundaries(), [0.2, 0.4],
                               atol=1e-15)

    is_fluid = np.zeros(nregions, dtype='bool')
    is_fluid[0] = True
    m = model(name, model_type, anelastic, anisotropic, nregions,
              discontinuities, is_fluid, elastic_parameters_fct, scale)
    np.testing.assert_allclose(m.get_solid_fluid_boundaries(), [0.2],
                               atol=1e-15)

    is_fluid = np.zeros(nregions, dtype='bool')
    is_fluid[[1, 2, 3]] = True
    m = model(name, model_type, anelastic, anisotropic, nregions,
              discontinuities, is_fluid, elastic_parameters_fct, scale)
    np.testing.assert_allclose(m.get_solid_fluid_boundaries(), [0.2, 0.8],
                               atol=1e-15)

    is_fluid = np.zeros(nregions, dtype='bool')
    is_fluid[[1, 3]] = True
    m = model(name, model_type, anelastic, anisotropic, nregions,
              discontinuities, is_fluid, elastic_parameters_fct, scale)
    np.testing.assert_allclose(m.get_solid_fluid_boundaries(),
                               [0.2, 0.4, 0.6, 0.8], atol=1e-15)

    is_fluid = np.zeros(nregions, dtype='bool')
    is_fluid[[0, 1, 3, 4]] = True
    m = model(name, model_type, anelastic, anisotropic, nregions,
              discontinuities, is_fluid, elastic_parameters_fct, scale)
    np.testing.assert_allclose(m.get_solid_fluid_boundaries(), [0.4, 0.6],
                               atol=1e-15)


def test_get_radial_mesh():
    m = model.built_in('prem_ani')

    cmb = m.get_fluid_regions()[0][1]
    element_boundaries = m.get_radial_mesh(dominant_period=150.,
                                           elements_per_wavelength=0.5,
                                           rmin=cmb * m.scale)

    element_boundaries_ref = np.array([0.54622508, 0.56976927, 0.72437608,
                                       0.87898289, 0.89483598, 0.90582326,
                                       0.93721551, 0.96546853, 0.9874431,
                                       0.99617015, 0.99764558, 1.])
    np.testing.assert_allclose(element_boundaries, element_boundaries_ref,
                               atol=1e-8)


def test_available_elastic_parameters():
    m = model.built_in('prem_ani')
    params = m.available_elastic_parameters
    params_ref = ['VPV', 'VPH', 'VSV', 'VSH', 'ETA', 'RHO', 'QMU', 'QKAPPA']
    assert all(map(lambda v: v in params_ref, params))

    m = model.built_in('prem_iso')
    params = m.available_elastic_parameters
    params_ref = ['VP', 'VS', 'RHO', 'QMU', 'QKAPPA']
    assert all(map(lambda v: v in params_ref, params))


def test_get_fluid_regions():
    m = model.built_in('prem_ani_ocean')
    fr = m.get_fluid_regions()
    fr_ref = np.array([(0.19172814314864228, 0.54622508240464607),
                       (0.99952911630827179, 1.0)])
    np.testing.assert_allclose(fr, fr_ref, atol=1e-8)


def test_get_is_fluid():
    m = model.built_in('prem_ani_ocean')
    x = np.linspace(0., 1. - 1e-5, 10)
    fr = m.get_is_fluid(x)
    fr_ref = np.array([False, False, True, True, True, False, False, False,
                       False, True])
    np.testing.assert_allclose(fr, fr_ref, atol=1e-8)


def test_get_vpmax():
    m = model.built_in('prem_ani_ocean')
    x = np.linspace(0., 1. - 1e-5, 10)
    vpmax = m.get_vpmax(x)
    vpmax_ref = np.array([11262.2, 11183.63367012, 10239.97453846,
                          9734.19564124, 9011.85899454, 13702.1257163,
                          12961.37489629, 12086.44432434, 10869.46871899,
                          1450.])
    np.testing.assert_allclose(vpmax, vpmax_ref, atol=1e-8)


def test_get_vmin():
    m = model.built_in('prem_ani_ocean')
    x = np.linspace(0., 1. - 1e-5, 10)
    vmin = m.get_vmin(x)
    vmin_ref = np.array([3667.8, 3612.89369074, 10239.97453846, 9734.19564124,
                         9011.85899454, 7265.23301029, 6989.19324336,
                         6643.43118656, 6056.08043431, 1450.])
    np.testing.assert_allclose(vmin, vmin_ref, atol=1e-8)


def test_get_rho():
    m = model.built_in('prem_ani_ocean')
    x = np.linspace(0., 1. - 1e-5, 10)
    rho = [m.get_rho(r) for r in x]
    rho_ref = np.array([1020.0, 12979.389836556991, 12060.117279486447,
                        11550.774005120327, 10814.99958737093,
                        5536.70905828376, 5183.3436397496407,
                        4814.3479563934088, 4404.3672133185682, 1020.0])

    np.testing.assert_allclose(rho, rho_ref, atol=1e-8)


def test_get_native_parameter():
    m = model.built_in('prem_ani_ocean')
    x = np.linspace(0., 1. - 1e-5, 10)
    rho = [m.get_native_parameter('RHO', r) for r in x]
    rho_ref = np.array([1020.0, 12979.389836556991, 12060.117279486447,
                        11550.774005120327, 10814.99958737093,
                        5536.70905828376, 5183.3436397496407,
                        4814.3479563934088, 4404.3672133185682, 1020.0])

    np.testing.assert_allclose(rho, rho_ref, atol=1e-8)


def test_get_elastic_parameter_list():
    m = model.built_in('prem_iso')
    x = np.linspace(0., 1., 10)

    pl = ['A', 'C', 'L', 'N', 'F', 'VP', 'VPH', 'VPV']
    params = m.get_elastic_parameter_list(pl, x)

    for p in pl:
        ref = m.get_elastic_parameter(p, x)
        np.testing.assert_allclose(params[p], ref, atol=1e-8)


def test_get_elastic_parameter():
    m = model.built_in('prem_iso')
    x = np.linspace(0., 1., 10)
    y = np.linspace(0., 1., 10)

    vp_ref = np.array([0.00176773, 0.0017554, 0.00160728, 0.00152789,
                       0.00141451, 0.0021507, 0.00203443, 0.00189709,
                       0.00170606, 0.00091038])

    vp = m.get_elastic_parameter('VP', x, scaled=False)
    np.testing.assert_allclose(vp, vp_ref, atol=1e-8)

    vp = m.get_elastic_parameter('VP', x, y, scaled=False)
    np.testing.assert_allclose(vp, vp_ref, atol=1e-8)

    A_ref = np.array([1.66010802e+12, 1.62337909e+12, 1.26458565e+12,
                      1.09448280e+12, 8.78315504e+11, 1.03950281e+12,
                      8.70777243e+11, 7.03278391e+11, 5.20334482e+11,
                      8.74640000e+10])
    C_ref = np.array([1.66010802e+12, 1.62337909e+12, 1.26458565e+12,
                      1.09448280e+12, 8.78315504e+11, 1.03950281e+12,
                      8.70777243e+11, 7.03278391e+11, 5.20334482e+11,
                      8.74640000e+10])
    L_ref = np.array([1.76076408e+11, 1.69419855e+11, 0.00000000e+00,
                      0.00000000e+00, 0.00000000e+00, 2.92246587e+11,
                      2.53197797e+11, 2.12479191e+11, 1.61524935e+11,
                      2.66240000e+10])
    N_ref = np.array([1.76076408e+11, 1.69419855e+11, 0.00000000e+00,
                      0.00000000e+00, 0.00000000e+00, 2.92246587e+11,
                      2.53197797e+11, 2.12479191e+11, 1.61524935e+11,
                      2.66240000e+10])
    F_ref = np.array([1.30795521e+12, 1.28453938e+12, 1.26458565e+12,
                      1.09448280e+12, 8.78315504e+11, 4.55009634e+11,
                      3.64381650e+11, 2.78320010e+11, 1.97284613e+11,
                      3.42160000e+10])
    XI_ref = np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.])
    PHI_ref = np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.])
    LAMBDA_ref = np.array([1.30795521e+12, 1.28453938e+12, 1.26458565e+12,
                           1.09448280e+12, 8.78315504e+11, 4.55009634e+11,
                           3.64381650e+11, 2.78320010e+11, 1.97284613e+11,
                           3.42160000e+10])
    MU_ref = np.array([1.76076408e+11, 1.69419855e+11, 0.00000000e+00,
                       0.00000000e+00, 0.00000000e+00, 2.92246587e+11,
                       2.53197797e+11, 2.12479191e+11, 1.61524935e+11,
                       2.66240000e+10])

    KAPPA_ref = LAMBDA_ref + 2. / 3. * MU_ref

    for ref, p in zip([A_ref, C_ref, L_ref, N_ref, F_ref, XI_ref, PHI_ref,
                       LAMBDA_ref, MU_ref, KAPPA_ref],
                      ['A', 'C', 'L', 'N', 'F', 'XI', 'PHI', 'LAMBDA', 'MU',
                       'KAPPA']):
        param = m.get_elastic_parameter(p, x, scaled=False)
        np.testing.assert_allclose(param, ref, atol=1e-8)

    # Voigt averages
    m = model.built_in('prem_ani')
    VP_ref = np.array([11262.2, 11183.63209877, 10239.96584362, 9734.17777778,
                       9011.82427984, 13702.11714678, 12961.32592593,
                       12086.37640604, 10869.29245542, 5800.])
    VS_ref = np.array([3667.8, 3612.89259259, 0., 0., 0., 7265.23333333,
                       6989.17407407, 6643.4042524, 6055.91481481, 3200.])
    LAMBDA_ref = np.array([1.30795521e+12, 1.28453938e+12, 1.26458565e+12,
                           1.09448280e+12, 8.78315504e+11, 4.55009634e+11,
                           3.64381650e+11, 2.78320010e+11, 1.97284613e+11,
                           3.42160000e+10])
    MU_ref = np.array([1.76076408e+11, 1.69419855e+11, 0.00000000e+00,
                       0.00000000e+00, 0.00000000e+00, 2.92246587e+11,
                       2.53197797e+11, 2.12479191e+11, 1.61524935e+11,
                       2.66240000e+10])

    KAPPA_ref = LAMBDA_ref + 2. / 3. * MU_ref

    for ref, p in zip([VP_ref, VS_ref, LAMBDA_ref, MU_ref, KAPPA_ref],
                      ['VP', 'VS', 'LAMBDA', 'MU', 'KAPPA']):
        param = m.get_elastic_parameter(p, x, scaled=False)
        np.testing.assert_allclose(param, ref, atol=1e-8)


def test_get_ellipticity():
    m = model.built_in('prem_iso')
    r = np.linspace(0., 1., 20)

    epsilon = m.get_ellipticity(r)
    epsilon_ref = np.array([0.00242322, 0.002424, 0.00242634, 0.00243026,
                            0.00243819, 0.0024592, 0.00247914, 0.00249705,
                            0.00251446, 0.00253261, 0.00255242, 0.00258498,
                            0.00265687, 0.00275021, 0.0028521, 0.0029555,
                            0.0030569, 0.00315485, 0.00325194, 0.00335281])
    np.testing.assert_allclose(epsilon, epsilon_ref, atol=1e-8)


def test_get_gravity():
    m = model.built_in('prem_iso')
    r = np.linspace(0., 1., 20)

    g = m.get_gravity(r)
    g_ref = np.array([9.46221019e-16, 1.22556325e+00, 2.44286620e+00,
                      3.64364184e+00, 4.76498480e+00, 5.79320689e+00,
                      6.81131165e+00, 7.79627361e+00, 8.73271491e+00,
                      9.60752275e+00, 1.04080555e+01, 1.04253087e+01,
                      1.01496547e+01, 1.00033572e+01, 9.94351746e+00,
                      9.94016517e+00, 9.97139044e+00, 1.00204100e+01,
                      9.95122899e+00, 9.82555849e+00])
    np.testing.assert_allclose(g, g_ref, atol=1e-8)


def test_get_gravitational_potential():
    m = model.built_in('prem_iso')
    r = np.linspace(0., 5., 20)

    g = m.get_gravitational_potential(r)
    g_ref = np.array([-1.11788695e+08, -1.06760036e+08, -9.29881693e+07,
                      -7.59552469e+07, -5.94687015e+07, -4.75749612e+07,
                      -3.96458010e+07, -3.39821151e+07, -2.97343507e+07,
                      -2.64305340e+07, -2.37874806e+07, -2.16249824e+07,
                      -1.98229005e+07, -1.82980620e+07, -1.69910576e+07,
                      -1.58583204e+07, -1.48671754e+07, -1.39926356e+07,
                      -1.32152670e+07, -1.25197266e+07])
    np.testing.assert_allclose(g, g_ref, atol=1e-8)


def test_get_gradient_gravity():
    m = model.built_in('prem_iso')
    r = np.linspace(0., 1., 20)

    dg = m.get_gradient_gravity(r)
    dg_ref = np.array([3.65906306e-06, 3.64675135e-06, 3.60978667e-06,
                       3.54819220e-06, 3.04494619e-06, 3.06623559e-06,
                       2.99555455e-06, 2.87193817e-06, 2.70717436e-06,
                       2.50450831e-06, 2.26398380e-06, -1.07170414e-06,
                       -6.03626978e-07, -2.89886852e-07, -8.17025832e-08,
                       5.09549886e-08, 1.27037994e-07, 1.58708722e-07,
                       -3.58162521e-07, -9.03870470e-07])
    np.testing.assert_allclose(dg, dg_ref, atol=1e-8)


def test_get_mass():

    m = model.built_in('prem_ani')
    mass = m.get_mass()
    np.testing.assert_allclose(mass, 5.97559351524e+24)


def test_get_moment_of_inertia():

    m = model.built_in('prem_ani')
    moi = m.get_moment_of_inertia()
    np.testing.assert_allclose(moi, 8.0267401387e+37)


def test_get_builtin_models():
    models = model.get_builtin_models()
    for m in models:
        assert m in ['ak135', 'iasp91', 'mars_sohl', 'Moon_Weber2011',
                     'prem_crust20_global', 'prem_crust20_cont', 'prem_ani',
                     'prem_iso', 'prem_ani_ocean', 'prem_crust20_ocean',
                     'ak135f', 'prem_ani_one_crust', 'prem_iso_one_crust',
                     'VPREMOON', 'VPREMOON_noLVL']


@pytest.mark.mpl_image_compare(baseline_dir='data/mpl_baseline', tolerance=20,
                               savefig_kwargs={'dpi': 50})
def test_plot_model():
    m = model.built_in('prem_iso')
    return m.plot(show=False)


@pytest.mark.mpl_image_compare(baseline_dir='data/mpl_baseline', tolerance=20,
                               savefig_kwargs={'dpi': 50})
def test_plot_vp_vs_profile():
    m = model.built_in('prem_iso')
    return m.plot_vp_vs_profile(show=False)


@pytest.mark.mpl_image_compare(baseline_dir='data/mpl_baseline', tolerance=20,
                               savefig_kwargs={'dpi': 50})
def test_plot_ellipticity():
    m = model.built_in('prem_iso')
    return m.plot_ellipticity(show=False)


@pytest.mark.mpl_image_compare(baseline_dir='data/mpl_baseline', tolerance=20,
                               savefig_kwargs={'dpi': 50})
def test_plot_gravity():
    m = model.built_in('prem_iso')
    return m.plot_gravity(show=False)


@pytest.mark.mpl_image_compare(baseline_dir='data/mpl_baseline', tolerance=20,
                               savefig_kwargs={'dpi': 50})
def test_plot_ellipticity_gravity():
    m = model.built_in('prem_iso')
    return m.plot_ellipticity_gravity(show=False)