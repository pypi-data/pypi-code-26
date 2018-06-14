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


class CommonUserDefinedParameterTests :
    class TestRegisterUserDefinedParameter( unittest.TestCase ) :
        # The tests will fail unless a test case loader correctly fulfills this value.
        RegisterType = None


        def setUp( self ) :
            self.setCollection = SetCollection()
            self.testSpace = MemorySpace()

            self.registerUnderTest = self.RegisterType( self.testSpace,
                                                        setCollection = self.setCollection )


        def testAssignNewParameterOk( self ) :
            expectedValue = 'some value'
            self.registerUnderTest[ 'my-parameter' ] = expectedValue

            self.assertEqual( expectedValue, self.registerUnderTest[ 'my-parameter' ] )


        def testBadParameterRaises( self ) :
            with self.assertRaisesRegex( KeyError, 'Register parameter not in core or user data' ) :
                self.registerUnderTest[ 'bad-parameter' ]


        def testUnderscorePrefixAsserts( self ) :
            with self.assertRaises( AssertionError ) :
                self.registerUnderTest[ '_my-parameter' ] = 2
