"""
Unit tests for RegisterMap
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

from registerMap.registerMap import \
    ConfigurationError, \
    Module, \
    RegisterMap


log = logging.getLogger( __name__ )


class TestDefaultModuleInstantiation( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = RegisterMap()


    def testDefaultValues( self ) :
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )


class TestBaseAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = RegisterMap()


    def testDefaultBaseAddress( self ) :
        expectedBaseAddress = 0
        actualBaseAddress = self.thisMap.memory.baseAddress

        self.assertTrue( isinstance( actualBaseAddress, int ) )
        self.assertEqual( actualBaseAddress, expectedBaseAddress )


    def testSetBaseAddressGoodValue( self ) :
        expectedBaseAddress = 25

        # Don't test with the default value
        self.assertNotEqual( expectedBaseAddress, self.thisMap.memory.baseAddress )

        self.thisMap.memory.baseAddress = expectedBaseAddress
        actualBaseAddress = self.thisMap.memory.baseAddress

        self.assertEqual( actualBaseAddress, expectedBaseAddress )


class TestMemoryAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = RegisterMap()


    def testDefaultMemoryAddressBits( self ) :
        expectedMemoryAddressBits = 32
        actualMemoryAddressBits = self.thisMap.memory.addressBits

        self.assertTrue( isinstance( actualMemoryAddressBits, int ) )
        self.assertEqual( actualMemoryAddressBits, expectedMemoryAddressBits )


    def testSetGoodValue( self ) :
        expectedMemoryAddressBits = 20

        self.assertNotEqual( expectedMemoryAddressBits, self.thisMap.memory.addressBits )

        self.thisMap.memory.addressBits = expectedMemoryAddressBits
        actualMemoryAddressBits = self.thisMap.memory.addressBits

        self.assertEqual( actualMemoryAddressBits, expectedMemoryAddressBits )


class TestMemoryUnit( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = RegisterMap()


    def testDefaultMemoryUnitBits( self ) :
        expectedMemoryUnitBits = 8
        actualMemoryUnitBits = self.thisMap.memory.memoryUnitBits

        self.assertTrue( isinstance( actualMemoryUnitBits, int ) )
        self.assertEqual( actualMemoryUnitBits, expectedMemoryUnitBits )


class TestPageSize( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = RegisterMap()


    def testDefaultPageSize( self ) :
        actualPageSize = self.thisMap.memory.pageSize

        self.assertIsNone( actualPageSize )


    def testPageSizeAssignment( self ) :
        expectedPageSize = 128

        self.assertNotEqual( expectedPageSize, self.thisMap.memory.pageSize )

        self.thisMap.memory.pageSize = expectedPageSize
        actualPageSize = self.thisMap.memory.pageSize

        self.assertEqual( actualPageSize, expectedPageSize )


class TestRegisterMapModules( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = RegisterMap()


    def testDefaultModules( self ) :
        self.assertTrue( isinstance( self.thisMap[ 'modules' ], dict ) )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )


class TestAddModule( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = RegisterMap()


    def testAddSingleModule( self ) :
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )

        newModule = self.thisMap.addModule( 'm1' )

        self.assertEqual( self.thisMap.spanMemoryUnits, 0 )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 1 )
        self.assertTrue( isinstance( newModule, Module ) )

        self.assertEqual( newModule.baseAddress, self.thisMap.memory.baseAddress )


    def testAddDuplicateModuleNameRaises( self ) :
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )

        self.thisMap.addModule( 'm1' )

        with self.assertRaisesRegex( ConfigurationError,
                                     '^Created module names must be unique within a register map' ) :
            self.thisMap.addModule( 'm1' )


class TestModuleAddresses( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = RegisterMap()


    def testBaseAddressUpdate( self ) :
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )

        m1 = self.thisMap.addModule( 'm1' )
        self.assertEqual( self.thisMap.spanMemoryUnits, 0 )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 1 )
        self.assertEqual( m1.baseAddress, self.thisMap.memory.baseAddress )

        r1 = m1.addRegister( 'r1' )
        self.assertEqual( self.thisMap.spanMemoryUnits, 1 )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 1 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 1 )
        self.assertEqual( r1.address, self.thisMap.memory.baseAddress )

        self.thisMap.memory.baseAddress = 0x10

        # Existing register and module must reflect the base address change.
        self.assertEqual( m1.baseAddress, self.thisMap.memory.baseAddress )
        self.assertEqual( r1.address, self.thisMap.memory.baseAddress )


    def testModuleSequentialAddresses( self ) :
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )

        m1 = self.thisMap.addModule( 'm1' )
        self.assertEqual( self.thisMap.spanMemoryUnits, 0 )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 1 )
        self.assertEqual( m1.baseAddress, self.thisMap.memory.baseAddress )

        r1 = m1.addRegister( 'r1' )
        self.assertEqual( self.thisMap.spanMemoryUnits, 1 )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 1 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 1 )
        self.assertEqual( r1.address, self.thisMap.memory.baseAddress )

        m2 = self.thisMap.addModule( 'm2' )
        r2 = m2.addRegister( 'r2' )

        self.thisMap.memory.baseAddress = 0x10

        # Existing registers and modules must reflect the base address change.
        self.assertEqual( m1.baseAddress, self.thisMap.memory.baseAddress )
        self.assertEqual( r1.address, self.thisMap.memory.baseAddress )
        self.assertEqual( m2.baseAddress, (self.thisMap.memory.baseAddress + 1) )
        self.assertEqual( r2.address, (self.thisMap.memory.baseAddress + 1) )


    def testAssignedCount( self ) :
        self.assertEqual( 8, self.thisMap.memory.memoryUnitBits )
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( 0, self.thisMap.assignedMemoryUnits )
        self.assertEqual( 0, len( self.thisMap[ 'modules' ] ) )

        m1 = self.thisMap.addModule( 'm1' )
        r1 = m1.addRegister( 'r1' )
        m2 = self.thisMap.addModule( 'm2' )
        r2 = m2.addRegister( 'r2' )
        r2.addField( 'f2', [ 3, 10 ], (3, 10) )
        r2[ 'constraints' ][ 'fixedAddress' ] = 0x15

        log.debug( 'm1 address before base assigment: ' + hex( m1.baseAddress ) )
        log.debug( 'm2 address before base assigment: ' + hex( m2.baseAddress ) )
        log.debug( 'r1 address before base assigment: ' + hex( r1.address ) )
        log.debug( 'r2 address before base assigment: ' + hex( r2.address ) )

        self.assertEqual( 3, self.thisMap.assignedMemoryUnits )
        self.assertEqual( 23, self.thisMap.spanMemoryUnits )

        log.debug( 'register map base address assignment' )
        self.thisMap.memory.baseAddress = 0x10

        log.debug( 'm1 address after base assigment: ' + hex( m1.baseAddress ) )
        log.debug( 'm2 address after base assigment: ' + hex( m2.baseAddress ) )
        log.debug( 'r1 address after base assigment: ' + hex( r1.address ) )
        log.debug( 'r2 address after base assigment: ' + hex( r2.address ) )

        self.assertEqual( 1, m1.spanMemoryUnits )
        self.assertEqual( 6, m2.spanMemoryUnits )

        expectedRegisterMapSpan = m1.spanMemoryUnits + m2.spanMemoryUnits

        self.assertEqual( 3, self.thisMap.assignedMemoryUnits )
        self.assertEqual( expectedRegisterMapSpan, self.thisMap.spanMemoryUnits )


if __name__ == '__main__' :
    unittest.main()
