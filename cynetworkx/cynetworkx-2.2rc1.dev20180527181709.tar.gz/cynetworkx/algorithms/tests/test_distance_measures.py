#!/usr/bin/env python
from nose.tools import *
import cynetworkx


class TestDistance:

    def setUp(self):
        G = cynetworkx.Graph()
        from cynetworkx import convert_node_labels_to_integers as cnlti
        G = cnlti(cynetworkx.grid_2d_graph(4, 4), first_label=1, ordering="sorted")
        self.G = G

    def test_eccentricity(self):
        assert_equal(cynetworkx.eccentricity(self.G, 1), 6)
        e = cynetworkx.eccentricity(self.G)
        assert_equal(e[1], 6)
        sp = dict(cynetworkx.shortest_path_length(self.G))
        e = cynetworkx.eccentricity(self.G, sp=sp)
        assert_equal(e[1], 6)
        e = cynetworkx.eccentricity(self.G, v=1)
        assert_equal(e, 6)
        # This behavior changed in version 1.8 (ticket #739)
        e = cynetworkx.eccentricity(self.G, v=[1, 1])
        assert_equal(e[1], 6)
        e = cynetworkx.eccentricity(self.G, v=[1, 2])
        assert_equal(e[1], 6)
        # test against graph with one node
        G = cynetworkx.path_graph(1)
        e = cynetworkx.eccentricity(G)
        assert_equal(e[0], 0)
        e = cynetworkx.eccentricity(G, v=0)
        assert_equal(e, 0)
        assert_raises(cynetworkx.NetworkXError, cynetworkx.eccentricity, G, 1)
        # test against empty graph
        G = cynetworkx.empty_graph()
        e = cynetworkx.eccentricity(G)
        assert_equal(e, {})

    def test_diameter(self):
        assert_equal(cynetworkx.diameter(self.G), 6)

    def test_radius(self):
        assert_equal(cynetworkx.radius(self.G), 4)

    def test_periphery(self):
        assert_equal(set(cynetworkx.periphery(self.G)), set([1, 4, 13, 16]))

    def test_center(self):
        assert_equal(set(cynetworkx.center(self.G)), set([6, 7, 10, 11]))

    def test_bound_diameter(self):
        assert_equal(cynetworkx.diameter(self.G, usebounds=True), 6)

    def test_bound_radius(self):
        assert_equal(cynetworkx.radius(self.G, usebounds=True), 4)

    def test_bound_periphery(self):
        assert_equal(set(cynetworkx.periphery(self.G, usebounds=True)), set([1, 4, 13, 16]))

    def test_bound_center(self):
        assert_equal(set(cynetworkx.center(self.G, usebounds=True)), set([6, 7, 10, 11]))

    def test_radius_exception(self):
        G = cynetworkx.Graph()
        G.add_edge(1, 2)
        G.add_edge(3, 4)
        assert_raises(cynetworkx.NetworkXError, cynetworkx.diameter, G)

    @raises(cynetworkx.NetworkXError)
    def test_eccentricity_infinite(self):
        G = cynetworkx.Graph([(1, 2), (3, 4)])
        e = cynetworkx.eccentricity(G)

    @raises(cynetworkx.NetworkXError)
    def test_eccentricity_undirected_not_connected(self):
        G = cynetworkx.Graph([(1, 2), (3, 4)])
        e = cynetworkx.eccentricity(G, sp=1)

    @raises(cynetworkx.NetworkXError)
    def test_eccentricity_directed_weakly_connected(self):
        DG = cynetworkx.DiGraph([(1, 2), (1, 3)])
        cynetworkx.eccentricity(DG)
