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

from registerMap.elements.tests.mockObserver import MockObserver
from registerMap.exceptions import ConfigurationError
from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace


class CommonPublicParameterTests :
    class TestRegisterPublic( unittest.TestCase ) :
        # The tests will fail unless a test case loader correctly fulfills this value.
        RegisterType = None


        def setUp( self ) :
            self.observer = MockObserver()
            self.setCollection = SetCollection()
            self.testSpace = MemorySpace()
            self.registerUnderTest = self.RegisterType( self.testSpace,
                                                        setCollection = self.setCollection )

            self.registerUnderTest.sizeChangeNotifier.addObserver( self.observer )


        def testDefaultValue( self ) :
            expectedValue = True
            self.assertEqual( self.registerUnderTest[ 'public' ], expectedValue )


        def testDataAssignment( self ) :
            self.assertTrue( self.registerUnderTest[ 'public' ] )

            self.registerUnderTest[ 'public' ] = False

            self.assertFalse( self.registerUnderTest[ 'public' ] )
            self.assertEqual( self.observer.updateCount, 0 )


        def testNonBoolRaises( self ) :
            with self.assertRaisesRegex( ConfigurationError, '^Public must be specified as boolean' ) :
                self.registerUnderTest[ 'public' ] = 'true'
