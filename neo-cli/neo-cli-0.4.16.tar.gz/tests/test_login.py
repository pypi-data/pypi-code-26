"""Tests for our `neo hello` subcommand."""

from subprocess import PIPE, Popen as popen
from unittest import TestCase
from neo.libs import login


class TestLogin(TestCase):
    def test_do_login(self):
        output = login.do_login()
        self.assertTrue(output)
