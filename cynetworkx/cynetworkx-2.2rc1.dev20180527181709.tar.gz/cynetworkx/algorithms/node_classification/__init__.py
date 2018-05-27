""" This module provides the functions for node classification problem.

The functions in this module are not imported
into the top level `cynetworkx` namespace.
You can access these functions by importing
the `cynetworkx.algorithms.node_classification` modules,
then accessing the functions as attributes of `node_classification`.
For example:

  >>> import cynetworkx as nx
  >>> from cynetworkx.algorithms import node_classification
  >>> G = nx.path_graph(4)
  >>> G.edges()
  EdgeView([(0, 1), (1, 2), (2, 3)])
  >>> G.node[0]['label'] = 'A'
  >>> G.node[3]['label'] = 'B'
  >>> node_classification.harmonic_function(G)  # doctest: +SKIP
  ['A', 'A', 'B', 'B']

"""

from cynetworkx.algorithms.node_classification.hmn import *
from cynetworkx.algorithms.node_classification.lgc import *
