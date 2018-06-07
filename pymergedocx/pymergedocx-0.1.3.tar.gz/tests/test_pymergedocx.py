#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pymergedocx` package."""

import os
import unittest
from click.testing import CliRunner
from pymergedocx import pymergedocx
from pymergedocx import cli, merge_docx

current_path = os.path.dirname(os.path.abspath(__file__))


class TestPymergedocx(unittest.TestCase):
    """Tests for `pymergedocx` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""
        merge_docx('{}/files/result.docx'.format(current_path), '{}/files/template.docx'.format(current_path),
                   '{}/files/template1.docx'.format(current_path), '{}/files/template2.docx'.format(current_path))

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'pymergedocx.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
