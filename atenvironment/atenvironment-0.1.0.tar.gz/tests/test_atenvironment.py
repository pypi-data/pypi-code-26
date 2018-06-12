#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `atenvironment` package."""


import unittest
import os

from atenvironment import atenvironment


class TestAtenvironment(unittest.TestCase):
    """Tests for `atenvironment` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_decorator(self):
        """Test decorator."""
        key = next(iter(os.environ.keys()))

        @atenvironment.environment(key)
        def test(key):
            return key

        self.assertEqual(test(), os.environ[key])
