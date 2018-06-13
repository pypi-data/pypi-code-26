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
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import ctypes as C
import numpy as np

from .helpers import load_lib


lib = load_lib()


def connectivity_2D(nelem_x, nelem_y):

    connectivity = np.zeros((nelem_x * nelem_y, 4), dtype='int')

    lib.connectivity_2D(C.c_int(nelem_x), C.c_int(nelem_y),
                        connectivity.ctypes.data_as(C.POINTER(C.c_longlong)))

    return connectivity


def connectivity_3D(nelem_x, nelem_y, nelem_z):
    raise ValueError('This feature is not included in the free SalvusMesher version.')