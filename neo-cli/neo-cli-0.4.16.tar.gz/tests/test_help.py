"""Tests for our main skele CLI module."""

from subprocess import PIPE, Popen as popen
from unittest import TestCase

from neo import __version__ as VERSION


class TestHelp(TestCase):
    def test_returns_usage_information(self):
        output = popen(['neo', '-h'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:' in str(output))

        output = popen(['neo', '--help'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:' in str(output))


class TestVersion(TestCase):
    def test_returns_version_information(self):
        output = popen(['neo', '--version'], stdout=PIPE).communicate()[0]
        self.assertEqual(output, "{}\n".format(VERSION).encode())
