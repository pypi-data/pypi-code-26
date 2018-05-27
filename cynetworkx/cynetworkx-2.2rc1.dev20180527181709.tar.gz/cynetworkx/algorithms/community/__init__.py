"""Functions for computing and measuring community structure.

The functions in this class are not imported into the top-level
:mod:`cynetworkx` namespace. You can access these functions by importing
the :mod:`cynetworkx.algorithms.community` module, then accessing the
functions as attributes of ``community``. For example::

    >>> import cynetworkx as nx
    >>> from cynetworkx.algorithms import community
    >>> G = nx.barbell_graph(5, 1)
    >>> communities_generator = community.girvan_newman(G)
    >>> top_level_communities = next(communities_generator)
    >>> next_level_communities = next(communities_generator)
    >>> sorted(map(sorted, next_level_communities))
    [[0, 1, 2, 3, 4], [5], [6, 7, 8, 9, 10]]

"""
from cynetworkx.algorithms.community.asyn_fluidc import *
from cynetworkx.algorithms.community.centrality import *
from cynetworkx.algorithms.community.community_generators import *
from cynetworkx.algorithms.community.kclique import *
from cynetworkx.algorithms.community.kernighan_lin import *
from cynetworkx.algorithms.community.label_propagation import *
from cynetworkx.algorithms.community.modularity_max import *
from cynetworkx.algorithms.community.quality import *
from cynetworkx.algorithms.community.community_utils import *
