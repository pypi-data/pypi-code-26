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

import logging
import unittest

from registerMap.structure.memory.space import MemorySpace

from ..constraints import \
    AbstractConstraint, \
    AlignmentMemoryUnits, \
    ConstraintError, \
    ParseError


log = logging.getLogger( __name__ )


class TestAlignmentMemoryUnits( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()

        self.constraint = AlignmentMemoryUnits( self.memory )


    def testName( self ) :
        self.assertEqual( self.constraint.name, AlignmentMemoryUnits.name )


    def testType( self ) :
        self.assertEqual( self.constraint.type, AbstractConstraint.constraintTypes[ 'address' ] )


def doNoneConstraintValueAsserts( self, methodUnderTest ) :
    with self.assertRaises( AssertionError ) :
        methodUnderTest( 0xa )


def doNonIntAddressRaises( self, methodUnderTest ) :
    with self.assertRaises( AssertionError ) :
        methodUnderTest( '0xa' )


def doNegativeAddressRaises( self, methodUnderTest ) :
    with self.assertRaises( AssertionError ) :
        methodUnderTest( '-12' )


def doZeroAddressNoRaise( self, methodUnderTest ) :
    methodUnderTest( 0 )


class TestAlignmentMemoryUnitsConstructor( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()


    def testDefaultConstructorNoRaise( self ) :
        c = AlignmentMemoryUnits( self.memory )


    def testZeroConstraintValueRaises( self ) :
        with self.assertRaisesRegex( ConstraintError, '^Alignment must be a positive non-zero integer' ) :
            AlignmentMemoryUnits( self.memory,
                                  constraintValue = 0 )


    def testNonIntConstraintValueAsserts( self ) :
        with self.assertRaises( AssertionError ) :
            AlignmentMemoryUnits( self.memory,
                                  constraintValue = '1' )


    def testNoneConstraintValueNoRaise( self ) :
        c = AlignmentMemoryUnits( self.memory,
                                  constraintValue = None )


class TestAlignmentMemoryUnitsCalculation( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()

        self.constraint = AlignmentMemoryUnits( self.memory )


    def testNoneConstraintAsserts( self ) :
        doNoneConstraintValueAsserts( self, self.constraint.calculate )


    def testNonIntAddressRaises( self ) :
        doNonIntAddressRaises( self, self.constraint.calculate )


    def testNegativeAddressRaises( self ) :
        doNegativeAddressRaises( self, self.constraint.calculate )


    def testZeroAddressNoRaise( self ) :
        self.constraint.value = 4
        doZeroAddressNoRaise( self, self.constraint.calculate )


    def testAlignAddress( self ) :
        expectedAddress = 0xc
        self.constraint.value = 4

        actualAddress = self.constraint.calculate( 0xa )

        self.assertEqual( actualAddress, expectedAddress )


    def testNoneAddress( self ) :
        self.constraint.value = 4

        self.assertIsNone( self.constraint.calculate( None ) )


    def testZeroAddress( self ) :
        expectedAddress = 0
        self.constraint.value = 4

        actualAddress = self.constraint.calculate( expectedAddress )

        self.assertEqual( actualAddress, expectedAddress )


class TestAlignmentMemoryUnitsValidation( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()

        self.constraint = AlignmentMemoryUnits( self.memory )


    def testNonIntAddressRaises( self ) :
        doNonIntAddressRaises( self, self.constraint.validate )


    def testNegativeAddressRaises( self ) :
        doNegativeAddressRaises( self, self.constraint.validate )


    def testZeroAddressNoRaise( self ) :
        doZeroAddressNoRaise( self, self.constraint.validate )


class TestAlignmentMemoryUnitsValueProperty( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()

        self.constraint = AlignmentMemoryUnits( self.memory )


    def testGetProperty( self ) :
        expectedValue = 14
        self.constraint.value = expectedValue

        actualValue = self.constraint.value

        self.assertEqual( actualValue, expectedValue )


    def testZeroValueRaises( self ) :
        with self.assertRaisesRegex( ConstraintError, '^Alignment must be a positive non-zero integer' ) :
            self.constraint.value = 0


    def testNonIntValueAsserts( self ) :
        with self.assertRaises( AssertionError ) :
            self.constraint.value = '1'


class TestLoadSave( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()
        self.constraint = AlignmentMemoryUnits( self.memory )


    def testEncodeDecode( self ) :
        self.constraint.value = 4

        encodedYamlData = self.constraint.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = AlignmentMemoryUnits.from_yamlData( encodedYamlData, self.memory )

        self.assertEqual( decodedData.value, self.constraint.value )


    def testDecodeNonAlignmentConstraintRaises( self ) :
        with self.assertRaisesRegex( ParseError, '^Yaml data does not contain alignment constraint' ) :
            AlignmentMemoryUnits.from_yamlData( { }, self.memory )


    def testDecodeOptionalAlignmentConstraintRaises( self ) :
        constraint = AlignmentMemoryUnits.from_yamlData( { }, self.memory,
                                                         optional = True )

        self.assertIsNone( constraint )


if __name__ == '__main__' :
    unittest.main()
