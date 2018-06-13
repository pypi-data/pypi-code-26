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
from __future__ import absolute_import, division, print_function

import ctypes as C
import glob
import inspect
import os

import numpy as np


LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))), "lib")

cache = []


def load_lib():
    if cache:  # pragma: no cover
        return cache[0]
    else:
        # Enable a couple of different library naming schemes.
        possible_files = glob.glob(os.path.join(LIB_DIR, "salvus_mesher_lite*.so"))
        if not possible_files:  # pragma: no cover
            raise ValueError("Could not find suitable salvus_mesher_lite shared "
                             "library.")
        filename = possible_files[0]
        lib = C.CDLL(filename)

        # A couple of definitions.
        lib.lexsort_internal_loop.restype = C.c_void_p
        lib.lexsort_internal_loop.argtypes = [
            C.c_int,
            C.c_int,
            C.c_long,
            np.ctypeslib.ndpointer(dtype=np.float64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=1,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=1,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=1,
                                   flags=['C_CONTIGUOUS']),
            C.c_long]

        lib.hmin.restype = C.c_void_p
        lib.hmin.argtypes = [
            C.c_int,
            C.c_int,
            C.c_int,
            C.c_int,
            C.c_int,
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.float64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.float64, ndim=1,
                                   flags=['C_CONTIGUOUS'])]

        lib.hmax.restype = C.c_void_p
        lib.hmax.argtypes = [
            C.c_int,
            C.c_int,
            C.c_int,
            C.c_int,
            C.c_int,
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.float64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.float64, ndim=1,
                                   flags=['C_CONTIGUOUS'])]

        lib.facets.restype = C.c_void_p
        lib.facets.argtypes = [
            C.c_int,
            C.c_int,
            C.c_int,
            C.c_int,
            C.c_int,
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=2,
                                   flags=['C_CONTIGUOUS'])]

        lib.centroid.restype = C.c_void_p
        lib.centroid.argtypes = [
            C.c_int,
            C.c_int,
            C.c_int,
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.float64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.float64, ndim=2,
                                   flags=['C_CONTIGUOUS'])]

        lib.angle.restype = C.c_void_p
        lib.angle.argtypes = [
            C.c_int,
            C.c_int,
            C.c_int,
            C.c_int,
            C.c_int,
            C.c_int,
            np.ctypeslib.ndpointer(dtype=np.int64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.float64, ndim=2,
                                   flags=['C_CONTIGUOUS']),
            np.ctypeslib.ndpointer(dtype=np.float64, ndim=1,
                                   flags=['C_CONTIGUOUS'])]


        cache.append(lib)
        return lib