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

from ..global_numbering import get_global_lexi


def test_get_global_lexi():
    ref_index = np.array([1, 2, 1, 2, 0, 1, 0])

    points = np.array([[0., 1., 0., 1., 0., 0., 0.],
                       [1., 3., 1., 3., 0., 1., 0.]])
    index, nglob = get_global_lexi(points, tolerance_decimals=8)

    assert nglob == 3
    np.testing.assert_equal(index, ref_index)

    points = np.array([[0., 1., 0., 1., 0., 0., 0.],
                       [1., 3., 1., 3., 0., 1., 0.],
                       [2., 3., 2., 3., 0., 2., 0.]])
    index, nglob = get_global_lexi(points, tolerance_decimals=8)

    assert nglob == 3
    np.testing.assert_equal(index, ref_index)