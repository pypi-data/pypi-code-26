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

from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace

from ..module import Module


class TestModuleUserDefinedParameter( unittest.TestCase ) :
    def setUp( self ) :
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()

        self.moduleUnderTest = Module( self.testSpace, self.setCollection )


    def testAssignUserParameterOk( self ) :
        expectedValue = 'some value'

        self.moduleUnderTest[ 'my-parameter' ] = expectedValue

        self.assertEqual( expectedValue, self.moduleUnderTest[ 'my-parameter' ] )


    def testBadParameterRaises( self ) :
        with self.assertRaisesRegex( KeyError, 'Module parameter not in core or user data' ) :
            self.moduleUnderTest[ 'bad-parameter' ]


    def testUnderscorePrefixAsserts( self ) :
        with self.assertRaises( AssertionError ) :
            self.moduleUnderTest[ '_my-parameter' ] = 2


if __name__ == '__main__' :
    unittest.main()
