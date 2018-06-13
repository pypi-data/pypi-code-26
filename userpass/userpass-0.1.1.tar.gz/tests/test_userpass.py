#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test thu_utils

usage:
    python -m unittest test.py
    python -m unittest test.TestUserpass.testuser
"""

import pytest

from .context import userpass


class TestUserpass:
    """Pytest for userpass"""

    def test_user(self):
        """test User"""
        userpass.userpass.input = lambda _: 'test'
        userpass.userpass.getpass.getpass = lambda: 'password'
        user = userpass.User('.test')
        user.show()
        assert user.username == b'test'
        assert user.password == b'password'
        user.del_user()
