#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for cynetworkx

You can install cynetworkx with

python setup.py install
"""
from glob import glob
import os
import sys
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

if sys.argv[-1] == 'setup.py':
    print("To install, run 'python setup.py install'")
    print()

if sys.version_info[:2] < (2, 7):
    print("NetworkX requires Python 2.7 or later (%d.%d detected)." %
          sys.version_info[:2])
    sys.exit(-1)

# Write the version information.
sys.path.insert(0, 'cynetworkx')
import cynetworkx.release as release
version = release.write_versionfile()
sys.path.pop(0)

extensions = [
    Extension("cynetworkx.algorithms.approximation.__init__", ["cynetworkx/algorithms/approximation/__init__.py"]),
    Extension("cynetworkx.algorithms.approximation.clique", ["cynetworkx/algorithms/approximation/clique.py"]),
    Extension("cynetworkx.algorithms.approximation.clustering_coefficient", ["cynetworkx/algorithms/approximation/clustering_coefficient.py"]),
    Extension("cynetworkx.algorithms.approximation.connectivity", ["cynetworkx/algorithms/approximation/connectivity.py"]),
    Extension("cynetworkx.algorithms.approximation.dominating_set", ["cynetworkx/algorithms/approximation/dominating_set.py"]),
    Extension("cynetworkx.algorithms.approximation.independent_set", ["cynetworkx/algorithms/approximation/independent_set.py"]),
    Extension("cynetworkx.algorithms.approximation.kcomponents", ["cynetworkx/algorithms/approximation/kcomponents.py"]),
    Extension("cynetworkx.algorithms.approximation.matching", ["cynetworkx/algorithms/approximation/matching.py"]),
    Extension("cynetworkx.algorithms.approximation.ramsey", ["cynetworkx/algorithms/approximation/ramsey.py"]),
    Extension("cynetworkx.algorithms.approximation.steinertree", ["cynetworkx/algorithms/approximation/steinertree.py"]),
    Extension("cynetworkx.algorithms.approximation.vertex_cover", ["cynetworkx/algorithms/approximation/vertex_cover.py"]),

    Extension("cynetworkx.algorithms.assortativity.__init__", ["cynetworkx/algorithms/assortativity/__init__.py"]),
    Extension("cynetworkx.algorithms.assortativity.connectivity", ["cynetworkx/algorithms/assortativity/connectivity.py"]),
    Extension("cynetworkx.algorithms.assortativity.correlation", ["cynetworkx/algorithms/assortativity/correlation.py"]),
    Extension("cynetworkx.algorithms.assortativity.mixing", ["cynetworkx/algorithms/assortativity/mixing.py"]),
    Extension("cynetworkx.algorithms.assortativity.neighbor_degree", ["cynetworkx/algorithms/assortativity/neighbor_degree.py"]),
    Extension("cynetworkx.algorithms.assortativity.pairs", ["cynetworkx/algorithms/assortativity/pairs.py"]),

    Extension("cynetworkx.algorithms.bipartite.__init__", ["cynetworkx/algorithms/bipartite/__init__.py"]),
    Extension("cynetworkx.algorithms.bipartite.basic", ["cynetworkx/algorithms/bipartite/basic.py"]),
    Extension("cynetworkx.algorithms.bipartite.centrality", ["cynetworkx/algorithms/bipartite/centrality.py"]),
    Extension("cynetworkx.algorithms.bipartite.cluster", ["cynetworkx/algorithms/bipartite/cluster.py"]),
    Extension("cynetworkx.algorithms.bipartite.covering", ["cynetworkx/algorithms/bipartite/covering.py"]),
    Extension("cynetworkx.algorithms.bipartite.edgelist", ["cynetworkx/algorithms/bipartite/edgelist.py"]),
    Extension("cynetworkx.algorithms.bipartite.generators", ["cynetworkx/algorithms/bipartite/generators.py"]),
    Extension("cynetworkx.algorithms.bipartite.matching", ["cynetworkx/algorithms/bipartite/matching.py"]),
    Extension("cynetworkx.algorithms.bipartite.matrix", ["cynetworkx/algorithms/bipartite/matrix.py"]),
    Extension("cynetworkx.algorithms.bipartite.projection", ["cynetworkx/algorithms/bipartite/projection.py"]),
    Extension("cynetworkx.algorithms.bipartite.redundancy", ["cynetworkx/algorithms/bipartite/redundancy.py"]),
    Extension("cynetworkx.algorithms.bipartite.spectral", ["cynetworkx/algorithms/bipartite/spectral.py"]),

    Extension("cynetworkx.algorithms.centrality.__init__", ["cynetworkx/algorithms/centrality/__init__.py"]),
    Extension("cynetworkx.algorithms.centrality.betweenness", ["cynetworkx/algorithms/centrality/betweenness.py"]),
    Extension("cynetworkx.algorithms.centrality.betweenness_subset", ["cynetworkx/algorithms/centrality/betweenness_subset.py"]),
    Extension("cynetworkx.algorithms.centrality.closeness", ["cynetworkx/algorithms/centrality/closeness.py"]),
    Extension("cynetworkx.algorithms.centrality.current_flow_betweenness", ["cynetworkx/algorithms/centrality/current_flow_betweenness.py"]),
    Extension("cynetworkx.algorithms.centrality.current_flow_betweenness_subset", ["cynetworkx/algorithms/centrality/current_flow_betweenness_subset.py"]),
    Extension("cynetworkx.algorithms.centrality.current_flow_closeness", ["cynetworkx/algorithms/centrality/current_flow_closeness.py"]),
    Extension("cynetworkx.algorithms.centrality.degree_alg", ["cynetworkx/algorithms/centrality/degree_alg.py"]),
    Extension("cynetworkx.algorithms.centrality.dispersion", ["cynetworkx/algorithms/centrality/dispersion.py"]),
    Extension("cynetworkx.algorithms.centrality.eigenvector", ["cynetworkx/algorithms/centrality/eigenvector.py"]),
    Extension("cynetworkx.algorithms.centrality.flow_matrix", ["cynetworkx/algorithms/centrality/flow_matrix.py"]),
    Extension("cynetworkx.algorithms.centrality.harmonic", ["cynetworkx/algorithms/centrality/harmonic.py"]),
    Extension("cynetworkx.algorithms.centrality.katz", ["cynetworkx/algorithms/centrality/katz.py"]),
    Extension("cynetworkx.algorithms.centrality.load", ["cynetworkx/algorithms/centrality/load.py"]),
    Extension("cynetworkx.algorithms.centrality.reaching", ["cynetworkx/algorithms/centrality/reaching.py"]),
    Extension("cynetworkx.algorithms.centrality.subgraph_alg", ["cynetworkx/algorithms/centrality/subgraph_alg.py"]),

    Extension("cynetworkx.algorithms.coloring.__init__", ["cynetworkx/algorithms/coloring/__init__.py"]),
    Extension("cynetworkx.algorithms.coloring.greedy_coloring", ["cynetworkx/algorithms/coloring/greedy_coloring.py"]),
    Extension("cynetworkx.algorithms.coloring.greedy_coloring_with_interchange", ["cynetworkx/algorithms/coloring/greedy_coloring_with_interchange.py"]),

    Extension("cynetworkx.algorithms.community.__init__", ["cynetworkx/algorithms/community/__init__.py"]),
    Extension("cynetworkx.algorithms.community.asyn_fluidc", ["cynetworkx/algorithms/community/asyn_fluidc.py"]),
    Extension("cynetworkx.algorithms.community.centrality", ["cynetworkx/algorithms/community/centrality.py"]),
    Extension("cynetworkx.algorithms.community.community_generators", ["cynetworkx/algorithms/community/community_generators.py"]),
    Extension("cynetworkx.algorithms.community.community_utils", ["cynetworkx/algorithms/community/community_utils.py"]),
    Extension("cynetworkx.algorithms.community.kclique", ["cynetworkx/algorithms/community/kclique.py"]),
    Extension("cynetworkx.algorithms.community.kernighan_lin", ["cynetworkx/algorithms/community/kernighan_lin.py"]),
    Extension("cynetworkx.algorithms.community.label_propagation", ["cynetworkx/algorithms/community/label_propagation.py"]),
    Extension("cynetworkx.algorithms.community.quality", ["cynetworkx/algorithms/community/quality.py"]),

    Extension("cynetworkx.algorithms.components.__init__", ["cynetworkx/algorithms/components/__init__.py"]),
    Extension("cynetworkx.algorithms.components.attracting", ["cynetworkx/algorithms/components/attracting.py"]),
    Extension("cynetworkx.algorithms.components.biconnected", ["cynetworkx/algorithms/components/biconnected.py"]),
    Extension("cynetworkx.algorithms.components.connected", ["cynetworkx/algorithms/components/connected.py"]),
    Extension("cynetworkx.algorithms.components.semiconnected", ["cynetworkx/algorithms/components/semiconnected.py"]),
    Extension("cynetworkx.algorithms.components.strongly_connected", ["cynetworkx/algorithms/components/strongly_connected.py"]),
    Extension("cynetworkx.algorithms.components.weakly_connected", ["cynetworkx/algorithms/components/weakly_connected.py"]),

    Extension("cynetworkx.algorithms.connectivity.__init__", ["cynetworkx/algorithms/connectivity/__init__.py"]),
    Extension("cynetworkx.algorithms.connectivity.connectivity", ["cynetworkx/algorithms/connectivity/connectivity.py"]),
    Extension("cynetworkx.algorithms.connectivity.cuts", ["cynetworkx/algorithms/connectivity/cuts.py"]),
    Extension("cynetworkx.algorithms.connectivity.disjoint_paths", ["cynetworkx/algorithms/connectivity/disjoint_paths.py"]),
    Extension("cynetworkx.algorithms.connectivity.edge_augmentation", ["cynetworkx/algorithms/connectivity/edge_augmentation.py"]),
    Extension("cynetworkx.algorithms.connectivity.edge_kcomponents", ["cynetworkx/algorithms/connectivity/edge_kcomponents.py"]),
    Extension("cynetworkx.algorithms.connectivity.kcomponents", ["cynetworkx/algorithms/connectivity/kcomponents.py"]),
    Extension("cynetworkx.algorithms.connectivity.kcutsets", ["cynetworkx/algorithms/connectivity/kcutsets.py"]),
    Extension("cynetworkx.algorithms.connectivity.stoerwagner", ["cynetworkx/algorithms/connectivity/stoerwagner.py"]),
    Extension("cynetworkx.algorithms.connectivity.utils", ["cynetworkx/algorithms/connectivity/utils.py"]),

    Extension("cynetworkx.algorithms.flow.__init__", ["cynetworkx/algorithms/flow/__init__.py"]),
    Extension("cynetworkx.algorithms.flow.boykovkolmogorov", ["cynetworkx/algorithms/flow/boykovkolmogorov.py"]),
    Extension("cynetworkx.algorithms.flow.capacityscaling", ["cynetworkx/algorithms/flow/capacityscaling.py"]),
    Extension("cynetworkx.algorithms.flow.dinitz_alg", ["cynetworkx/algorithms/flow/dinitz_alg.py"]),
    Extension("cynetworkx.algorithms.flow.edmondskarp", ["cynetworkx/algorithms/flow/edmondskarp.py"]),
    Extension("cynetworkx.algorithms.flow.gomory_hu", ["cynetworkx/algorithms/flow/gomory_hu.py"]),
    Extension("cynetworkx.algorithms.flow.maxflow", ["cynetworkx/algorithms/flow/maxflow.py"]),
    Extension("cynetworkx.algorithms.flow.mincost", ["cynetworkx/algorithms/flow/mincost.py"]),
    Extension("cynetworkx.algorithms.flow.networksimplex", ["cynetworkx/algorithms/flow/networksimplex.py"]),
    Extension("cynetworkx.algorithms.flow.preflowpush", ["cynetworkx/algorithms/flow/preflowpush.py"]),
    Extension("cynetworkx.algorithms.flow.shortestaugmentingpath", ["cynetworkx/algorithms/flow/shortestaugmentingpath.py"]),
    Extension("cynetworkx.algorithms.flow.utils", ["cynetworkx/algorithms/flow/utils.py"]),

    Extension("cynetworkx.algorithms.isomorphism.__init__", ["cynetworkx/algorithms/isomorphism/__init__.py"]),
    Extension("cynetworkx.algorithms.isomorphism.isomorph", ["cynetworkx/algorithms/isomorphism/isomorph.py"]),
    Extension("cynetworkx.algorithms.isomorphism.isomorphvf2", ["cynetworkx/algorithms/isomorphism/isomorphvf2.py"]),
    Extension("cynetworkx.algorithms.isomorphism.matchhelpers", ["cynetworkx/algorithms/isomorphism/matchhelpers.py"]),
    Extension("cynetworkx.algorithms.isomorphism.temporalisomorphvf2", ["cynetworkx/algorithms/isomorphism/temporalisomorphvf2.py"]),
    Extension("cynetworkx.algorithms.isomorphism.vf2userfunc", ["cynetworkx/algorithms/isomorphism/vf2userfunc.py"]),

    Extension("cynetworkx.algorithms.link_analysis.__init__", ["cynetworkx/algorithms/link_analysis/__init__.py"]),
    Extension("cynetworkx.algorithms.link_analysis.hits_alg", ["cynetworkx/algorithms/link_analysis/hits_alg.py"]),
    Extension("cynetworkx.algorithms.link_analysis.pagerank_alg", ["cynetworkx/algorithms/link_analysis/pagerank_alg.py"]),

    Extension("cynetworkx.algorithms.operators.__init__", ["cynetworkx/algorithms/operators/__init__.py"]),
    Extension("cynetworkx.algorithms.operators.all", ["cynetworkx/algorithms/operators/all.py"]),
    Extension("cynetworkx.algorithms.operators.binary", ["cynetworkx/algorithms/operators/binary.py"]),
    Extension("cynetworkx.algorithms.operators.product", ["cynetworkx/algorithms/operators/product.py"]),
    Extension("cynetworkx.algorithms.operators.unary", ["cynetworkx/algorithms/operators/unary.py"]),

    Extension("cynetworkx.algorithms.shortest_paths.__init__", ["cynetworkx/algorithms/shortest_paths/__init__.py"]),
    Extension("cynetworkx.algorithms.shortest_paths.astar", ["cynetworkx/algorithms/shortest_paths/astar.py"]),
    Extension("cynetworkx.algorithms.shortest_paths.dense", ["cynetworkx/algorithms/shortest_paths/dense.py"]),
    Extension("cynetworkx.algorithms.shortest_paths.generic", ["cynetworkx/algorithms/shortest_paths/generic.py"]),
    Extension("cynetworkx.algorithms.shortest_paths.unweighted", ["cynetworkx/algorithms/shortest_paths/unweighted.py"]),
    Extension("cynetworkx.algorithms.shortest_paths.weighted", ["cynetworkx/algorithms/shortest_paths/weighted.py"]),

    Extension("cynetworkx.algorithms.traversal.__init__", ["cynetworkx/algorithms/traversal/__init__.py"]),
    Extension("cynetworkx.algorithms.traversal.beamsearch", ["cynetworkx/algorithms/traversal/beamsearch.py"]),
    Extension("cynetworkx.algorithms.traversal.breadth_first_search", ["cynetworkx/algorithms/traversal/breadth_first_search.py"]),
    Extension("cynetworkx.algorithms.traversal.depth_first_search", ["cynetworkx/algorithms/traversal/depth_first_search.py"]),
    Extension("cynetworkx.algorithms.traversal.edgedfs", ["cynetworkx/algorithms/traversal/edgedfs.py"]),

    Extension("cynetworkx.algorithms.tree.__init__", ["cynetworkx/algorithms/tree/__init__.py"]),
    Extension("cynetworkx.algorithms.tree.branchings", ["cynetworkx/algorithms/tree/branchings.py"]),
    Extension("cynetworkx.algorithms.tree.coding", ["cynetworkx/algorithms/tree/coding.py"]),
    Extension("cynetworkx.algorithms.tree.mst", ["cynetworkx/algorithms/tree/mst.py"]),
    Extension("cynetworkx.algorithms.tree.operations", ["cynetworkx/algorithms/tree/operations.py"]),
    Extension("cynetworkx.algorithms.tree.recognition", ["cynetworkx/algorithms/tree/recognition.py"]),

    Extension("cynetworkx.algorithms.__init__", ["cynetworkx/algorithms/__init__.py"]),
    Extension("cynetworkx.algorithms.boundary", ["cynetworkx/algorithms/boundary.py"]),
    Extension("cynetworkx.algorithms.bridges", ["cynetworkx/algorithms/bridges.py"]),
    Extension("cynetworkx.algorithms.chains", ["cynetworkx/algorithms/chains.py"]),
    Extension("cynetworkx.algorithms.chordal", ["cynetworkx/algorithms/chordal.py"]),
    Extension("cynetworkx.algorithms.clique", ["cynetworkx/algorithms/clique.py"]),
    Extension("cynetworkx.algorithms.cluster", ["cynetworkx/algorithms/cluster.py"]),
    Extension("cynetworkx.algorithms.communicability_alg", ["cynetworkx/algorithms/communicability_alg.py"]),
    Extension("cynetworkx.algorithms.core", ["cynetworkx/algorithms/core.py"]),
    Extension("cynetworkx.algorithms.covering", ["cynetworkx/algorithms/covering.py"]),
    Extension("cynetworkx.algorithms.cuts", ["cynetworkx/algorithms/cuts.py"]),
    Extension("cynetworkx.algorithms.cycles", ["cynetworkx/algorithms/cycles.py"]),
    Extension("cynetworkx.algorithms.dag", ["cynetworkx/algorithms/dag.py"]),
    Extension("cynetworkx.algorithms.distance_measures", ["cynetworkx/algorithms/distance_measures.py"]),
    Extension("cynetworkx.algorithms.distance_regular", ["cynetworkx/algorithms/distance_regular.py"]),
    Extension("cynetworkx.algorithms.dominance", ["cynetworkx/algorithms/dominance.py"]),
    Extension("cynetworkx.algorithms.domninating", ["cynetworkx/algorithms/dominating.py"]),
    Extension("cynetworkx.algorithms.efficiency", ["cynetworkx/algorithms/efficiency.py"]),
    Extension("cynetworkx.algorithms.euler", ["cynetworkx/algorithms/euler.py"]),
    Extension("cynetworkx.algorithms.graphical", ["cynetworkx/algorithms/graphical.py"]),
    Extension("cynetworkx.algorithms.hierarchy", ["cynetworkx/algorithms/hierarchy.py"]),
    Extension("cynetworkx.algorithms.hybrid", ["cynetworkx/algorithms/hybrid.py"]),
    Extension("cynetworkx.algorithms.isolate", ["cynetworkx/algorithms/isolate.py"]),
    Extension("cynetworkx.algorithms.link_prediction", ["cynetworkx/algorithms/link_prediction.py"]),
    Extension("cynetworkx.algorithms.lowest_common_ancestors", ["cynetworkx/algorithms/lowest_common_ancestors.py"]),
    Extension("cynetworkx.algorithms.matching", ["cynetworkx/algorithms/matching.py"]),
    Extension("cynetworkx.algorithms.minors", ["cynetworkx/algorithms/minors.py"]),
    Extension("cynetworkx.algorithms.mis", ["cynetworkx/algorithms/mis.py"]),
    Extension("cynetworkx.algorithms.reciprocity", ["cynetworkx/algorithms/reciprocity.py"]),
    Extension("cynetworkx.algorithms.richclub", ["cynetworkx/algorithms/richclub.py"]),
    Extension("cynetworkx.algorithms.similarity", ["cynetworkx/algorithms/similarity.py"]),
    Extension("cynetworkx.algorithms.simple_paths", ["cynetworkx/algorithms/simple_paths.py"]),
    Extension("cynetworkx.algorithms.smetric", ["cynetworkx/algorithms/smetric.py"]),
    Extension("cynetworkx.algorithms.structuralholes", ["cynetworkx/algorithms/structuralholes.py"]),
    Extension("cynetworkx.algorithms.swap", ["cynetworkx/algorithms/swap.py"]),
    Extension("cynetworkx.algorithms.threshold", ["cynetworkx/algorithms/threshold.py"]),
    Extension("cynetworkx.algorithms.tournament", ["cynetworkx/algorithms/tournament.py"]),
    Extension("cynetworkx.algorithms.triads", ["cynetworkx/algorithms/triads.py"]),
    Extension("cynetworkx.algorithms.vitality", ["cynetworkx/algorithms/vitality.py"]),
    Extension("cynetworkx.algorithms.voronoi", ["cynetworkx/algorithms/voronoi.py"]),
    Extension("cynetworkx.algorithms.weiner", ["cynetworkx/algorithms/wiener.py"]),

    Extension("cynetworkx.classes.__init__", ["cynetworkx/classes/__init__.py"]),
    Extension("cynetworkx.classes.coreviews", ["cynetworkx/classes/coreviews.py"]),
    Extension("cynetworkx.classes.digraph", ["cynetworkx/classes/digraph.py"]),
    Extension("cynetworkx.classes.filters", ["cynetworkx/classes/filters.py"]),
    Extension("cynetworkx.classes.function", ["cynetworkx/classes/function.py"]),
    Extension("cynetworkx.classes.graph", ["cynetworkx/classes/graph.py"]),
    Extension("cynetworkx.classes.graphviews", ["cynetworkx/classes/graphviews.py"]),
    Extension("cynetworkx.classes.multidigraph", ["cynetworkx/classes/multidigraph.py"]),
    Extension("cynetworkx.classes.multigraph", ["cynetworkx/classes/multigraph.py"]),
    Extension("cynetworkx.classes.ordered", ["cynetworkx/classes/ordered.py"]),
    Extension("cynetworkx.classes.reportviews", ["cynetworkx/classes/reportviews.py"]),

    Extension("cynetworkx.utils.__init__", ["cynetworkx/utils/__init__.py"]),
    Extension("cynetworkx.utils.contextmanagers", ["cynetworkx/utils/contextmanagers.py"]),
    Extension("cynetworkx.utils.decorators", ["cynetworkx/utils/decorators.py"]),
    Extension("cynetworkx.utils.heaps", ["cynetworkx/utils/heaps.py"]),
    Extension("cynetworkx.utils.misc", ["cynetworkx/utils/misc.py"]),
    Extension("cynetworkx.utils.random_sequence", ["cynetworkx/utils/random_sequence.py"]),
    Extension("cynetworkx.utils.rcm", ["cynetworkx/utils/rcm.py"]),
    Extension("cynetworkx.utils.union_find", ["cynetworkx/utils/union_find.py"]),

    Extension("cynetworkx.drawing.__init__", ["cynetworkx/drawing/__init__.py"]),
    Extension("cynetworkx.drawing.layout", ["cynetworkx/drawing/layout.py"]),
    Extension("cynetworkx.drawing.nx_agraph", ["cynetworkx/drawing/nx_agraph.py"]),
    Extension("cynetworkx.drawing.nx_pydot", ["cynetworkx/drawing/nx_pydot.py"]),
    Extension("cynetworkx.drawing.nx_pylab", ["cynetworkx/drawing/nx_pylab.py"]),

    Extension("cynetworkx.generators.__init__", ["cynetworkx/generators/__init__.py"]),
    Extension("cynetworkx.generators.atlas", ["cynetworkx/generators/atlas.py"]),
    Extension("cynetworkx.generators.classic", ["cynetworkx/generators/classic.py"]),
    Extension("cynetworkx.generators.community", ["cynetworkx/generators/community.py"]),
    Extension("cynetworkx.generators.degree_seq", ["cynetworkx/generators/degree_seq.py"]),
    Extension("cynetworkx.generators.directed", ["cynetworkx/generators/directed.py"]),
    Extension("cynetworkx.generators.duplication", ["cynetworkx/generators/duplication.py"]),
    Extension("cynetworkx.generators.ego", ["cynetworkx/generators/ego.py"]),
    Extension("cynetworkx.generators.expanders", ["cynetworkx/generators/expanders.py"]),
    Extension("cynetworkx.generators.geometric", ["cynetworkx/generators/geometric.py"]),
    Extension("cynetworkx.generators.intersection", ["cynetworkx/generators/intersection.py"]),
    Extension("cynetworkx.generators.joint_degree_seq", ["cynetworkx/generators/joint_degree_seq.py"]),
    Extension("cynetworkx.generators.lattice", ["cynetworkx/generators/lattice.py"]),
    Extension("cynetworkx.generators.line", ["cynetworkx/generators/line.py"]),
    Extension("cynetworkx.generators.mycielski", ["cynetworkx/generators/mycielski.py"]),
    Extension("cynetworkx.generators.nonisomorphic_trees", ["cynetworkx/generators/nonisomorphic_trees.py"]),
    Extension("cynetworkx.generators.random_clustered", ["cynetworkx/generators/random_clustered.py"]),
    Extension("cynetworkx.generators.random_graphs", ["cynetworkx/generators/random_graphs.py"]),
    Extension("cynetworkx.generators.small", ["cynetworkx/generators/small.py"]),
    Extension("cynetworkx.generators.social", ["cynetworkx/generators/social.py"]),
    Extension("cynetworkx.generators.stochastic", ["cynetworkx/generators/stochastic.py"]),
    Extension("cynetworkx.generators.trees", ["cynetworkx/generators/trees.py"]),
    Extension("cynetworkx.generators.triads", ["cynetworkx/generators/triads.py"]),

    Extension("cynetworkx.linalg.__init__", ["cynetworkx/linalg/__init__.py"]),
    Extension("cynetworkx.linalg.algebraicconnectivity", ["cynetworkx/linalg/algebraicconnectivity.py"]),
    Extension("cynetworkx.linalg.attrmatrix", ["cynetworkx/linalg/attrmatrix.py"]),
    Extension("cynetworkx.linalg.graphmatrix", ["cynetworkx/linalg/graphmatrix.py"]),
    Extension("cynetworkx.linalg.laplacianmatrix", ["cynetworkx/linalg/laplacianmatrix.py"]),
    Extension("cynetworkx.linalg.modularitymatrix", ["cynetworkx/linalg/modularitymatrix.py"]),
    Extension("cynetworkx.linalg.spectrum", ["cynetworkx/linalg/spectrum.py"]),

    Extension("cynetworkx.readwrite.json_graph.__init__", ["cynetworkx/readwrite/json_graph/__init__.py"]),
    Extension("cynetworkx.readwrite.json_graph.adjacency", ["cynetworkx/readwrite/json_graph/adjacency.py"]),
    Extension("cynetworkx.readwrite.json_graph.cytoscape", ["cynetworkx/readwrite/json_graph/cytoscape.py"]),
    Extension("cynetworkx.readwrite.json_graph.jit", ["cynetworkx/readwrite/json_graph/jit.py"]),
    Extension("cynetworkx.readwrite.json_graph.node_link", ["cynetworkx/readwrite/json_graph/node_link.py"]),
    Extension("cynetworkx.readwrite.json_graph.tree", ["cynetworkx/readwrite/json_graph/tree.py"]),

    Extension("cynetworkx.readwrite.__init__", ["cynetworkx/readwrite/__init__.py"]),
    Extension("cynetworkx.readwrite.adjlist", ["cynetworkx/readwrite/adjlist.py"]),
    Extension("cynetworkx.readwrite.edgelist", ["cynetworkx/readwrite/edgelist.py"]),
    Extension("cynetworkx.readwrite.gexf", ["cynetworkx/readwrite/gexf.py"]),
    Extension("cynetworkx.readwrite.gml", ["cynetworkx/readwrite/gml.py"]),
    Extension("cynetworkx.readwrite.gpickle", ["cynetworkx/readwrite/gpickle.py"]),
    Extension("cynetworkx.readwrite.graph6", ["cynetworkx/readwrite/graph6.py"]),
    Extension("cynetworkx.readwrite.graphml", ["cynetworkx/readwrite/graphml.py"]),
    Extension("cynetworkx.readwrite.leda", ["cynetworkx/readwrite/leda.py"]),
    Extension("cynetworkx.readwrite.multiline_adjlist", ["cynetworkx/readwrite/multiline_adjlist.py"]),
    Extension("cynetworkx.readwrite.nx_shp", ["cynetworkx/readwrite/nx_shp.py"]),
    Extension("cynetworkx.readwrite.nx_yaml", ["cynetworkx/readwrite/nx_yaml.py"]),
    Extension("cynetworkx.readwrite.p2g", ["cynetworkx/readwrite/p2g.py"]),
    Extension("cynetworkx.readwrite.pajek", ["cynetworkx/readwrite/pajek.py"]),
    Extension("cynetworkx.readwrite.sparse6", ["cynetworkx/readwrite/sparse6.py"]),

    Extension("cynetworkx.__init__", ["cynetworkx/__init__.py"]),
    Extension("cynetworkx.convert", ["cynetworkx/convert.py"]),
    Extension("cynetworkx.convert_matrix", ["cynetworkx/convert_matrix.py"]),
    Extension("cynetworkx.exception", ["cynetworkx/exception.py"]),
    Extension("cynetworkx.relabel", ["cynetworkx/relabel.py"])
]

packages = ["cynetworkx",
            "cynetworkx.algorithms",
            "cynetworkx.algorithms.assortativity",
            "cynetworkx.algorithms.bipartite",
            "cynetworkx.algorithms.node_classification",
            "cynetworkx.algorithms.centrality",
            "cynetworkx.algorithms.community",
            "cynetworkx.algorithms.components",
            "cynetworkx.algorithms.connectivity",
            "cynetworkx.algorithms.coloring",
            "cynetworkx.algorithms.flow",
            "cynetworkx.algorithms.traversal",
            "cynetworkx.algorithms.isomorphism",
            "cynetworkx.algorithms.shortest_paths",
            "cynetworkx.algorithms.link_analysis",
            "cynetworkx.algorithms.operators",
            "cynetworkx.algorithms.approximation",
            "cynetworkx.algorithms.tree",
            "cynetworkx.classes",
            "cynetworkx.generators",
            "cynetworkx.drawing",
            "cynetworkx.linalg",
            "cynetworkx.readwrite",
            "cynetworkx.readwrite.json_graph",
            "cynetworkx.tests",
            "cynetworkx.testing",
            "cynetworkx.utils"]

docdirbase = 'share/doc/cynetworkx-%s' % version
# add basic documentation
data = [(docdirbase, glob("*.txt"))]
# add examples
for d in ['.',
          'advanced',
          'algorithms',
          'basic',
          '3d_drawing',
          'drawing',
          'graph',
          'javascript',
          'jit',
          'pygraphviz',
          'subclass']:
    dd = os.path.join(docdirbase, 'examples', d)
    pp = os.path.join('examples', d)
    data.append((dd, glob(os.path.join(pp, "*.txt"))))
    data.append((dd, glob(os.path.join(pp, "*.py"))))
    data.append((dd, glob(os.path.join(pp, "*.bz2"))))
    data.append((dd, glob(os.path.join(pp, "*.gz"))))
    data.append((dd, glob(os.path.join(pp, "*.mbox"))))
    data.append((dd, glob(os.path.join(pp, "*.edgelist"))))

# add the tests
package_data = {
    'cynetworkx': ['tests/*.py'],
    'cynetworkx.algorithms': ['tests/*.py'],
    'cynetworkx.algorithms.assortativity': ['tests/*.py'],
    'cynetworkx.algorithms.bipartite': ['tests/*.py'],
    'cynetworkx.algorithms.node_classification': ['tests/*.py'],
    'cynetworkx.algorithms.centrality': ['tests/*.py'],
    'cynetworkx.algorithms.community': ['tests/*.py'],
    'cynetworkx.algorithms.components': ['tests/*.py'],
    'cynetworkx.algorithms.connectivity': ['tests/*.py'],
    'cynetworkx.algorithms.coloring': ['tests/*.py'],
    'cynetworkx.algorithms.flow': ['tests/*.py', 'tests/*.bz2'],
    'cynetworkx.algorithms.isomorphism': ['tests/*.py', 'tests/*.*99'],
    'cynetworkx.algorithms.link_analysis': ['tests/*.py'],
    'cynetworkx.algorithms.approximation': ['tests/*.py'],
    'cynetworkx.algorithms.operators': ['tests/*.py'],
    'cynetworkx.algorithms.shortest_paths': ['tests/*.py'],
    'cynetworkx.algorithms.traversal': ['tests/*.py'],
    'cynetworkx.algorithms.tree': ['tests/*.py'],
    'cynetworkx.classes': ['tests/*.py'],
    'cynetworkx.generators': ['tests/*.py', 'atlas.dat.gz'],
    'cynetworkx.drawing': ['tests/*.py'],
    'cynetworkx.linalg': ['tests/*.py'],
    'cynetworkx.readwrite': ['tests/*.py'],
    'cynetworkx.readwrite.json_graph': ['tests/*.py'],
    'cynetworkx.testing': ['tests/*.py'],
    'cynetworkx.utils': ['tests/*.py']
}

install_requires = ['decorator>=4.1.0']
extras_require = {'all': ['numpy', 'scipy', 'pandas', 'matplotlib',
                          'pygraphviz', 'pydot', 'pyyaml', 'gdal', 'lxml','nose']}

if __name__ == "__main__":

    setup(
        name=release.name.lower(),
        version=version,
        maintainer=release.maintainer,
        maintainer_email=release.maintainer_email,
        author=release.authors['Pattern, Inc.'][0],
        author_email=release.authors['Pattern, Inc.'][1],
        description=release.description,
        keywords=release.keywords,
        long_description=release.long_description,
        license=release.license,
        platforms=release.platforms,
        url=release.url,
        download_url=release.download_url,
        classifiers=release.classifiers,
        packages=packages,
        data_files=data,
        package_data=package_data,
        install_requires=install_requires,
        extras_require=extras_require,
        test_suite='nose.collector',
        tests_require=['nose>=0.10.1'],
        zip_safe=False,
        ext_modules=cythonize(extensions)
    )
