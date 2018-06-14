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
import math
import unittest

import registerMap.constraints.constraints as rmc
import registerMap.structure.memory.space as rmm


log = logging.getLogger( __name__ )


class TestFixedAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )

        self.constraint = rmc.FixedAddress( self.memory )


    def testName( self ) :
        self.assertEqual( self.constraint.name, rmc.FixedAddress.name )


    def testType( self ) :
        self.assertEqual( self.constraint.type, rmc.AbstractConstraint.constraintTypes[ 'address' ] )


class TestFixedAddressCalculation( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )

        self.constraint = rmc.FixedAddress( self.memory )


    def testAddressOverRaises( self ) :
        expectedAddress = 0x12

        self.constraint.value = expectedAddress

        with self.assertRaisesRegex( rmc.ConstraintError, '^Fixed address exceeded' ) :
            self.constraint.calculate( 0x14 )


    def testConstraintCalculation( self ) :
        expectedAddress = 0x12

        self.constraint.value = expectedAddress

        actualAddress = self.constraint.calculate( 0x10 )

        self.assertEqual( actualAddress, expectedAddress )


    def testFixedAddressOnPageRegisterRaises( self ) :
        self.memory.pageSize = 128
        numberMemoryUnits = math.ceil( float( self.memory.addressBits ) / self.memory.memoryUnitBits )
        pageAddresses = [ (self.memory.pageSize - x + 0x800) for x in range( 1, (numberMemoryUnits + 1) ) ]

        for address in pageAddresses :
            with self.assertRaisesRegex( rmc.ConstraintError, '^Cannot constrain address to page register' ) :
                self.constraint.value = address


    def testNonIntAddressAsserts( self ) :
        with self.assertRaisesRegex( rmc.ConstraintError, '^Fixed address must be a positive integer' ) :
            self.constraint.calculate( '0x14' )


    def testNoneAddress( self ) :
        expectedAddress = 0x12

        self.constraint.value = expectedAddress

        actualAddress = self.constraint.calculate( None )

        self.assertEqual( actualAddress, expectedAddress )


class TestFixedAddressValidation( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )

        # Verify that the memory defaults are what are assumed in these tests.
        self.assertEqual( self.memory.addressBits, 32 )
        self.assertEqual( self.memory.memoryUnitBits, 8 )

        self.constraint = rmc.FixedAddress( self.memory )


    def testNoPageRegisterPasses( self ) :
        # No page register means any address should pass
        self.constraint.value = 0x12
        self.constraint.validate( 0x14 )


    def testNoneAddressPasses( self ) :
        self.constraint.validate( None )


    def testFixedAddressOnPageRegisterRaises( self ) :
        self.memory.pageSize = 0x13

        with self.assertRaisesRegex( rmc.ConstraintError, '^Cannot constrain address to page register' ) :
            self.constraint.value = 0x12


    def testFixedAddressOnPageRegisterRaisesWhenPageSizeIntroduced( self ) :
        self.constraint.value = 0x12

        with self.assertRaisesRegex( rmc.ConstraintError, '^Cannot constrain address to page register' ) :
            # Changing the memory page size is expected to notify the constraint which will now raise because it is no
            # longer valid.
            self.memory.pageSize = 0x13


    def testFixedAddressNotOnPageRegisterPasses( self ) :
        self.assertEqual( self.memory.addressBits, 32 )

        self.memory.pageSize = 0x13
        self.constraint.value = self.memory.pageSize - 4 - 1

        self.assertFalse( self.memory.isPageRegister( self.constraint.value ) )

        self.constraint.validate( 0x12 )


class TestFixedAddressMemoryUnitsValueProperty( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )

        self.constraint = rmc.FixedAddress( self.memory )


    def testGetProperty( self ) :
        expectedValue = 14
        self.constraint.value = expectedValue

        actualValue = self.constraint.value

        self.assertEqual( actualValue, expectedValue )


    def testZeroValueNoRaise( self ) :
        expectedValue = 0
        self.constraint.value = expectedValue

        actualValue = self.constraint.value

        self.assertEqual( actualValue, expectedValue )


    def testNoneValueAsserts( self ) :
        with self.assertRaises( AssertionError ) :
            self.constraint.value = None


class TestLoadSave( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )
        self.constraint = rmc.FixedAddress( self.memory )


    def testEncodeDecode( self ) :
        self.constraint.value = 4

        encodedYamlData = self.constraint.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = rmc.FixedAddress.from_yamlData( encodedYamlData, self.memory )

        self.assertEqual( decodedData.value, self.constraint.value )


    def testDecodeNonAlignmentConstraintRaises( self ) :
        with self.assertRaisesRegex( rmc.ParseError, '^Yaml data does not contain fixed address constraint' ) :
            rmc.FixedAddress.from_yamlData( { }, self.memory )


    def testDecodeOptionalAlignmentConstraintRaises( self ) :
        constraint = rmc.FixedAddress.from_yamlData( { }, self.memory,
                                                     optional = True )

        self.assertIsNone( constraint )


if __name__ == '__main__' :
    unittest.main( )
