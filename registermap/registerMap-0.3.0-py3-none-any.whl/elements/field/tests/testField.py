"""
Test BitField.
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

from registerMap.elements.tests.mockObserver import MockObserver
from registerMap.exceptions import ConfigurationError

from ..field import Field


log = logging.getLogger( __name__ )


class TestFieldDescription( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.testField = Field()

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = ''
        self.assertEqual( self.testField[ 'description' ], expectedValue )


    def testDataAssignment( self ) :
        expectedValue = 'some description'
        self.assertNotEqual( expectedValue, self.testField[ 'description' ] )

        self.testField[ 'description' ] = expectedValue

        self.assertEqual( self.testField[ 'description' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 0 )


class TestFieldGlobal( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.testField = Field()

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertTrue( self.testField[ 'global' ] )


    def testDataAssignment( self ) :
        class MockRegister :
            def __init__( self ) :
                self.canonicalId = 'someName'


        register = MockRegister()

        testField = Field( parent = register )

        self.assertFalse( testField[ 'global' ] )


class TestFieldName( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.testField = Field()

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = 'unassigned'
        self.assertEqual( self.testField[ 'name' ], expectedValue )


    def testDataAssignment( self ) :
        expectedValue = 'new name'
        self.assertNotEqual( expectedValue, self.testField[ 'name' ] )

        self.testField[ 'name' ] = expectedValue

        self.assertEqual( self.testField[ 'name' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 0 )


class TestFieldResetValue( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.testField = Field()

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertEqual( self.testField[ 'resetValue' ], 0 )


    def testDataAssignment( self ) :
        expectedValue = 0xd
        self.testField[ 'size' ] = 9
        self.assertEqual( self.observer.updateCount, 1 )
        self.assertNotEqual( expectedValue, self.testField[ 'resetValue' ] )

        self.testField[ 'resetValue' ] = expectedValue
        actualValue = self.testField[ 'resetValue' ]

        self.assertEqual( actualValue, expectedValue )
        self.assertEqual( self.observer.updateCount, 1 )


    def testNonIntRaises( self ) :
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Must be an int' ) :
            self.testField[ 'resetValue' ] = '5'


    def testNegativeIntRaises( self ) :
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Must be a positive int' ) :
            self.testField[ 'resetValue' ] = -5


    def testResetValueGreaterThanBitRangeRaises( self ) :
        self.testField[ 'size' ] = 2
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Reset value cannot exceed number of bits of field' ) :
            self.testField[ 'resetValue' ] = 8


    def testResetValueAssignBitRangeUndefinedRaises( self ) :
        self.assertEqual( self.testField[ 'size' ], 0 )
        with self.assertRaisesRegex( ConfigurationError, '^Reset value cannot exceed number of bits of field' ) :
            self.testField[ 'resetValue' ] = 8


class TestFieldSize( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.testField = Field()

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = 0

        self.assertEqual( self.testField[ 'size' ], expectedValue )
        self.assertEqual( self.testField[ 'size' ], self.testField.sizeBits )


    def testDataAssignment( self ) :
        expectedValue = 10
        self.assertNotEqual( expectedValue, self.testField[ 'size' ] )

        self.testField[ 'size' ] = expectedValue
        actualValue = self.testField[ 'size' ]

        self.assertEqual( actualValue, expectedValue )
        self.assertEqual( self.observer.updateCount, 1 )


    def testChangedValueNotifies( self ) :
        expectedValue = 15
        self.assertNotEqual( self.testField[ 'size' ], expectedValue )

        self.testField[ 'size' ] = expectedValue

        self.assertEqual( self.observer.updateCount, 1 )


class TestFieldSummary( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.testField = Field()

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = ''
        self.assertEqual( self.testField[ 'summary' ], expectedValue )


    def testDataAssignment( self ) :
        expectedValue = 'does something'
        self.assertNotEqual( expectedValue, self.testField[ 'summary' ] )

        self.testField[ 'summary' ] = expectedValue

        self.assertEqual( self.testField[ 'summary' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 0 )


if __name__ == '__main__' :
    unittest.main()
