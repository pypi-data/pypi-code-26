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
import unittest.mock

from registerMap.elements.module import Module
from registerMap.elements.tests.mockObserver import MockObserver
from registerMap.exceptions import ConstraintError
from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace

from registerMap.elements.register.tests.mocks import MockPreviousRegister

from ..instance import RegisterInstance


log = logging.getLogger( __name__ )


class TestRegisterAddressPreviousNoneAddress( unittest.TestCase ) :
    """
    Test register address when the previous address has no defined address or size.
    """


    def setUp( self ) :
        self.observer = MockObserver()
        self.previousRegister = MockPreviousRegister()
        self.testBitFieldSet = SetCollection()
        self.testSpace = MemorySpace()
        self.registerUnderTest = RegisterInstance( self.testSpace,
                                                   setCollection = self.testBitFieldSet )

        self.registerUnderTest.previousElement = self.previousRegister

        self.registerUnderTest.sizeChangeNotifier.addObserver( self.observer )
        self.registerUnderTest.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.registerUnderTest.address )
        self.assertIsNone( self.registerUnderTest.endAddress )


    def testFixedAddress( self ) :
        expectedValue = 0x15

        self.assertNotEqual( self.registerUnderTest.address, expectedValue )

        self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = expectedValue

        self.assertEqual( expectedValue, self.registerUnderTest.address )
        self.assertEqual( expectedValue, self.registerUnderTest.endAddress )
        self.assertEqual( self.observer.updateCount, 1 )


    def testAlignedAddress( self ) :
        alignmentValue = 2

        self.registerUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = alignmentValue

        # Attempt to constrain alignment with no concrete addresses does nothing
        self.assertIsNone( self.registerUnderTest.address )
        self.assertIsNone( self.registerUnderTest.endAddress )
        self.assertEqual( self.observer.updateCount, 0 )


class TestRegisterAddressPreviousConcreteAddress( unittest.TestCase ) :
    """
    Test register address when the previous register has concrete address and size.
    """


    def setUp( self ) :
        self.observer = MockObserver()
        self.previousRegister = MockPreviousRegister( startAddress = 0x10,
                                                      sizeMemoryUnits = 5 )
        self.testBitFieldSet = SetCollection()
        self.testSpace = MemorySpace()
        self.registerUnderTest = RegisterInstance( self.testSpace,
                                                   setCollection = self.testBitFieldSet )

        self.registerUnderTest.previousElement = self.previousRegister

        self.registerUnderTest.sizeChangeNotifier.addObserver( self.observer )
        self.registerUnderTest.addressChangeNotifier.addObserver( self.observer )


    def testFixedAddress( self ) :
        expectedValue = 0x16

        self.assertEqual( 1, self.registerUnderTest.sizeMemoryUnits )
        self.assertNotEqual( self.registerUnderTest.address, expectedValue )

        self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = expectedValue

        self.assertEqual( expectedValue, self.registerUnderTest.address )
        self.assertEqual( expectedValue, self.registerUnderTest.endAddress )
        self.assertEqual( self.observer.updateCount, 1 )


    def testFixedAddressOnPreviousRaises( self ) :
        expectedValue = self.previousRegister.endAddress

        with self.assertRaisesRegex( ConstraintError, '^Fixed address exceeded' ) :
            self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = expectedValue


    def testAlignedAddress( self ) :
        alignmentValue = 2
        expectedValue = self.previousRegister.endAddress + 2

        self.assertEqual( 1, self.registerUnderTest.sizeMemoryUnits )
        self.assertEqual( 0, (expectedValue % alignmentValue) )
        self.assertLess( self.registerUnderTest.address, expectedValue )

        self.registerUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = alignmentValue

        self.assertEqual( expectedValue, self.registerUnderTest.address )
        self.assertEqual( expectedValue, self.registerUnderTest.endAddress )
        self.assertEqual( self.observer.updateCount, 1 )


    def testEndAddressMultipleMemoryUnits( self ) :
        f1 = self.registerUnderTest.addField( 'f1', (0, 10) )

        self.assertLess( 1, self.registerUnderTest.sizeMemoryUnits )

        startAddress = self.registerUnderTest.address

        expectedEndAddress = startAddress + self.registerUnderTest.sizeMemoryUnits - 1

        self.assertEqual( expectedEndAddress, self.registerUnderTest.endAddress )


    def testEndAddressMultipleFieldsSameSize( self ) :
        def checkExpectedEndAddress():
            startAddress = self.registerUnderTest.address

            expectedEndAddress = startAddress + self.registerUnderTest.sizeMemoryUnits - 1

            self.assertEqual( expectedEndAddress, self.registerUnderTest.endAddress )

        self.registerUnderTest.addField( 'f1', (0, 3) )
        self.assertEqual( 1, self.registerUnderTest.sizeMemoryUnits )

        checkExpectedEndAddress()

        # Add a second field that doesn't change the size of the register.
        self.registerUnderTest.addField( 'f2', (5, 7) )
        self.assertEqual( 1, self.registerUnderTest.sizeMemoryUnits )

        checkExpectedEndAddress()


    def testEndAddressMultipleMemoryUnitsMultipleFields( self ) :
        def checkExpectedEndAddress():
            startAddress = self.registerUnderTest.address

            expectedEndAddress = startAddress + self.registerUnderTest.sizeMemoryUnits - 1

            self.assertEqual( expectedEndAddress, self.registerUnderTest.endAddress )

        self.registerUnderTest.addField( 'f1', (0, 5) )
        self.assertEqual( 1, self.registerUnderTest.sizeMemoryUnits )

        checkExpectedEndAddress()

        # Add an adjacent field that extends to a second memory unit.
        self.registerUnderTest.addField( 'f2', (6, 10) )
        self.assertEqual( 2, self.registerUnderTest.sizeMemoryUnits )

        checkExpectedEndAddress()

        # Add a field with a gap that extends to a third memory unit.
        self.registerUnderTest.addField( 'f3', (15, 18) )
        self.assertEqual( 3, self.registerUnderTest.sizeMemoryUnits )

        checkExpectedEndAddress()


class TestRegisterPageRegisterInteraction( unittest.TestCase ) :
    def setUp( self ) :
        self.testBitFieldSet = SetCollection()
        self.testSpace = MemorySpace()
        self.registerUnderTest = RegisterInstance( self.testSpace,
                                                   setCollection = self.testBitFieldSet )

        self.previousRegister = MockPreviousRegister( startAddress = 0,
                                                      sizeMemoryUnits = 4 )
        self.registerUnderTest.previousElement = self.previousRegister


    def testPageSize( self ) :
        self.assertEqual( 32, self.testSpace.addressBits )
        self.assertEqual( 8, self.testSpace.memoryUnitBits )

        self.previousRegister.address = 0x278

        log.debug( 'Mock previous register start address: ' + hex( self.previousRegister.address ) )
        log.debug( 'Mock previous register end address: ' + hex( self.previousRegister.endAddress ) )
        self.assertEqual( 0x278, self.previousRegister.address )
        log.debug( 'Test register start address no page size: ' + hex( self.registerUnderTest.address ) )
        log.debug( 'Test register end address no page size: ' + hex( self.registerUnderTest.endAddress ) )
        self.assertEqual( 0x27c, self.registerUnderTest.address )

        self.testSpace.pageSize = 0x80
        log.debug( 'Test register start address page size {0}: {1}'.format(
            hex( self.testSpace.pageSize ),
            hex( self.registerUnderTest.address ) ) )
        log.debug( 'Test register end address page size {0}: {1}'.format(
            hex( self.testSpace.pageSize ),
            hex( self.registerUnderTest.endAddress ) ) )
        self.assertEqual( 0x280, self.registerUnderTest.address )


class TestRegisterPreviousRegister( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.testBitFieldSet = SetCollection()
        self.testSpace = MemorySpace()
        self.registerUnderTest = RegisterInstance( self.testSpace,
                                                   setCollection = self.testBitFieldSet )

        self.registerUnderTest.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.registerUnderTest.previousElement )


    def testPreviousRegisterAssign( self ) :
        expectedValue = 0x10
        self.registerUnderTest.previousElement = MockPreviousRegister( startAddress = 0x5,
                                                                       endAddress = (expectedValue - 1) )

        self.assertEqual( expectedValue, self.registerUnderTest.address )


    def testUnassignedPreviousRegisterNoneAddress( self ) :
        fixedAddress = 0x10
        self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = fixedAddress

        self.assertEqual( fixedAddress, self.registerUnderTest.address )


    def testUnassignedEndAddress( self ) :
        self.registerUnderTest.previousElement = MockPreviousRegister()

        actualAddress = self.registerUnderTest.address
        self.assertIsNone( actualAddress )


    def testAssignPreviousRegisterEndAddress( self ) :
        self.registerUnderTest.previousElement = MockPreviousRegister( startAddress = 0x5 )

        self.assertIsNone( self.registerUnderTest.address )

        expectedAddress = 0x10
        self.registerUnderTest.previousElement.endAddress = expectedAddress - 1

        actualAddress = self.registerUnderTest.address
        self.assertEqual( expectedAddress, actualAddress )


class TestRegisterOffset( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.previousRegister = MockPreviousRegister()
        self.testBitFieldSet = SetCollection()
        self.testSpace = MemorySpace()
        self.testSpace.baseAddress = 0x20f0

        self.registerUnderTest = RegisterInstance( self.testSpace,
                                                   setCollection = self.testBitFieldSet )

        self.registerUnderTest.previousElement = self.previousRegister

        self.registerUnderTest.sizeChangeNotifier.addObserver( self.observer )
        self.registerUnderTest.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.registerUnderTest.offset )


    def testDataAssignment( self ) :
        expectedValue = 0xde
        inputValue = self.testSpace.baseAddress + expectedValue

        self.assertNotEqual( expectedValue, self.registerUnderTest.offset )

        self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = inputValue

        self.assertEqual( inputValue, self.registerUnderTest.address )

        self.assertEqual( expectedValue, self.registerUnderTest.offset )


class TestRegisterModuleOffset( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.previousRegister = MockPreviousRegister()
        self.testBitFieldSet = SetCollection()
        self.testSpace = MemorySpace()
        self.testSpace.baseAddress = 0x20f0
        self.mockModule = unittest.mock.create_autospec(Module)
        self.mockModule.baseAddress = 0x21f0

        self.registerUnderTest = RegisterInstance( self.testSpace,
                                                   parent = self.mockModule,
                                                   setCollection = self.testBitFieldSet )

        self.registerUnderTest.previousElement = self.previousRegister

        self.registerUnderTest.sizeChangeNotifier.addObserver( self.observer )
        self.registerUnderTest.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.registerUnderTest.offset )


    def testDataAssignment( self ) :
        expectedValue = 0xde
        inputValue = self.mockModule.baseAddress + expectedValue

        self.assertNotEqual( expectedValue, self.registerUnderTest.moduleOffset )

        self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = inputValue

        self.assertEqual( inputValue, self.registerUnderTest.address )

        self.assertEqual( expectedValue, self.registerUnderTest.moduleOffset )


if __name__ == '__main__' :
    unittest.main()
