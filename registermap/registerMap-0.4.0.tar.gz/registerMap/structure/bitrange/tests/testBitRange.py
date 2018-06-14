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

import registerMap.exceptions as rme
import registerMap.structure.bitrange as rmbr

from registerMap.elements.tests.mockObserver import MockObserver


log = logging.getLogger( __name__ )


class TestBitRange( unittest.TestCase ) :
    def setUp( self ) :
        self.testBitRange = rmbr.BitRange()
        self.observer = MockObserver()

        self.testBitRange.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertEqual( self.testBitRange, None )


    def testConstructedValue( self ) :
        expectedValue = [ 3, 6 ]
        r = rmbr.BitRange( value = expectedValue )
        self.assertEqual( r.value, set( expectedValue ) )


    def testBadConstructedValueRaises( self ) :
        expectedValue = '[3, 6]'
        with self.assertRaisesRegex( rme.ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            rmbr.BitRange( value = expectedValue )


    def testValueAssignment( self ) :
        expectedValue = [ 0, 8 ]

        self.testBitRange.value = expectedValue

        self.assertTrue( isinstance( self.testBitRange, rmbr.BitRange ) )
        self.assertEqual( self.testBitRange, expectedValue )
        self.assertTrue( self.observer.updated )


    def testMaxValue( self ) :
        expectedValue = 7
        self.testBitRange.value = [ 2, 4 ]
        self.assertEqual( self.testBitRange.maxValue, expectedValue )


    def testNonListRaises( self ) :
        with self.assertRaisesRegex( rme.ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            self.testBitRange.value = '5'


    def testListNonIntRaises( self ) :
        with self.assertRaisesRegex( rme.ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            self.testBitRange.value = [ 5, '6' ]


    def testNegativeValuesRaises( self ) :
        with self.assertRaisesRegex( rme.ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            self.testBitRange.value = [ 5, -7 ]


    def testWrongLengthRaises( self ) :
        with self.assertRaisesRegex( rme.ConfigurationError,
                                     '^Interval must be a set of one or two positive integers' ) :
            self.testBitRange.value = [ 5, 8, 6 ]


class TestNumberBits( unittest.TestCase ) :
    def setUp( self ) :
        self.testBitRange = rmbr.BitRange()


    def testCalculateNumberBits( self ) :
        expectedValue = 5
        self.testBitRange.value = [ 2, 6 ]
        self.assertEqual( self.testBitRange.numberBits, expectedValue )


    def testNumberBitsNoneValueIsZero( self ) :
        self.assertEqual( self.testBitRange.numberBits, 0 )


class TestEqualOperator( unittest.TestCase ) :
    def setUp( self ) :
        self.expectedValue = [ 3, 7 ]
        self.testBitRange = rmbr.BitRange( value = self.expectedValue )


    def testList( self ) :
        self.assertTrue( self.testBitRange == self.expectedValue )


    def testNone( self ) :
        # It is necessary to use == operator here because 'is' operator cannot be overridden in Python.
        self.assertFalse( self.testBitRange == None )


    def testBitRange( self ) :
        self.assertTrue( self.testBitRange == rmbr.BitRange( value = self.expectedValue ) )
        self.assertFalse( self.testBitRange == rmbr.BitRange( value = [ 0, 4 ] ) )


class TestNotEqualOperator( unittest.TestCase ) :
    def setUp( self ) :
        self.expectedValue = [ 3, 7 ]
        self.testBitRange = rmbr.BitRange( value = self.expectedValue )


    def testList( self ) :
        self.assertTrue( self.testBitRange != [ 0, 4 ] )


    def testNone( self ) :
        # It is necessary to use != operator here because 'is' operator cannot be overridden in Python.
        self.assertTrue( self.testBitRange != None )


    def testBitRange( self ) :
        self.assertFalse( self.testBitRange != rmbr.BitRange( value = self.expectedValue ) )
        self.assertTrue( self.testBitRange != rmbr.BitRange( value = [ 0, 4 ] ) )


if __name__ == '__main__' :
    unittest.main()
