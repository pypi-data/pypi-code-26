#
# Copyright 2017 Russell Smiley
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

from ..element import \
    ClosedIntegerInterval, \
    ConfigurationError


class TestIntervalDefaultConstructor( unittest.TestCase ) :
    def testDefaultValue( self ) :
        r = ClosedIntegerInterval()
        self.assertEqual( r, None )


    def testConstructedValue( self ) :
        expectedValue = { 3, 6 }
        r = ClosedIntegerInterval( value = expectedValue )
        self.assertEqual( r.value, expectedValue )


    def testHashable( self ) :
        # Using ClosedIntegerInterval as key in a dict must not fail.
        r = ClosedIntegerInterval()
        x = dict()
        x[ r ] = 'test'


    def testHashTwoEqualIntervalsIsSame( self ) :
        interval = (4, 7)
        r1 = ClosedIntegerInterval()
        r1.value = interval

        r2 = ClosedIntegerInterval()
        r2.value = interval

        self.assertEqual( hash( r1 ), hash( r2 ) )


class TestIntervalAssignment( unittest.TestCase ) :
    def setUp( self ) :
        self.testInterval = ClosedIntegerInterval()


    def testBadConstructedValueRaises( self ) :
        expectedValue = '[3, 6]'
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            ClosedIntegerInterval( value = expectedValue )


    def testSetValueAssignment( self ) :
        expectedValue = { 0, 8 }

        self.testInterval.value = expectedValue

        self.assertTrue( isinstance( self.testInterval, ClosedIntegerInterval ) )
        self.assertTrue( self.testInterval == expectedValue )


    def testListValueAssignment( self ) :
        expectedValue = [ 0, 8 ]

        self.testInterval.value = expectedValue

        self.assertTrue( isinstance( self.testInterval, ClosedIntegerInterval ) )
        self.assertTrue( self.testInterval == expectedValue )


    def testTupleValueAssignment( self ) :
        expectedValue = (0, 8)

        self.testInterval.value = expectedValue

        self.assertTrue( isinstance( self.testInterval, ClosedIntegerInterval ) )
        self.assertEqual( self.testInterval, expectedValue )


    def testSetSingleValueAssignment( self ) :
        expectedValue = { 1 }

        self.testInterval.value = expectedValue

        self.assertTrue( isinstance( self.testInterval, ClosedIntegerInterval ) )
        self.assertTrue( self.testInterval == expectedValue )


    def testListSingleValueAssignment( self ) :
        expectedValue = [ 1, 1 ]

        self.testInterval.value = expectedValue

        self.assertTrue( isinstance( self.testInterval, ClosedIntegerInterval ) )
        self.assertTrue( self.testInterval == expectedValue )


    def testTupleSingleValueAssignment( self ) :
        expectedValue = (1, 1)

        self.testInterval.value = expectedValue

        self.assertTrue( isinstance( self.testInterval, ClosedIntegerInterval ) )
        self.assertEqual( self.testInterval, expectedValue )


    def testNonListRaises( self ) :
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            self.testInterval.value = '5'


    def testListNonIntRaises( self ) :
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            self.testInterval.value = [ 5, '6' ]


    def testNegativeValuesRaises( self ) :
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            self.testInterval.value = [ 5, -7 ]


    def testWrongLengthRaises( self ) :
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            self.testInterval.value = [ 5, 7, 6 ]

        with self.assertRaisesRegex( ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            self.testInterval.value = tuple()


class TestIntervalSize( unittest.TestCase ) :
    def setUp( self ) :
        self.testInterval = ClosedIntegerInterval()


    def testDefaultSize( self ) :
        self.assertEqual( self.testInterval.size, 0 )


    def testSizeSingle( self ) :
        self.testInterval.value = (5, 5)
        self.assertEqual( self.testInterval.size, 1 )


    def testSizeMultiple( self ) :
        self.testInterval.value = (5, 8)
        self.assertEqual( self.testInterval.size, 4 )


class TestEqualOperator( unittest.TestCase ) :
    def setUp( self ) :
        self.expectedValue = [ 3, 7 ]
        self.testInterval = ClosedIntegerInterval( value = self.expectedValue )


    def testEqualSet( self ) :
        self.assertTrue( self.testInterval == { 3, 7 } )


    def testEqualList( self ) :
        self.assertTrue( self.testInterval == [ 3, 7 ] )


    def testEqualTuple( self ) :
        self.assertTrue( self.testInterval == (3, 7) )


    def testNone( self ) :
        self.assertFalse( self.testInterval == None )


    def testBitRange( self ) :
        self.assertTrue( self.testInterval == ClosedIntegerInterval( value = self.expectedValue ) )
        self.assertFalse( self.testInterval == ClosedIntegerInterval( value = [ 0, 4 ] ) )


class TestNotEqualOperator( unittest.TestCase ) :
    def setUp( self ) :
        self.expectedValue = [ 3, 7 ]
        self.testInterval = ClosedIntegerInterval( value = self.expectedValue )


    def testList( self ) :
        self.assertTrue( self.testInterval != [ 0, 4 ] )


    def testNone( self ) :
        self.assertTrue( self.testInterval != None )


    def testBitRange( self ) :
        self.assertFalse( self.testInterval != ClosedIntegerInterval( value = self.expectedValue ) )
        self.assertTrue( self.testInterval != ClosedIntegerInterval( value = [ 0, 4 ] ) )


class TestIntegerOffsetArithmetic( unittest.TestCase ) :
    def setUp( self ) :
        self.expectedValue = [ 3, 7 ]
        self.interval = ClosedIntegerInterval( value = self.expectedValue )


    def testAddInteger( self ) :
        expectedResult = ClosedIntegerInterval( value = (6, 10) )
        actualResult = self.interval + 3

        self.assertEqual( actualResult, expectedResult )


    def testIntegerAddInPlace( self ) :
        expectedResult = ClosedIntegerInterval( value = (6, 10) )
        self.interval += 3

        self.assertEqual( self.interval, expectedResult )


    def testSubtractInteger( self ) :
        expectedResult = ClosedIntegerInterval( value = (0, 4) )
        actualResult = self.interval - 3

        self.assertEqual( actualResult, expectedResult )


    def testIntegerSubtractInPlace( self ) :
        expectedResult = ClosedIntegerInterval( value = (0, 4) )
        self.interval -= 3

        self.assertEqual( self.interval, expectedResult )


if __name__ == '__main__' :
    unittest.main()
