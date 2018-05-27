#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""

import logging
import unittest
from unittest.util import safe_repr

logger = logging.getLogger(__name__)


class Test(object):
    VARIATONS = {}

    def __init__(self):
        self.variation = None

    def assertEqual(self, first, second, msg=None):
        """Fail if the two objects are unequal as determined by the '=='
           operator.
        """
        if first != second:
            raise AssertionError(msg)
       
    
    def assertLess(self, a, b, msg=None):
        """Just like self.assertTrue(a < b), but with a nicer default message."""
        if not a < b:
            msg = msg or '%s not less than %s' % (safe_repr(a), safe_repr(b))
            raise AssertionError(msg)

    def assertLessEqual(self, a, b, msg=None):
        """Just like self.assertTrue(a <= b), but with a nicer default message."""
        if not a <= b:
            msg = msg or '%s not less than or equal to %s' % (safe_repr(a), safe_repr(b))
            raise AssertionError(msg)

    def assertGreater(self, greater, lower, msg=None):
        """Just like self.assertTrue(a > b), but with a nicer default message."""
        if not greater > lower:
            msg = msg or '%s not greater than %s' % (safe_repr(greater), safe_repr(lower))
            raise AssertionError(msg)

    def assertGreaterEqual(self, a, b, msg=None):
        """Just like self.assertTrue(a >= b), but with a nicer default message."""
        if not a >= b:
            msg = msg or '%s not greater than or equal to %s' % (safe_repr(a), safe_repr(b))
            raise AssertionError(msg)

    def assertIsNone(self, obj, msg=None):
        """Same as self.assertTrue(obj is None), with a nicer default message."""
        if obj is not None:
            msg = msg or '%s is not None' % (safe_repr(obj),)
            raise AssertionError(msg)

    def assertIsNotNone(self, obj, msg=None):
        """Included for symmetry with assertIsNone."""
        if obj is None:
            msg = msg or 'unexpectedly None'
            raise AssertionError(msg)
