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
import numpy as np
import pytest

from ..structured_grid_2D import StructuredGrid2D
from ..skeleton import Skeleton








def test_shell_radii():
    radii = np.array([0.5, 0.52, 0.6])
    sg = StructuredGrid2D.shell_radii(radii, 2, max_colat=20.)
    assert sg.nelem() == 4

    c = np.array([[0, 3, 4, 1], [3, 6, 7, 4], [1, 4, 5, 2], [4, 7, 8, 5]])
    x = np.array([0., 0., 0., 0.08682409, 0.09029705, 0.10418891, 0.17101007,
                  0.17785047, 0.20521209])
    y = np.array([0.5, 0.52, 0.6, 0.49240388, 0.51210003, 0.59088465,
                  0.46984631, 0.48864016, 0.56381557])

    np.testing.assert_equal(sg.get_connectivity(), c)
    np.testing.assert_allclose(sg.x.flatten(), x, atol=1e-15)
    np.testing.assert_allclose(sg.y.flatten(), y, atol=1e-15)

    sg = StructuredGrid2D.shell_radii(radii, 3, max_colat=20., min_colat=-10.)

    c = np.array([0, 3, 4, 1, 3, 6, 7, 4, 6, 9, 10, 7, 1, 4, 5, 2, 4, 7, 8, 5,
                  7, 10, 11, 8])
    x = np.array([-0.08682409, -0.09029705, -0.10418891, 0., 0., 0.,
                  0.08682409, 0.09029705, 0.10418891, 0.17101007, 0.17785047,
                  0.20521209])
    y = np.array([0.49240388, 0.51210003, 0.59088465, 0.5, 0.52, 0.6,
                  0.49240388, 0.51210003, 0.59088465, 0.46984631, 0.48864016,
                  0.56381557])

    np.testing.assert_equal(sg.get_connectivity().flatten(), c)
    np.testing.assert_allclose(sg.x.flatten(), x, atol=1e-15)
    np.testing.assert_allclose(sg.y.flatten(), y, atol=1e-15)

    et = np.array([0, 0, 0, 0, 0, 0])
    np.testing.assert_equal(sg.element_type.flatten(), et)


def test_spherical_doubling_layer():
    sg = StructuredGrid2D.spherical_doubling_layer(0.5, 0.6, 2, max_colat=20.)
    assert sg.nelem() == 6

    c = np.array([[0, 3, 4, 1], [9, 12, 13, 10], [1, 4, 5, 2], [4, 7, 8, 5],
                  [7, 10, 11, 8], [10, 13, 14, 11]])
    x = np.array([0., 0., 0., 0.08682409, 0.04793566, 0.05229345, 0.08682409,
                  0.08682409, 0.10418891, 0.08682409, 0.14235047, 0.15529143,
                  0.17101007, 0.18811108, 0.20521209])
    y = np.array([0.5, 0.55, 0.6, 0.49240388, 0.54790708, 0.59771682,
                  0.49240388, 0.49240388, 0.59088465, 0.49240388, 0.5312592,
                  0.5795555, 0.46984631, 0.51683094, 0.56381557])

    np.testing.assert_equal(sg.get_connectivity(), c)
    np.testing.assert_allclose(sg.x.flatten(), x, atol=1e-15)
    np.testing.assert_allclose(sg.y.flatten(), y, atol=1e-15)

    sg = StructuredGrid2D.spherical_doubling_layer(
        0.5, 0.6, 3, min_colat=-10., max_colat=20.)

    c = np.array([0, 3, 4, 1, 9, 12, 13, 10, 12, 15, 16, 13, 1, 4, 5, 2, 4, 7,
                  8, 5, 7, 10, 11, 8, 10, 13, 14, 11, 13, 16, 17, 14, 16, 19,
                  20, 17])
    x = np.array([-8.68240888e-02, -9.55064977e-02, -1.04188907e-01,
                  0.00000000e+00, -4.79356585e-02, -5.22934456e-02,
                  0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                  -6.93889390e-18, 4.79356585e-02, 5.22934456e-02,
                  8.68240888e-02, 9.55064977e-02, 1.04188907e-01,
                  1.71010072e-01, 1.42350475e-01, 1.55291427e-01,
                  1.71010072e-01, 1.71010072e-01, 2.05212086e-01])
    y = np.array([0.49240388, 0.54164426, 0.59088465, 0.5, 0.54790708,
                  0.59771682, 0.5, 0.5, 0.6, 0.5, 0.54790708, 0.59771682,
                  0.49240388, 0.54164426, 0.59088465, 0.46984631, 0.5312592,
                  0.5795555, 0.46984631, 0.46984631, 0.56381557])

    np.testing.assert_equal(sg.get_connectivity().flatten(), c)
    np.testing.assert_allclose(sg.x.flatten(), x, atol=1e-15)
    np.testing.assert_allclose(sg.y.flatten(), y, atol=1e-15)

    et = np.array([0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 2, 2])
    np.testing.assert_equal(sg.element_type.flatten(), et)

    sg = StructuredGrid2D.spherical_doubling_layer(0.5, 0.6, 2, max_colat=20.,
                                                   flip_vertical=True)
    assert sg.nelem() == 6

    m = sg.get_unstructured_mesh()

    c = np.array([11, 10, 1, 8, 8, 7, 3, 1])
    p = np.array([0., 0.55, 0.04357787, 0.54790708, 0.10418891, 0.48296291,
                  0.17101007, 0.51683094])

    np.testing.assert_equal(m.connectivity.flatten()[::3], c)
    np.testing.assert_allclose(m.points.flatten()[::3], p, atol=1e-15)




def test_spherical_axisem_tripling_layer():
    sg = StructuredGrid2D.spherical_axisem_tripling_layer(0.5, 0.6, 3,
                                                          max_colat=20.)
    assert sg.nelem() == 10

    c = np.array([[0, 3, 4, 1], [9, 12, 13, 10], [18, 21, 22, 19],
                  [1, 4, 5, 2], [4, 7, 8, 5], [7, 10, 11, 8], [10, 13, 14, 11],
                  [13, 16, 17, 14], [16, 19, 20, 17], [19, 22, 23, 20]])
    x = np.array([0., 0., 0., 0.05804646, 0.02741524, 0.02990753, 0.05804646,
                  0.05804646, 0.05974071, 0.05804646, 0.08347961, 0.08942536,
                  0.11530794, 0.10748647, 0.11888769, 0.11530794, 0.11530794,
                  0.14805444, 0.11530794, 0.16211535, 0.1768531, 0.17101007,
                  0.18811108, 0.20521209])
    y = np.array([0.5, 0.55, 0.6, 0.49661918, 0.54931631, 0.59925415,
                  0.49661918, 0.49661918, 0.59701847, 0.49661918, 0.54362777,
                  0.5932985, 0.48652244, 0.53939471, 0.58810349, 0.48652244,
                  0.48652244, 0.58144637, 0.48652244, 0.52556504, 0.57334368,
                  0.46984631, 0.51683094, 0.56381557])

    np.testing.assert_equal(sg.get_connectivity(), c)
    np.testing.assert_allclose(sg.x.flatten(), x, rtol=1e-6, atol=1e-15)
    np.testing.assert_allclose(sg.y.flatten(), y, rtol=1e-6, atol=1e-15)

    et = np.array([0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0])
    np.testing.assert_equal(sg.element_type.flatten(), et)

    sg = StructuredGrid2D.spherical_axisem_tripling_layer(
        0.5, 0.6, 3, max_colat=20., flip_vertical=True)
    assert sg.nelem() == 10
    m = sg.get_unstructured_mesh()

    c = np.array([17, 16, 8, 2, 16, 15, 11, 10, 10, 9, 5, 4, 4, 3])
    p = np.array([0., 0.55, 0.02492294, 0.54931631, 0.06965575, 0.49441541,
                  0.09907307, 0.53939471, 0.13836952, 0.4777864, 0.17101007,
                  0.51683094])

    np.testing.assert_equal(m.connectivity.flatten()[::3], c)
    np.testing.assert_allclose(m.points.flatten()[::3], p, atol=1e-9)


def test_central_sphere():
    nelem = 2
    r = 2.
    sg1, sg2 = StructuredGrid2D.central_sphere(r, nelem, full=True)
    sk = Skeleton([sg1, sg2])
    m = sk.get_unstructured_mesh()

    p = np.array([0., -2., 0., -1., 0., -0., 0., 1., 0., 2., 0.8, -0.8, 0.8,
                  0.8, 1., -0., 1.41421356, -1.41421356, 1.41421356,
                  1.41421356, 2., -0.])
    c = np.array([1, 5, 7, 2, 2, 7, 6, 3, 4, 3, 6, 9, 9, 6, 7, 10, 10, 7, 5, 8,
                  8, 5, 1, 0])

    np.testing.assert_allclose(m.points.flatten(), p, rtol=1e-6, atol=1e-15)
    np.testing.assert_equal(m.connectivity.flatten(), c)

    nelem = 6
    r = 2.
    sg1, sg2 = StructuredGrid2D.central_sphere(r, nelem, full=True)

    assert sg1.nelem() == 18
    assert sg2.nelem() == 12

    x = np.array([0., 0., 0., 0., 0., 0., 0., 0.46482321, 0.48241161,
                  0.4952872, 0.5, 0.4952872, 0.48241161, 0.46482321,
                  0.86871843, 0.93435922, 0.98241161, 1., 0.98241161,
                  0.93435922, 0.86871843, 1.23743687, 1.36871843, 1.46482321,
                  1.5, 1.46482321, 1.36871843, 1.23743687])
    y = np.array([-1.5, -1., -0.5, -0., 0.5, 1., 1.5, -1.46482321, -0.98241161,
                  -0.4952872, -0., 0.4952872, 0.98241161, 1.46482321,
                  -1.36871843, -0.93435922, -0.48241161, -0., 0.48241161,
                  0.93435922, 1.36871843, -1.23743687, -0.86871843,
                  -0.46482321, -0., 0.46482321, 0.86871843, 1.23743687])
    c = np.array([0, 7, 8, 1, 7, 14, 15, 8, 14, 21, 22, 15, 1, 8, 9, 2, 8, 15,
                  16, 9, 15, 22, 23, 16, 2, 9, 10, 3, 9, 16, 17, 10, 16, 23,
                  24, 17, 3, 10, 11, 4, 10, 17, 18, 11, 17, 24, 25, 18, 4, 11,
                  12, 5, 11, 18, 19, 12, 18, 25, 26, 19, 5, 12, 13, 6, 12, 19,
                  20, 13, 19, 26, 27, 20])

    np.testing.assert_allclose(sg1.x.flatten(), x, rtol=1e-6, atol=1e-15)
    np.testing.assert_allclose(sg1.y.flatten(), y, rtol=1e-6, atol=1e-15)
    np.testing.assert_equal(sg1.get_connectivity().flatten(), c)

    x = np.array([0., 0.51763809, 1., 1.41421356, 1.73205081, 1.93185165, 2.,
                  1.93185165, 1.73205081, 1.41421356, 1., 0.51763809, 0., 0.,
                  0.46482321, 0.86871843, 1.23743687, 1.36871843, 1.46482321,
                  1.5, 1.46482321, 1.36871843, 1.23743687, 0.86871843,
                  0.46482321, 0., ])
    y = np.array([2.00000000e+00, 1.93185165e+00, 1.73205081e+00,
                  1.41421356e+00, 1.00000000e+00, 5.17638090e-01,
                  -1.22464680e-16, -5.17638090e-01, -1.00000000e+00,
                  -1.41421356e+00, -1.73205081e+00, -1.93185165e+00,
                  -2.00000000e+00, 1.50000000e+00, 1.46482321e+00,
                  1.36871843e+00, 1.23743687e+00, 8.68718434e-01,
                  4.64823210e-01, -0.00000000e+00, -4.64823210e-01,
                  -8.68718434e-01, -1.23743687e+00, -1.36871843e+00,
                  -1.46482321e+00, -1.50000000e+00])
    c = np.array([0, 13, 14, 1, 1, 14, 15, 2, 2, 15, 16, 3, 3, 16, 17, 4, 4,
                  17, 18, 5, 5, 18, 19, 6, 6, 19, 20, 7, 7, 20, 21, 8, 8, 21,
                  22, 9, 9, 22, 23, 10, 10, 23, 24, 11, 11, 24, 25, 12])

    np.testing.assert_allclose(sg2.x.flatten(), x, rtol=1e-6, atol=1e-15)
    np.testing.assert_allclose(sg2.y.flatten(), y, rtol=1e-6, atol=1e-15)
    np.testing.assert_equal(sg2.get_connectivity().flatten(), c)

    # testing left orientation as well
    sg1, sg2 = StructuredGrid2D.central_sphere(r, nelem, full=True, left=True)
    assert sg1.nelem() == 18
    assert sg2.nelem() == 12

    x = np.array([-0., -0., -0., -0., -0., -0., -0., -0.46482321, -0.48241161,
                  -0.4952872, -0.5, -0.4952872, -0.48241161, -0.46482321,
                  -0.86871843, -0.93435922, -0.98241161, -1., -0.98241161,
                  -0.93435922, -0.86871843, -1.23743687, -1.36871843,
                  -1.46482321, -1.5, -1.46482321, -1.36871843, -1.23743687])
    y = np.array([1.5, 1., 0.5, -0., -0.5, -1., -1.5, 1.46482321, 0.98241161,
                  0.4952872, -0., -0.4952872, -0.98241161, -1.46482321,
                  1.36871843, 0.93435922, 0.48241161, -0., -0.48241161,
                  -0.93435922, -1.36871843, 1.23743687, 0.86871843, 0.46482321,
                  -0., -0.46482321, -0.86871843, -1.23743687])
    c = np.array([0, 7, 8, 1, 7, 14, 15, 8, 14, 21, 22, 15, 1, 8, 9, 2, 8, 15,
                  16, 9, 15, 22, 23, 16, 2, 9, 10, 3, 9, 16, 17, 10, 16, 23,
                  24, 17, 3, 10, 11, 4, 10, 17, 18, 11, 17, 24, 25, 18, 4, 11,
                  12, 5, 11, 18, 19, 12, 18, 25, 26, 19, 5, 12, 13, 6, 12, 19,
                  20, 13, 19, 26, 27, 20])

    np.testing.assert_allclose(sg1.x.flatten(), x, rtol=1e-6, atol=1e-15)
    np.testing.assert_allclose(sg1.y.flatten(), y, rtol=1e-6, atol=1e-15)
    np.testing.assert_equal(sg1.get_connectivity().flatten(), c)

    x = np.array([-0., -0.51763809, -1., -1.41421356, -1.73205081, -1.93185165,
                  -2., -1.93185165, -1.73205081, -1.41421356, -1., -0.51763809,
                  -0., -0., -0.46482321, -0.86871843, -1.23743687, -1.36871843,
                  -1.46482321, -1.5, -1.46482321, -1.36871843, -1.23743687,
                  -0.86871843, -0.46482321, -0., ])
    y = np.array([-2.00000000e+00, -1.93185165e+00, -1.73205081e+00,
                  -1.41421356e+00, -1.00000000e+00, -5.17638090e-01,
                  -1.22464680e-16, 5.17638090e-01, 1.00000000e+00,
                  1.41421356e+00, 1.73205081e+00, 1.93185165e+00,
                  2.00000000e+00, -1.50000000e+00, -1.46482321e+00,
                  -1.36871843e+00, -1.23743687e+00, -8.68718434e-01,
                  -4.64823210e-01, -0.00000000e+00, 4.64823210e-01,
                  8.68718434e-01, 1.23743687e+00, 1.36871843e+00,
                  1.46482321e+00, 1.50000000e+00])
    c = np.array([0, 13, 14, 1, 1, 14, 15, 2, 2, 15, 16, 3, 3, 16, 17, 4, 4,
                  17, 18, 5, 5, 18, 19, 6, 6, 19, 20, 7, 7, 20, 21, 8, 8, 21,
                  22, 9, 9, 22, 23, 10, 10, 23, 24, 11, 11, 24, 25, 12])

    np.testing.assert_allclose(sg2.x.flatten(), x, rtol=1e-6, atol=1e-15)
    np.testing.assert_allclose(sg2.y.flatten(), y, rtol=1e-6, atol=1e-15)
    np.testing.assert_equal(sg2.get_connectivity().flatten(), c)

    et = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    np.testing.assert_equal(sg1.element_type.flatten(), et)

    et = np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
    np.testing.assert_equal(sg2.element_type.flatten(), et)








def test_rectangle_y():
    y = np.array([0.5, 0.52, 0.6])
    sg = StructuredGrid2D.rectangle_y(y, 2)
    assert sg.nelem() == 4

    c = np.array([[0, 3, 4, 1], [3, 6, 7, 4], [1, 4, 5, 2], [4, 7, 8, 5]])
    x = np.array([0., 0., 0., 0.5, 0.5, 0.5, 1., 1., 1.])
    y = np.array([0.5, 0.52, 0.6, 0.5, 0.52, 0.6, 0.5, 0.52, 0.6])

    np.testing.assert_equal(sg.get_connectivity(), c)
    np.testing.assert_allclose(sg.x.flatten(), x, atol=1e-15)
    np.testing.assert_allclose(sg.y.flatten(), y, atol=1e-15)






def test_cartesian_axisem_tripling_layer():
    sg = StructuredGrid2D.cartesian_axisem_tripling_layer(3, min_y=0.5,
                                                          max_y=0.7)
    assert sg.nelem() == 10

    c = np.array([[0, 3, 4, 1], [9, 12, 13, 10], [18, 21, 22, 19],
                  [1, 4, 5, 2], [4, 7, 8, 5], [7, 10, 11, 8], [10, 13, 14, 11],
                  [13, 16, 17, 14], [16, 19, 20, 17], [19, 22, 23, 20]])
    x = np.array([0., 0., 0., 0.33333333, 0.14285714, 0.14285714, 0.33333333,
                  0.33333333, 0.28571429, 0.33333333, 0.43650794, 0.42857143,
                  0.66666667, 0.56349206, 0.57142857, 0.66666667, 0.66666667,
                  0.71428571, 0.66666667, 0.85714286, 0.85714286, 1., 1., 1.])
    y = np.array([0.5, 0.6, 0.7, 0.5, 0.6, 0.7, 0.5, 0.5, 0.7, 0.5, 0.6, 0.7,
                  0.5, 0.6, 0.7, 0.5, 0.5, 0.7, 0.5, 0.6, 0.7, 0.5, 0.6, 0.7])

    np.testing.assert_equal(sg.get_connectivity(), c)
    np.testing.assert_allclose(sg.x.flatten(), x, atol=1e-15)
    np.testing.assert_allclose(sg.y.flatten(), y, atol=1e-15)












@pytest.mark.mpl_image_compare(baseline_dir='data/mpl_baseline', tolerance=20,
                               savefig_kwargs={'dpi': 50})
def test_plot_structured_grid_2D_element_type():
    sg = StructuredGrid2D.spherical_doubling_layer(0.5, 0.6, 2, max_colat=20.)
    return sg.plot(show=False, mode='element_type', colorbar=True,
                   new_figure=True)