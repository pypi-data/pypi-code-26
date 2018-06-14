"""
Unit tests for MemorySpace.
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

import registerMap.structure.memory.space as rmm
from registerMap.elements.tests.mockObserver import MockObserver


log = logging.getLogger( __name__ )


class TestBaseAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.thisSpace = rmm.MemorySpace( )

        self.observer = MockObserver( )
        self.thisSpace.addressChangeNotifier.addObserver( self.observer )
        self.thisSpace.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultBaseAddress( self ) :
        expectedBaseAddress = 0
        actualBaseAddress = self.thisSpace.baseAddress

        self.assertTrue( isinstance( actualBaseAddress, int ) )
        self.assertEqual( actualBaseAddress, expectedBaseAddress )
        self.assertEqual( self.observer.updateCount, 0 )


    def testSetBaseAddressGoodValue( self ) :
        expectedBaseAddress = 25

        # Don't test with the default value
        self.assertNotEqual( expectedBaseAddress, self.thisSpace.baseAddress )

        self.thisSpace.baseAddress = expectedBaseAddress
        actualBaseAddress = self.thisSpace.baseAddress

        self.assertEqual( actualBaseAddress, expectedBaseAddress )
        self.assertEqual( self.observer.updateCount, 1 )
        self.assertEqual( self.observer.arguments, 'baseAddress' )


    def testNonIntRaises( self ) :
        expectedBaseAddress = '25'

        with self.assertRaisesRegex( rmm.ConfigurationError,
                                     '^Base address must be specified as non-negative integer' ) :
            self.thisSpace.baseAddress = expectedBaseAddress


    def testNegativeRaises( self ) :
        with self.assertRaisesRegex( rmm.ConfigurationError,
                                     '^Base address must be specified as non-negative integer' ) :
            self.thisSpace.baseAddress = -1


    def testBaseAddressGreaterThanMemoryAddressBitsRaises( self ) :
        self.thisSpace.addressBits = 4

        expectedBaseAddress = 20

        with self.assertRaisesRegex( rmm.ConfigurationError,
                                     '^Base address must be less than maximum addressable memory' ) :
            self.thisSpace.baseAddress = expectedBaseAddress


class TestMaximumAddressableMemory( unittest.TestCase ) :
    def setUp( self ) :
        self.thisSpace = rmm.MemorySpace( )


    def testDefaultMaximumAddressableMemory( self ) :
        expectedMaximumAddressableMemory = pow( 2, self.thisSpace.addressBits )
        actualMaximumAddressableMemory = self.thisSpace.maximumMemoryAddress

        self.assertEqual( actualMaximumAddressableMemory, expectedMaximumAddressableMemory )


    def testSetNumberOfAddressBits( self ) :
        numberBits = 24
        self.assertNotEqual( self.thisSpace.addressBits, numberBits )

        self.thisSpace.addressBits = numberBits

        self.assertEqual( self.thisSpace.addressBits, numberBits )
        self.assertEqual( self.thisSpace.maximumMemoryAddress, pow( 2, numberBits ) )


class TestMemoryAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.thisSpace = rmm.MemorySpace( )

        self.observer = MockObserver( )
        self.thisSpace.addressChangeNotifier.addObserver( self.observer )


    def testDefaultMemoryAddressBits( self ) :
        expectedMemoryAddressBits = 32
        actualMemoryAddressBits = self.thisSpace.addressBits

        self.assertTrue( isinstance( actualMemoryAddressBits, int ) )
        self.assertEqual( actualMemoryAddressBits, expectedMemoryAddressBits )


    def testSetGoodValue( self ) :
        expectedMemoryAddressBits = 20

        self.assertNotEqual( expectedMemoryAddressBits, self.thisSpace.addressBits )

        self.thisSpace.addressBits = expectedMemoryAddressBits
        actualMemoryAddressBits = self.thisSpace.addressBits

        self.assertEqual( actualMemoryAddressBits, expectedMemoryAddressBits )


    def testNonIntRaises( self ) :
        with self.assertRaisesRegex( rmm.ConfigurationError,
                                     '^Memory address bits must be specified as positive non-zero integer' ) :
            self.thisSpace.addressBits = '20'


    def testZeroNegativeRaises( self ) :
        with self.assertRaisesRegex( rmm.ConfigurationError,
                                     '^Memory address bits must be specified as positive non-zero integer' ) :
            self.thisSpace.addressBits = 0


    def testSetMemoryAddressBitsLessThanBaseAddressRaises( self ) :
        self.thisSpace.baseAddress = 20
        expectedMemoryAddressBits = 4

        with self.assertRaisesRegex( rmm.ConfigurationError,
                                     '^Addressable memory must be greater than the base address' ) :
            self.thisSpace.addressBits = expectedMemoryAddressBits


    def testNonePageSizeNoNotifyOnChange( self ) :
        self.assertIsNone( self.thisSpace.pageSize )
        self.assertEqual( self.observer.updateCount, 0 )

        self.thisSpace.addressBits = 16

        self.assertEqual( self.observer.updateCount, 0 )


    def testAssignedPageSizeNotifyOnChange( self ) :
        self.thisSpace.pageSize = 0x80
        # One notification for the page size change
        self.assertEqual( self.observer.updateCount, 1 )
        self.assertEqual( self.observer.arguments, 'pageSize' )

        self.thisSpace.addressBits = 16

        self.assertEqual( self.observer.updateCount, 2 )
        self.assertEqual( self.observer.arguments, 'addressBits' )


class TestMemoryUnit( unittest.TestCase ) :
    def setUp( self ) :
        self.thisSpace = rmm.MemorySpace( )

        self.observer = MockObserver( )
        self.thisSpace.addressChangeNotifier.addObserver( self.observer )


    def testDefaultMemoryUnitBits( self ) :
        expectedMemoryUnitBits = 8
        actualMemoryUnitBits = self.thisSpace.memoryUnitBits

        self.assertTrue( isinstance( actualMemoryUnitBits, int ) )
        self.assertEqual( actualMemoryUnitBits, expectedMemoryUnitBits )


    def testDirectAssignment( self ) :
        expectedValue = 16
        self.assertNotEqual( expectedValue, self.thisSpace.memoryUnitBits )

        self.thisSpace.memoryUnitBits = expectedValue

        self.assertEqual( self.thisSpace.memoryUnitBits, expectedValue )


    def testNonIntRaises( self ) :
        with self.assertRaisesRegex( rmm.ConfigurationError,
                                     '^Memory unit bits must be specified as positive non-zero integer' ) :
            self.thisSpace.memoryUnitBits = '5'


    def testZeroRaises( self ) :
        with self.assertRaisesRegex( rmm.ConfigurationError,
                                     '^Memory unit bits must be specified as positive non-zero integer' ) :
            self.thisSpace.memoryUnitBits = 0


    def testNegativeRaises( self ) :
        with self.assertRaisesRegex( rmm.ConfigurationError,
                                     '^Memory unit bits must be specified as positive non-zero integer' ) :
            self.thisSpace.memoryUnitBits = -1


    def testNonePageSizeNoNotifyOnChange( self ) :
        self.assertIsNone( self.thisSpace.pageSize )
        self.assertEqual( self.observer.updateCount, 0 )

        self.thisSpace.memoryUnitBits = 16

        self.assertEqual( self.observer.updateCount, 0 )


    def testAssignedPageSizeNotifyOnChange( self ) :
        self.thisSpace.pageSize = 0x80
        # One notification for the page size change
        self.assertEqual( self.observer.updateCount, 1 )
        self.assertEqual( self.observer.arguments, 'pageSize' )

        self.thisSpace.memoryUnitBits = 16

        self.assertEqual( self.observer.updateCount, 2 )
        self.assertEqual( self.observer.arguments, 'memoryUnitBits' )


class TestPageSize( unittest.TestCase ) :
    def setUp( self ) :
        self.thisSpace = rmm.MemorySpace( )

        self.observer = MockObserver( )
        self.thisSpace.addressChangeNotifier.addObserver( self.observer )


    def testDefaultPageSize( self ) :
        actualPageSize = self.thisSpace.pageSize

        self.assertIsNone( actualPageSize )


    def testPageSizeAssignment( self ) :
        expectedPageSize = 128

        self.assertNotEqual( expectedPageSize, self.thisSpace.pageSize )

        self.thisSpace.pageSize = expectedPageSize
        actualPageSize = self.thisSpace.pageSize

        self.assertEqual( actualPageSize, expectedPageSize )


    def testNonIntRaises( self ) :
        with self.assertRaisesRegex( rmm.ConfigurationError, '^Page size must be specified as integer' ) :
            self.thisSpace.pageSize = '5'


    def testNoneOkay( self ) :
        self.thisSpace.pageSize = None

        self.assertIsNone( self.thisSpace.pageSize )


    def testPageSizeLessThanMemoryAddressRaises( self ) :
        expectedPageSize = 3

        self.assertEqual( self.thisSpace.memoryUnitBits, 8 )
        self.assertEqual( self.thisSpace.addressBits, 32 )

        with self.assertRaisesRegex( rmm.ConfigurationError, '^Bad page size' ) :
            self.thisSpace.pageSize = expectedPageSize


    def testChangePageSizeNotifiesObserver( self ) :
        self.assertEqual( self.observer.updateCount, 0 )

        self.thisSpace.pageSize = 0x80

        self.assertEqual( self.observer.updateCount, 1 )
        self.assertEqual( self.observer.arguments, 'pageSize' )


class TestPageRegisters( unittest.TestCase ) :
    def setUp( self ) :
        self.thisSpace = rmm.MemorySpace( )


    def testPageRegisters( self ) :
        self.thisSpace.addressBits = 32
        self.thisSpace.memoryUnitBits = 8

        expectedNumberPageRegisters = int( self.thisSpace.addressBits / self.thisSpace.memoryUnitBits )

        self.thisSpace.pageSize = 0x80
        expectedPageRegisterTest = [ True, True, True, True, False, False ]
        actualPageRegisterTest = list( )
        for offset in range( expectedNumberPageRegisters, 0, -1 ) :
            thisAddress = (self.thisSpace.pageSize * 3) - offset

            actualPageRegisterTest.append( self.thisSpace.isPageRegister( thisAddress ) )

        actualPageRegisterTest.append( self.thisSpace.isPageRegister( 5 * self.thisSpace.pageSize ) )
        actualPageRegisterTest.append( self.thisSpace.isPageRegister( (self.thisSpace.pageSize * 4) - 5 ) )

        self.assertEqual( actualPageRegisterTest, expectedPageRegisterTest )


    def testPageBaseAddress( self ) :
        self.thisSpace.pageSize = 0x80

        expectedPageBaseAddresses = [
            self.thisSpace.pageSize * 2,
            self.thisSpace.pageSize * 4,
            self.thisSpace.pageSize * 7
        ]

        testAddresses = [
            expectedPageBaseAddresses[ 0 ],
            expectedPageBaseAddresses[ 1 ] + 0x7f,
            expectedPageBaseAddresses[ 2 ] + 3
        ]

        for thisAddress, pageBaseAddress in zip( testAddresses, expectedPageBaseAddresses ) :
            actualPageBaseAddress = self.thisSpace.pageBaseAddress( thisAddress )

            self.assertEqual( actualPageBaseAddress, pageBaseAddress )


class TestCalculatePageRegisterImpact( unittest.TestCase ) :
    def setUp( self ) :
        self.thisSpace = rmm.MemorySpace( )
        self.thisSpace.pageSize = 0x80


    def testNoShiftNonPageRegister( self ) :
        self.assertEqual( self.thisSpace.addressBits, 32 )
        self.assertEqual( self.thisSpace.memoryUnitBits, 8 )

        expectedAddress = 0x27b
        actualAddress = self.thisSpace.calculatePageRegisterImpact( expectedAddress )

        self.assertEqual( actualAddress, expectedAddress )


    def testShiftOnPageRegister( self ) :
        self.assertEqual( self.thisSpace.addressBits, 32 )
        self.assertEqual( self.thisSpace.memoryUnitBits, 8 )

        expectedAddress = 0x400
        inputAddress = 0x3fc
        actualAddress = self.thisSpace.calculatePageRegisterImpact( inputAddress )

        self.assertEqual( actualAddress, expectedAddress )


class TestYamlLoadSave( unittest.TestCase ) :
    def setUp( self ) :
        self.thisSpace = rmm.MemorySpace( )


    def testEncodeDecode( self ) :
        encodedYamlData = self.thisSpace.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedMemorySpace = rmm.MemorySpace.from_yamlData( encodedYamlData )

        self.assertEqual( decodedMemorySpace.addressBits, self.thisSpace.addressBits )
        self.assertEqual( decodedMemorySpace.baseAddress, self.thisSpace.baseAddress )
        self.assertEqual( decodedMemorySpace.memoryUnitBits, self.thisSpace.memoryUnitBits )
        self.assertEqual( decodedMemorySpace.pageSize, self.thisSpace.pageSize )


    def testNonDefaultValues( self ) :
        self.thisSpace.baseAddress = 0x10
        self.thisSpace.addressBits = 24
        self.thisSpace.memoryUnitBits = 16
        self.thisSpace.pageSize = 128

        encodedYamlData = self.thisSpace.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedMemorySpace = rmm.MemorySpace.from_yamlData( encodedYamlData )

        self.assertEqual( decodedMemorySpace.addressBits, self.thisSpace.addressBits )
        self.assertEqual( decodedMemorySpace.baseAddress, self.thisSpace.baseAddress )
        self.assertEqual( decodedMemorySpace.memoryUnitBits, self.thisSpace.memoryUnitBits )
        self.assertEqual( decodedMemorySpace.pageSize, self.thisSpace.pageSize )


    def testOptionalAddressBits( self ) :
        yamlData = { 'memorySpace' : { 'baseAddress' : 0x10,
                                       'memoryUnitBits' : 16,
                                       'pageSizeMemoryUnits' : 128 } }
        decodedMemorySpace = rmm.MemorySpace.from_yamlData( yamlData )

        self.assertEqual( decodedMemorySpace.addressBits, 32 )
        self.assertEqual( decodedMemorySpace.baseAddress, 0x10 )
        self.assertEqual( decodedMemorySpace.memoryUnitBits, 16 )
        self.assertEqual( decodedMemorySpace.pageSize, 128 )


    def testOptionalBaseAddress( self ) :
        yamlData = { 'memorySpace' : { 'addressBits' : 24,
                                       'memoryUnitBits' : 16,
                                       'pageSizeMemoryUnits' : 128 } }
        decodedMemorySpace = rmm.MemorySpace.from_yamlData( yamlData )

        self.assertEqual( decodedMemorySpace.addressBits, 24 )
        self.assertEqual( decodedMemorySpace.baseAddress, 0 )
        self.assertEqual( decodedMemorySpace.memoryUnitBits, 16 )
        self.assertEqual( decodedMemorySpace.pageSize, 128 )


    def testOptionalMemoryUnitBits( self ) :
        yamlData = { 'memorySpace' : { 'addressBits' : 24,
                                       'baseAddress' : 0x10,
                                       'pageSizeMemoryUnits' : 128 } }
        decodedMemorySpace = rmm.MemorySpace.from_yamlData( yamlData )

        self.assertEqual( decodedMemorySpace.addressBits, 24 )
        self.assertEqual( decodedMemorySpace.baseAddress, 0x10 )
        self.assertEqual( decodedMemorySpace.memoryUnitBits, 8 )
        self.assertEqual( decodedMemorySpace.pageSize, 128 )


    def testOptionalPageSizeMemoryUnits( self ) :
        yamlData = { 'memorySpace' : { 'addressBits' : 24,
                                       'memoryUnitBits' : 16,
                                       'baseAddress' : 0x10 } }
        decodedMemorySpace = rmm.MemorySpace.from_yamlData( yamlData )

        self.assertEqual( decodedMemorySpace.addressBits, 24 )
        self.assertEqual( decodedMemorySpace.baseAddress, 0x10 )
        self.assertEqual( decodedMemorySpace.memoryUnitBits, 16 )
        self.assertIsNone( decodedMemorySpace.pageSize )


if __name__ == '__main__' :
    unittest.main( )
