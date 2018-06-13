#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test thu_utils

usage:
    python -m unittest test.py
    python -m unittest test.TestUserpass.testuser
"""

import unittest

from context import userpass


class TestUserpass(unittest.TestCase):
    """Unittest for thu_utils"""

    def test_user(self):
        """test User"""
        userpass.userpass.input = lambda _: 'test'
        userpass.userpass.getpass.getpass = lambda: 'test'
        user = userpass.User('.test_thu')
        self.assertEqual(user.username, b'test')
        self.assertEqual(user.password, b'test')
        user.del_user()


if __name__ == "__main__":
    unittest.main()
