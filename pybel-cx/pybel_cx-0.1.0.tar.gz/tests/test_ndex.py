# -*- coding: utf-8 -*-

"""Tests for NDEx upload and download."""

import os
import time
import unittest

from pybel_cx import from_ndex, to_ndex
from pybel_cx.ndex_utils import NDEX_PASSWORD, NDEX_USERNAME
from tests.cases import TestCase
from tests.examples import example_graph

_has_ndex_cred = NDEX_USERNAME in os.environ and NDEX_PASSWORD in os.environ


@unittest.skip
class TestInterchange(TestCase):
    """A test case for CX and NDEx import/export."""

    def help_test_ndex(self, graph):
        """Test sending and receiving a graph with NDEx.

        This test sleeps in the middle so NDEx can process.
        """
        network_id = to_ndex(graph)
        time.sleep(10)
        reconstituted = from_ndex(network_id)
        self.assert_graph_equal(graph, reconstituted)

    @unittest.skipUnless(_has_ndex_cred, 'Need NDEx credentials')
    def test_example_ndex(self):
        """Test the round trip to NDEx."""
        self.help_test_ndex(example_graph)


if __name__ == '__main__':
    unittest.main()
