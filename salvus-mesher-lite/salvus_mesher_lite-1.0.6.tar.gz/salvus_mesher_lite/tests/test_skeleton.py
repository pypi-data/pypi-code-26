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

from .. import Skeleton
from ..structured_grid_2D import StructuredGrid2D


def test_bottom_up():
    discontinuities = np.array([0., 0.5, 1.])
    nlayer = len(discontinuities) - 1
    hmax = np.ones(nlayer) * 0.3
    hmax[-1] = 0.17

    sk = Skeleton.create_cartesian_mesh(discontinuities, hmax)
    assert sk.nelem() == 30
    assert sk.npoint() == 42

    sk = Skeleton.create_cartesian_mesh(discontinuities, hmax,
                                        refinement_top_down=False)
    assert sk.nelem() == 40
    assert sk.npoint() == 73




def test_create_mesh_spherical_axisem_2D():
    discontinuities = np.array([0., 0.3, 0.9, 1.])
    nlayer = len(discontinuities) - 1
    hmax = np.ones(nlayer) * 0.1
    hmax[-1] = 0.05
    hmax[0] = 0.09

    # tripling, axisem
    sk = Skeleton.create_spherical_mesh(
        discontinuities, hmax, max_colat=40.,
        refinement_style='tripling', axisem=True, full_sphere=True,
        inner_core=True)

    m = sk.get_unstructured_mesh()

    c = np.array([28, 338, 418, 238, 284, 517, 445, 97, 451, 659, 556, 148,
                  433, 676, 626, 272, 394, 680, 673, 356, 500, 35, 488, 564,
                  485, 111, 150, 121, 58, 217, 196, 266, 290])

    p = np.array([1.22464680e-16, -7.70862483e-01, 6.32194996e-02,
                  1.29655681e-01, 1.30606369e-01, -3.26978590e-02,
                  2.04545191e-01, -6.87686426e-01, 2.92478374e-01,
                  6.86739866e-01, 4.24742466e-01, -6.47595624e-01,
                  5.64652179e-01, -7.71489180e-01, 7.10304622e-01,
                  5.83506293e-02, 8.34586638e-01, -2.86634569e-01])

    np.testing.assert_equal(m.connectivity.flatten()[::79], c)
    np.testing.assert_allclose(m.points.flatten()[::79], p, atol=1e-15)

    hmax[:] = 0.05
    hmax[-1] = 0.01
    sk = Skeleton.create_spherical_mesh(
        discontinuities, hmax, max_colat=40.,
        refinement_style='tripling', axisem=True, inner_core=True,
        full_sphere=True)

    m = sk.get_unstructured_mesh()

    c = np.array([51, 2651, 3029, 1315, 3662, 1210, 4952, 79, 4961, 239, 5111,
                  645, 5050, 915, 5113, 1310, 4976, 1574, 4947, 1904, 4716,
                  2161, 4602, 2495, 4363, 1844, 3187, 4454, 976, 713])

    p = np.array([1.22464680e-16, -9.07681424e-01, 1.32352800e-01,
                  8.77689750e-01, 2.69964750e-01, -6.25792053e-01,
                  4.26632033e-01, -8.29763122e-01, 5.70953956e-01,
                  -7.53948375e-01, 7.10745477e-01, -5.48749439e-01,
                  8.34380667e-01, 2.67061903e-01, 9.17985552e-01,
                  -8.56786622e-03])

    np.testing.assert_equal(m.connectivity.flatten()[::719], c)
    np.testing.assert_allclose(m.points.flatten()[::719], p, atol=1e-15)




@pytest.mark.mpl_image_compare(baseline_dir='data/mpl_baseline', tolerance=20,
                               savefig_kwargs={'dpi': 50})
def test_plot_skeleton_2D():
    sg = StructuredGrid2D.central_sphere(1., 6, hmax=np.pi/12.)
    sk = Skeleton(sg)
    return sk.plot(show=False, mode='max_edge')