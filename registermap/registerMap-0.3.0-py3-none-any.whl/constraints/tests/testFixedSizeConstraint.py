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

import registerMap.constraints.constraints as rmc
import registerMap.structure.memory.space as rmm


log = logging.getLogger( __name__ )


class TestFixedSizeMemoryUnits( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )

        self.constraint = rmc.FixedSizeMemoryUnits( self.memory )


    def testName( self ) :
        self.assertEqual( self.constraint.name, rmc.FixedSizeMemoryUnits.name )


    def testType( self ) :
        self.assertEqual( self.constraint.type, rmc.AbstractConstraint.constraintTypes[ 'size' ] )


def doNoneConstraintAsserts( self, methodUnderTest ) :
    with self.assertRaises( AssertionError ) :
        methodUnderTest( 14 )


def doNonIntSizeRaises( self, methodUnderTest ) :
    with self.assertRaises( AssertionError ) :
        methodUnderTest( '12' )


def doNegativeSizeRaises( self, methodUnderTest ) :
    self.constraint.sizeConstraint = 12

    with self.assertRaisesRegex( rmc.ConstraintError, '^Fixed size must be a positive integer' ) :
        methodUnderTest( -14 )


class TestFixedSizeMemoryUnitsCalculation( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )

        self.constraint = rmc.FixedSizeMemoryUnits( self.memory )


    def testNoneConstraintAsserts( self ) :
        doNoneConstraintAsserts( self, self.constraint.calculate )


    def testNonIntSizeRaises( self ) :
        doNonIntSizeRaises( self, self.constraint.calculate )


    def testNegativeSizeRaises( self ) :
        self.constraint.value = 12

        doNegativeSizeRaises( self, self.constraint.calculate )


    def testOverSizeRaises( self ) :
        expectedSize = 12

        self.constraint.value = expectedSize

        with self.assertRaisesRegex( rmc.ConstraintError, '^Fixed size exceeded' ) :
            self.constraint.calculate( 14 )


    def testConstraintCalculation( self ) :
        expectedSize = 12

        self.constraint.value = expectedSize

        actualSize = self.constraint.calculate( 10 )

        self.assertEqual( actualSize, expectedSize )


class TestFixedSizeMemoryUnitsValidation( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )

        self.constraint = rmc.FixedSizeMemoryUnits( self.memory )


    def testNonIntSizeRaises( self ) :
        doNonIntSizeRaises( self, self.constraint.validate )


    def testNegativeSizeRaises( self ) :
        self.constraint.value = 12

        doNegativeSizeRaises( self, self.constraint.validate )


class TestFixedSizeMemoryUnitsValueProperty( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )

        self.constraint = rmc.FixedSizeMemoryUnits( self.memory )


    def testGetProperty( self ) :
        expectedValue = 14
        self.constraint.value = expectedValue

        actualValue = self.constraint.value

        self.assertEqual( actualValue, expectedValue )


    def testNegativeConstraintRaises( self ) :
        with self.assertRaisesRegex( rmc.ConstraintError,
                                     '^Fixed size must be a positive integer' ) :
            self.constraint.value = -12


class TestLoadSave( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )
        self.constraint = rmc.FixedSizeMemoryUnits( self.memory )


    def testEncodeDecode( self ) :
        self.constraint.value = 4

        encodedYamlData = self.constraint.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = rmc.FixedSizeMemoryUnits.from_yamlData( encodedYamlData, self.memory )

        self.assertEqual( decodedData.value, self.constraint.value )


    def testDecodeNonAlignmentConstraintRaises( self ) :
        with self.assertRaisesRegex( rmc.ParseError, '^Yaml data does not contain fixed size constraint' ) :
            rmc.FixedSizeMemoryUnits.from_yamlData( { }, self.memory )


    def testDecodeOptionalAlignmentConstraintRaises( self ) :
        constraint = rmc.FixedAddress.from_yamlData( { }, self.memory,
                                                     optional = True )

        self.assertIsNone( constraint )


if __name__ == '__main__' :
    unittest.main( )
