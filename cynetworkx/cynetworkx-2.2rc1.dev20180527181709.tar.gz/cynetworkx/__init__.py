"""
cyNetworkX
========

cyNetworkX is a Cython port of the NetworkX package for the creation, manipulation, and
study of the structure, dynamics, and functions of complex networks.

Website (including documentation)::

    https://github.com/pattern-inc/cynetworkx

Source::

    https://github.com/pattern-inc/cynetworkx

Bug reports::

    https://github.com/pattern-inc/cynetworkx/issues

Simple example
--------------

Find the shortest path between two nodes in an undirected graph::

    >>> import cynetworkx as nx
    >>> G = nx.Graph()
    >>> G.add_edge('A', 'B', weight=4)
    >>> G.add_edge('B', 'D', weight=2)
    >>> G.add_edge('A', 'C', weight=3)
    >>> G.add_edge('C', 'D', weight=4)
    >>> nx.shortest_path(G, 'A', 'D', weight='weight')
    ['A', 'B', 'D']

Bugs
----

Please report any bugs that you find `here <https://github.com/pattern-inc/cynetworkx/issues>`_.
Or, even better, fork the repository on GitHub and create a pull request (PR).

License
-------

Released under the Apache 2.0 license

"""
# Add platform dependent shared library path to sys.path
#

from __future__ import absolute_import

import sys
if sys.version_info[:2] < (2, 7):
    m = "Python 2.7 or later is required for NetworkX (%d.%d detected)."
    raise ImportError(m % sys.version_info[:2])
del sys

# Release data
from cynetworkx import release

__author__ = '%s <%s>' % (release.authors['Pattern, Inc.'])
__license__ = release.license

__date__ = release.date
__version__ = release.version


# These are import orderwise
from cynetworkx.exception import *
import cynetworkx.utils

import cynetworkx.classes.filters
import cynetworkx.classes
from cynetworkx.classes import *

import cynetworkx.convert
from cynetworkx.convert import *

import cynetworkx.convert_matrix
from cynetworkx.convert_matrix import *


import cynetworkx.relabel
from cynetworkx.relabel import *

import cynetworkx.generators
from cynetworkx.generators import *

import cynetworkx.readwrite
from cynetworkx.readwrite import *

# Need to test with SciPy, when available
import cynetworkx.algorithms
from cynetworkx.algorithms import *
import cynetworkx.linalg

from cynetworkx.linalg import *
from cynetworkx.tests.test import run as test

import cynetworkx.drawing
from cynetworkx.drawing import *
