# -*- coding: utf-8 -*-

"""Testing for CX and NDEx import/export."""

import unittest

from pybel.examples import braf_graph, egf_graph, sialic_acid_graph, statin_graph
from pybel_cx.cx import from_cx, to_cx
from tests.cases import TestCase
from tests.examples import example_graph


class TestSchema1(TestCase):
    """Test mapping schema 1."""

    def help_test_graph(self, graph):
        """Help test a graph with remapping.

        :param pybel.BELGraph graph:
        """
        reconstituted = from_cx(to_cx(graph))
        self.assert_graph_equal(graph, reconstituted)

    def test_sialic_acid_graph(self):
        """Test the round trip in the sialic acid graph."""
        self.help_test_graph(sialic_acid_graph)

    def test_braf_graph(self):
        """Test the round trip in the BRAF graph."""
        self.help_test_graph(braf_graph)

    def test_egf_graph(self):
        """Test the round trip in the EGF graph."""
        self.help_test_graph(egf_graph)

    def test_statin_graph(self):
        """Test the round trip in the statin graph."""
        self.help_test_graph(statin_graph)

    def test_example(self):
        """Test the round trip in an example graph."""
        self.help_test_graph(example_graph)


if __name__ == '__main__':
    unittest.main()
