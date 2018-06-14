#
# Copyright 2018 Russell Smiley
#
# This file is part of registerMap.
#
# registerMap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# registerMap is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with registerMap.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest

from ..instance import RegisterInstance

from .commonTests import \
    addCommonTestCases


# https://docs.python.org/3.6/library/unittest.html#load-tests-protocol
#
# nosetests doesn't use the loader, tests, patten arguments with load_tests
# so since they aren't being used anyway, just made them optional.
def load_tests( loader = None, tests = None, pattern = None ) :
    thisSuite = unittest.TestSuite()

    thisSuite = addCommonTestCases( RegisterInstance, thisSuite )

    return thisSuite
