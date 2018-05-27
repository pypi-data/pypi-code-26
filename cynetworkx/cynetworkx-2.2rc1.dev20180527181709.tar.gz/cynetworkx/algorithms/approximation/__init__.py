# __init__.py - package containing heuristics for optimization problems
#
# Copyright 2016-2018 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Approximations of graph properties and Heuristic functions for optimization
problems.

    .. warning:: The approximation submodule is not imported in the top-level
        ``cynetworkx``.

    These functions can be imported with
    ``from cynetworkx.algorithms import approximation``.

"""

from cynetworkx.algorithms.approximation.clustering_coefficient import *
from cynetworkx.algorithms.approximation.clique import *
from cynetworkx.algorithms.approximation.connectivity import *
from cynetworkx.algorithms.approximation.dominating_set import *
from cynetworkx.algorithms.approximation.kcomponents import *
from cynetworkx.algorithms.approximation.independent_set import *
from cynetworkx.algorithms.approximation.matching import *
from cynetworkx.algorithms.approximation.ramsey import *
from cynetworkx.algorithms.approximation.steinertree import *
from cynetworkx.algorithms.approximation.vertex_cover import *
