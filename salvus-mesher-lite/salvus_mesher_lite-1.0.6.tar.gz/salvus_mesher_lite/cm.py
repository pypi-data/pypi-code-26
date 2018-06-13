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
from matplotlib.colors import LinearSegmentedColormap

# for quality plots
cdict_quality = {
    'red': ((0.0, 1.0, 1.0),
            (0.4, 1.0, 0.0),
            (0.6, 0.0, 0.0),
            (0.8, 0.0, 1.0),
            (0.9, 1.0, 1.0),
            (1.0, 1.0, 1.0)),
    'green': ((0.0, 1.0, 1.0),
              (0.4, 1.0, 1.0),
              (0.6, 1.0, 0.5),
              (0.8, 0.5, 0.5),
              (0.9, 0.5, 0.0),
              (1.0, 0.0, 0.0)),
    'blue': ((0.0, 0.0, 0.0),
             (0.4, 0.0, 0.0),
             (0.6, 0.0, 0.0),
             (0.8, 0.0, 0.0),
             (0.9, 0.0, 0.0),
             (1.0, 0.0, 0.0))}

cmap_quality = LinearSegmentedColormap('cmap_quality', cdict_quality, 1024)

# a purely white cmap, as I could not figure out how to make all masked
# elements white in pcolor otherwise
cdict_white = {
    'red': ((0.0, 1.0, 1.0),
            (1.0, 1.0, 1.0)),
    'green': ((0.0, 1.0, 1.0),
              (1.0, 1.0, 1.0)),
    'blue': ((0.0, 1.0, 1.0),
             (1.0, 1.0, 1.0))}

cmap_white = LinearSegmentedColormap('cmap_white', cdict_white, 1024)