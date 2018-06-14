"""
Unit tests for Register
"""
#
# Copyright 2016 Russell Smiley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
import unittest

from ..register import Register

from .commonTests import \
    addCommonTestCases


log = logging.getLogger( __name__ )


# https://docs.python.org/3.6/library/unittest.html#load-tests-protocol
#
# nosetests doesn't use the loader, tests, patten arguments with load_tests
# so since they aren't being used anyway, just made them optional.
def load_tests( loader = None, tests = None, pattern = None ) :
    thisSuite = unittest.TestSuite()

    thisSuite = addCommonTestCases( Register, thisSuite )

    return thisSuite
