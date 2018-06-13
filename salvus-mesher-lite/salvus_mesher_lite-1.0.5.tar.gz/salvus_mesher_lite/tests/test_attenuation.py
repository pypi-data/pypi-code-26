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

from .. import attenuation


def test_invert_linear_solids():
    ls = attenuation.LinearSolid.invert_linear_solids(N=1, freq_weight=False)
    w_j_ref = np.array([0.19869163])
    y_j_ref = np.array([6.43698352])

    np.testing.assert_allclose(w_j_ref, ls.w_j, rtol=1e-5)
    np.testing.assert_allclose(y_j_ref, ls.y_j, rtol=1e-5)

    ls = attenuation.LinearSolid.invert_linear_solids(N=2, freq_weight=False)

    w_j_ref = np.array([0.02756839, 1.43198512])
    y_j_ref = np.array([2.66302747, 2.66302524])

    np.testing.assert_allclose(w_j_ref, ls.w_j, atol=1e-9)
    np.testing.assert_allclose(y_j_ref, ls.y_j, atol=1e-9)

    ls = attenuation.LinearSolid.invert_linear_solids(N=2, freq_weight=False,
                                                      exact=True, Q=1e9)

    w_j_ref = np.array([0.02756839, 1.43198512])
    y_j_ref = np.array([2.66302747, 2.66302524]) / 1e9

    np.testing.assert_allclose(w_j_ref, ls.w_j, atol=1e-9)
    np.testing.assert_allclose(y_j_ref, ls.y_j, atol=1e-9)

    ls = attenuation.LinearSolid.invert_linear_solids(N=4, freq_weight=False,
                                                      exact=True, Q=10.)

    w_j_ref = np.array([0.0089472, 0.07693113, 0.58383746, 5.22271609])
    y_j_ref = np.array([0.17987619, 0.16239703, 0.18492229, 0.28624039])

    np.testing.assert_allclose(w_j_ref, ls.w_j, atol=1e-9)
    np.testing.assert_allclose(y_j_ref, ls.y_j, atol=1e-9)

    ls = attenuation.LinearSolid.invert_linear_solids(N=5, freq_weight=False)

    w_j_ref = np.array([6.09316735e-03, 3.86633288e-02, 1.98696898e-01,
                        1.02110647e+00, 6.47912101e+00])
    y_j_ref = np.array([1.55016419, 1.05459902, 1.03783409, 1.05457329,
                        1.55015799])

    np.testing.assert_allclose(w_j_ref, ls.w_j, rtol=1e-4)
    np.testing.assert_allclose(y_j_ref, ls.y_j, rtol=1e-4)

    ls = attenuation.LinearSolid.invert_linear_solids(N=3, freq_weight=True)

    w_j_ref = np.array([0.03198043, 0.54416118, 5.30825005])
    y_j_ref = np.array([2.30269669, 1.50429431, 1.67581451])

    np.testing.assert_allclose(w_j_ref, ls.w_j, rtol=1e-5)
    np.testing.assert_allclose(y_j_ref, ls.y_j, rtol=1e-5)

    ls = attenuation.LinearSolid.invert_linear_solids(N=3, alpha=0.4,
                                                      freq_weight=False)

    w_j_ref = np.array([0.00793376, 0.13745404, 2.07044628])
    y_j_ref = np.array([27.6227175, 6.37360887, 2.31038753])

    np.testing.assert_allclose(w_j_ref, ls.w_j, rtol=1e-4)
    np.testing.assert_allclose(y_j_ref, ls.y_j, rtol=1e-4)


@pytest.mark.mpl_image_compare(baseline_dir='data/mpl_baseline', tolerance=20,
                               savefig_kwargs={'dpi': 50})
def test_plot_linea_solids():
    ls = attenuation.LinearSolid.invert_linear_solids(N=2, freq_weight=False)
    return ls.plot(show=False)