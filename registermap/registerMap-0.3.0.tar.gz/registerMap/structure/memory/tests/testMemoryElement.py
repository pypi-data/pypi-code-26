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

from registerMap.exceptions import ConfigurationError

from ..element import AddressableMemoryElement, Size
from ..space import MemorySpace


log = logging.getLogger( __name__ )


class TestDefaultConstructor( unittest.TestCase ) :

    def setUp( self ) :
        self.memory = MemorySpace()


    def testDefaultArguments( self ) :
        testElement = AddressableMemoryElement( self.memory )

        self.assertIsNone( testElement.startAddress )
        self.assertIsNone( testElement.endAddress )
        self.assertEqual( 1, testElement.sizeMemoryUnits )


    def testAssignStartAddressWithNoneSizeEnd( self ) :
        testElement = AddressableMemoryElement( self.memory )

        testElement.startAddress = 2
        testElement.sizeMemoryUnits = None

        self.assertEqual( 2, testElement.startAddress )
        self.assertIsNone( testElement.endAddress )
        self.assertIsNone( testElement.sizeMemoryUnits )


    def testNoneSizeEndThenAssignStartAddress( self ) :
        testElement = AddressableMemoryElement( self.memory )

        testElement.sizeMemoryUnits = None
        testElement.startAddress = 2

        self.assertEqual( 2, testElement.startAddress )
        self.assertIsNone( testElement.endAddress )
        self.assertIsNone( testElement.sizeMemoryUnits )


    def testValidStartAddressArgument( self ) :
        expectedValue = 0x10
        testElement = AddressableMemoryElement( self.memory,
                                                startAddress = expectedValue )

        self.assertEqual( expectedValue, testElement.startAddress )
        self.assertEqual( expectedValue, testElement.endAddress )
        self.assertEqual( 1, testElement.sizeMemoryUnits )


    def testValidStartEndAddressArguments( self ) :
        expectedStartAddress = 0x10
        expectedEndAddress = 0x15
        testElement = AddressableMemoryElement( self.memory,
                                                startAddress = expectedStartAddress,
                                                endAddress = expectedEndAddress )

        self.assertEqual( expectedStartAddress, testElement.startAddress )
        self.assertEqual( expectedEndAddress, testElement.endAddress )
        self.assertEqual( (expectedEndAddress - expectedStartAddress + 1), testElement.sizeMemoryUnits )


    def testValidStartAddressSizeArguments( self ) :
        expectedStartAddress = 0x10
        expectedSize = 5
        testElement = AddressableMemoryElement( self.memory,
                                                startAddress = expectedStartAddress,
                                                sizeMemoryUnits = expectedSize )

        self.assertEqual( expectedStartAddress, testElement.startAddress )
        self.assertEqual( expectedSize, testElement.sizeMemoryUnits )
        self.assertEqual( (expectedStartAddress + expectedSize - 1), testElement.endAddress )


    def testSpecifyBothEndAddressAndSizeRaises( self ) :
        with self.assertRaisesRegex( ConfigurationError, '^Cannot specify both endAddress and sizeMemoryUnits' ) :
            AddressableMemoryElement( self.memory,
                                      endAddress = 4,
                                      sizeMemoryUnits = 6 )


    def testSizeObjectNonDefaultSizeNoneStart( self ) :
        expectedSize = 10
        size = Size()
        size.value = expectedSize

        elementUnderTest = AddressableMemoryElement( self.memory,
                                                     sizeObject = size )

        self.assertEqual( expectedSize, elementUnderTest.sizeMemoryUnits )


    def testSizeObjectNonDefaultSizeNumericStart( self ) :
        expectedSize = 10
        size = Size()
        size.value = expectedSize

        elementUnderTest = AddressableMemoryElement( self.memory,
                                                     sizeObject = size,
                                                     startAddress = 0x10 )

        self.assertEqual( expectedSize, elementUnderTest.sizeMemoryUnits )


class TestMemoryElementOffset( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()
        self.memory.baseAddress = 0x2010

        self.elementUnderTest = AddressableMemoryElement( self.memory )


    def testDefaultValue( self ) :
        self.assertIsNone( self.elementUnderTest.offset )


    def testOffset( self ) :
        self.elementUnderTest.startAddress = 0x21e4

        expectedValue = self.elementUnderTest.startAddress - self.memory.baseAddress

        self.assertEqual( expectedValue, self.elementUnderTest.offset )


class TestMemoryElementStartAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()
        self.testElement = AddressableMemoryElement( self.memory )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testElement.startAddress )


    def testAssignValueNoSize( self ) :
        expectedValue = 0x10
        self.assertNotEqual( self.testElement.startAddress, expectedValue )

        self.testElement.startAddress = expectedValue

        self.assertEqual( expectedValue, self.testElement.startAddress )
        self.assertEqual( self.testElement.endAddress, self.testElement.startAddress )


    def testAssignValueSizeDefined( self ) :
        self.testElement.sizeMemoryUnits = 5

        expectedStartAddress = 0x10
        self.assertNotEqual( expectedStartAddress, self.testElement.startAddress )
        expectedEndAddress = 0x14
        self.assertNotEqual( expectedEndAddress, self.testElement.endAddress )

        self.testElement.startAddress = expectedStartAddress

        self.assertEqual( expectedStartAddress, self.testElement.startAddress )
        self.assertEqual( expectedEndAddress, self.testElement.endAddress )


    def testAssignValueWithEndAddress( self ) :
        initialStartAddress = 0x10
        self.assertNotEqual( initialStartAddress, self.testElement.startAddress )

        self.testElement.startAddress = initialStartAddress
        self.testElement.sizeMemoryUnits = 5

        expectedStartAddress = 0x10
        self.testElement.startAddress = expectedStartAddress

        log.debug( 'Size after start address change: ' + repr( self.testElement.sizeMemoryUnits ) )

        self.assertEqual( expectedStartAddress, self.testElement.startAddress )
        self.assertEqual( (expectedStartAddress + self.testElement.sizeMemoryUnits - 1), self.testElement.endAddress )


    def testUnassignedStartAddressRaises( self ) :
        testElement = AddressableMemoryElement( self.memory )
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Must define start address before attempting to define end address' ) :
            testElement.endAddress = 0x5


    def testAssignNone( self ) :
        expectedValue = 0x10
        self.testElement.startAddress = expectedValue
        self.assertEqual( expectedValue, self.testElement.startAddress )

        self.testElement.startAddress = None

        self.assertIsNone( self.testElement.startAddress )
        self.assertIsNone( self.testElement.endAddress )


class TestMemoryElementEndAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()
        self.testElement = AddressableMemoryElement( self.memory )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testElement.endAddress )


    def testAssignValue( self ) :
        self.testElement.startAddress = 0x10
        expectedEndAddress = 0x20
        self.assertNotEqual( expectedEndAddress, self.testElement.endAddress )

        self.testElement.endAddress = expectedEndAddress

        self.assertEqual( expectedEndAddress, self.testElement.endAddress )
        self.assertEqual( (expectedEndAddress - self.testElement.startAddress + 1), self.testElement.sizeMemoryUnits )


class TestMemoryElementSize( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()
        self.testElement = AddressableMemoryElement( self.memory )


    def testDefaultValue( self ) :
        self.assertEqual( 1, self.testElement.sizeMemoryUnits )


    def testValueAfterInitialStartAddressAssign( self ) :
        self.testElement.startAddress = 0x10

        self.assertEqual( 1, self.testElement.sizeMemoryUnits )


    def testAssignValue( self ) :
        self.testElement.startAddress = 0x10
        expectedSize = 5
        self.assertNotEqual( expectedSize, self.testElement.sizeMemoryUnits )

        self.testElement.sizeMemoryUnits = expectedSize

        self.assertEqual( expectedSize, self.testElement.sizeMemoryUnits )
        self.assertEqual( (self.testElement.startAddress + self.testElement.sizeMemoryUnits - 1),
                          self.testElement.endAddress )


    def testPrematureAssignmentNoRaise( self ) :
        self.assertIsNone( self.testElement.startAddress )
        self.assertIsNone( self.testElement.endAddress )

        expectedValue = 5
        self.testElement.sizeMemoryUnits = expectedValue

        self.assertEqual( expectedValue, self.testElement.sizeMemoryUnits )


class TestMemoryElementSizeProperty( unittest.TestCase ) :

    def setUp( self ) :
        self.memory = MemorySpace()
        self.elementUnderTest = AddressableMemoryElement( self.memory )


    def testSizeObject( self ) :
        actualSize = self.elementUnderTest.size

        self.assertEqual( 1, actualSize.value )

        actualSize.value = 10

        self.assertEqual( self.elementUnderTest.sizeMemoryUnits, actualSize.value )


if __name__ == '__main__' :
    unittest.main()
