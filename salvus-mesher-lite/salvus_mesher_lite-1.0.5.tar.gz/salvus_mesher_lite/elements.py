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

# some element definitions according to the exodus standard (indexes starting
# at 0 though in contrast to the exodus documentation)

QUAD_EDGES = [(0, 1), (1, 2), (2, 3), (3, 0)]

QUAD_SIDE_SET_MASK = [np.zeros(4, dtype='bool') for _ in range(4)]
QUAD_SIDE_SET_MASK[0][[0, 1]] = True
QUAD_SIDE_SET_MASK[1][[1, 2]] = True
QUAD_SIDE_SET_MASK[2][[2, 3]] = True
QUAD_SIDE_SET_MASK[3][[3, 0]] = True

QUAD8_SIDE_SET_MASK = [np.zeros(8, dtype='bool') for _ in range(4)]
QUAD8_SIDE_SET_MASK[0][[0, 1, 4]] = True
QUAD8_SIDE_SET_MASK[1][[1, 2, 5]] = True
QUAD8_SIDE_SET_MASK[2][[2, 3, 6]] = True
QUAD8_SIDE_SET_MASK[3][[3, 0, 7]] = True

QUAD_ANGLES = [(3, 0, 1), (0, 1, 2), (1, 2, 3), (2, 3, 0)]

QUAD_PLOT_LINE = np.array([0, 1, 2, 3])
QUAD8_PLOT_LINE = np.array([0, 4, 1, 5, 2, 6, 3, 7])

QUAD_TO_4QUAD = [[0, 4, 8, 7],
                 [4, 1, 5, 8],
                 [8, 5, 2, 6],
                 [7, 8, 6, 3]]


# easy access via ndim and nodes_per_element
name = {(2, 4): 'QUAD',
        (2, 8): 'QUAD',
        (2, 9): 'QUAD',
        }

edges = {(2, 4): QUAD_EDGES,
         (2, 8): QUAD_EDGES,
         (2, 9): QUAD_EDGES,
         }

facets = {(2, 4): QUAD_EDGES,
          (2, 8): QUAD_EDGES,
          (2, 9): QUAD_EDGES,
          }


side_set_mask = {(2, 4): QUAD_SIDE_SET_MASK,
                 }

angles = {(2, 4): QUAD_ANGLES,
          }

theta_e = {(2, 4): np.pi / 2,
           }

plot_line = {
    (2, 4): QUAD_PLOT_LINE,
    (2, 8): QUAD8_PLOT_LINE,
    (2, 9): QUAD8_PLOT_LINE,
}