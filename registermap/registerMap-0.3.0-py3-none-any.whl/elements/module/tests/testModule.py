"""
Unit test Module class
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

from registerMap.exceptions import ConstraintError
from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace

from registerMap.elements.tests.mockObserver import MockObserver

from ..module import \
    Module, \
    RegistersParameter

from .mocks import MockPreviousModule


log = logging.getLogger( __name__ )


class TestFirstRegister( unittest.TestCase ) :

    def setUp( self ) :
        pass


    def testGetEndAddressProperty( self ) :
        expectedValue = 0x10
        firstRegister = RegistersParameter.FirstRegister( endAddress = expectedValue )
        self.assertEqual( expectedValue, firstRegister.endAddress )


    def testSetEndAddressProperty( self ) :
        expectedValue = 0x10
        firstRegister = RegistersParameter.FirstRegister( endAddress = 0x20 )
        self.assertNotEqual( firstRegister.endAddress, expectedValue )

        firstRegister.endAddress = expectedValue

        self.assertEqual( expectedValue, firstRegister.endAddress )


class TestModule( unittest.TestCase ) :

    def setUp( self ) :
        self.observer = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testModule = Module( self.testSpace, self.setCollection )
        self.testModule[ 'name' ] = 'module'

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultMemory( self ) :
        self.assertEqual( 8, self.testModule.memory.memoryUnitBits )

        self.assertIsNone( self.testModule.baseAddress )
        self.assertIsNone( self.testModule.previousElement )
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 0, self.testModule.assignedMemoryUnits )


    def testAddSingleRegister( self ) :
        self.assertEqual( 8, self.testModule.memory.memoryUnitBits )

        r = self.testModule.addRegister( 'r1' )

        self.assertIsNone( self.testModule.baseAddress )
        self.assertIsNone( self.testModule.previousElement )
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 1, self.testModule.assignedMemoryUnits )
        self.assertEqual( 'module.r1', r.canonicalId )


    def testReviewAddressChangeEmptyModule( self ) :
        testModule = Module( self.testSpace, self.setCollection )

        self.assertEqual( 0, len( testModule[ 'registers' ] ) )

        # No exceptions should be thrown
        testModule.reviewAddressChange()

        self.assertIsNone( testModule.baseAddress )


    def testReviewAddressChangeEmptyModuleFromYaml( self ) :
        testModule = Module( self.testSpace, self.setCollection )

        self.assertEqual( 0, len( testModule[ 'registers' ] ) )

        yamlData = testModule.to_yamlData()
        generatedModule = Module.from_yamlData( yamlData, self.testSpace, self.setCollection )

        # No exceptions should be thrown
        generatedModule.reviewAddressChange()

        self.assertIsNone( generatedModule.baseAddress )


class TestModuleWithPreviousModule( unittest.TestCase ) :

    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x10 )
        self.observer = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testModule = Module( self.testSpace, self.setCollection )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultMemory( self ) :
        self.assertEqual( 8, self.testModule.memory.memoryUnitBits )

        self.assertEqual( (self.previousModule.endAddress + 1), self.testModule.baseAddress )
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 0, self.testModule.assignedMemoryUnits )


    def testAddSingleRegister( self ) :
        self.assertEqual( 8, self.testModule.memory.memoryUnitBits )

        self.testModule.addRegister( 'r1' )

        self.assertEqual( (self.previousModule.endAddress + 1), self.testModule.baseAddress )
        self.assertEqual( 1, self.testModule.spanMemoryUnits )
        self.assertEqual( 1, self.testModule.assignedMemoryUnits )


class TestModuleConstraints( unittest.TestCase ) :

    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x10 )
        self.observer = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testModule = Module( self.testSpace, self.setCollection )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testFixedAddress( self ) :
        expectedValue = 0x15

        self.assertGreater( expectedValue, self.previousModule.endAddress )
        self.assertNotEqual( expectedValue, self.testModule.baseAddress )

        self.testModule[ 'constraints' ][ 'fixedAddress' ] = expectedValue

        self.assertEqual( expectedValue, self.testModule.baseAddress )


    def testAlignedAddress( self ) :
        alignmentValue = 2
        expectedValue = self.previousModule.endAddress + 2

        self.assertEqual( 0, (expectedValue % alignmentValue) )
        self.assertLess( self.testModule.baseAddress, expectedValue )

        self.assertNotEqual( expectedValue, self.testModule.baseAddress )

        self.testModule[ 'constraints' ][ 'alignmentMemoryUnits' ] = alignmentValue

        self.assertEqual( expectedValue, self.testModule.baseAddress )


    def testAddRegisterOverFixedSizeRaises( self ) :
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 0, self.testModule.assignedMemoryUnits )
        self.assertEqual( 8, self.testSpace.memoryUnitBits )

        self.testModule[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = 3

        r1 = self.testModule.addRegister( 'r1' )
        r1.addField( 'f1', [ 0, 10 ], (0, 10) )
        self.testModule.addRegister( 'r2' )

        self.assertEqual( 3, self.testModule.spanMemoryUnits )

        with self.assertRaisesRegex( ConstraintError, '^Fixed size exceeded' ) :
            # A register has a size of one memory unit even if it has no bit fields.
            # So adding a third register must exceed the size limit
            self.testModule.addRegister( 'r3' )


class TestModuleDescription( unittest.TestCase ) :

    def setUp( self ) :
        self.observer = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testModule = Module( self.testSpace, self.setCollection )

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertEqual( '', self.testModule[ 'description' ] )


class TestModuleName( unittest.TestCase ) :

    def setUp( self ) :
        self.observer = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testModule = Module( self.testSpace, self.setCollection )

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testModule[ 'name' ] )


class TestModuleOffsetProperty( unittest.TestCase ) :

    def setUp( self ) :
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()

        self.moduleUnderTest = Module( self.testSpace, self.setCollection )

        self.moduleUnderTest.addRegister( 'r1' )


    def testDefault( self ) :
        self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0

        self.assertEqual( 0, self.testSpace.baseAddress )

        self.assertEqual( 0, self.moduleUnderTest.offset )


    def testAddressChanged( self ) :
        self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x1e5

        self.assertEqual( 0, self.testSpace.baseAddress )

        self.assertEqual( 0x1e5, self.moduleUnderTest.offset )


class TestModulePageRegisterInteraction( unittest.TestCase ) :

    def setUp( self ) :
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testModule = Module( self.testSpace, self.setCollection )

        self.previousModule = MockPreviousModule( endAddress = 0 )
        self.testModule.previousElement = self.previousModule


    def testModuleOnPageRegister( self ) :
        self.assertEqual( 32, self.testSpace.addressBits )
        self.assertEqual( 8, self.testSpace.memoryUnitBits )

        self.previousModule.endAddress = 0x27b

        log.debug( 'Mock previous module end address: ' + hex( self.previousModule.endAddress ) )
        self.assertEqual( 0x27b, self.previousModule.endAddress )
        log.debug( 'Test module start address no page size: ' + hex( self.testModule.baseAddress ) )
        log.debug( 'Test module end address no page size: ' + hex( self.testModule.endAddress ) )
        self.assertEqual( 0x27c, self.testModule.baseAddress )

        self.testSpace.pageSize = 0x80
        log.debug( 'Test module start address page size {0}: {1}'.format(
            hex( self.testSpace.pageSize ),
            hex( self.testModule.baseAddress ) ) )
        log.debug( 'Test module end address page size {0}: {1}'.format(
            hex( self.testSpace.pageSize ),
            hex( self.testModule.endAddress ) ) )
        self.assertEqual( 0x280, self.testModule.baseAddress )


class TestModulePreviousModule( unittest.TestCase ) :

    def setUp( self ) :
        self.observer = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testModule = Module( self.testSpace, self.setCollection )

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testModule.previousElement )


    def testAssignPreviousModuleNoneEndAddress( self ) :
        previousModule = MockPreviousModule()
        self.testModule.previousElement = previousModule

        self.assertIsNone( self.testModule.endAddress )


    def testUpdatePreviousModuleEndAddress( self ) :
        previousModule = MockPreviousModule()
        self.testModule.previousElement = previousModule

        expectedAddress = 0x10
        previousModule.endAddress = expectedAddress - 1

        self.assertEqual( self.testModule.baseAddress, expectedAddress )


class TestModuleSizePreviousConcreteAddresses( unittest.TestCase ) :

    # Module size is the number of memory units spanned by registers from the lowest memory unit to the highest
    # memory unit.
    # - If a module has a fixed address then the lowest memory unit is always the fixed address.
    # - If a page size is specified, then register addresses must miss paging registers (a fixed address on a page
    # register must raise).
    def setUp( self ) :
        self.observer = MockObserver()
        self.previousModule = MockPreviousModule( endAddress = 0x10 )
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testModule = Module( self.testSpace, self.setCollection )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 0, self.testModule.assignedMemoryUnits )


    def testContiguousRegisters( self ) :
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 0, self.testModule.assignedMemoryUnits )
        self.assertEqual( 8, self.testSpace.memoryUnitBits )

        r1 = self.testModule.addRegister( 'r1' )
        self.assertEqual( 1, self.testModule.spanMemoryUnits )
        self.assertEqual( 1, self.testModule.assignedMemoryUnits )

        r1.addField( 'f1', [ 0, 10 ], [ 0, 10 ] )
        self.assertEqual( 2, self.testModule.spanMemoryUnits )
        self.assertEqual( 2, self.testModule.assignedMemoryUnits )

        r2 = self.testModule.addRegister( 'r2' )

        self.assertEqual( 3, self.testModule.spanMemoryUnits )
        self.assertEqual( 3, self.testModule.assignedMemoryUnits )


    def testDiscontiguousRegisters( self ) :
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 0, self.testModule.assignedMemoryUnits )
        self.assertEqual( 8, self.testSpace.memoryUnitBits )
        self.assertEqual( (self.previousModule.endAddress + 1), self.testModule.baseAddress )

        r1 = self.testModule.addRegister( 'r1' )
        r1.addField( 'f1', [ 0, 10 ], (0, 10) )
        self.assertEqual( 2, self.testModule.spanMemoryUnits )
        self.assertEqual( 2, self.testModule.assignedMemoryUnits )

        r2 = self.testModule.addRegister( 'r2' )
        self.assertEqual( 1, r2.sizeMemoryUnits )
        self.assertEqual( 3, self.testModule.spanMemoryUnits )
        self.assertEqual( 3, self.testModule.assignedMemoryUnits )

        expectedAddress = 0x15
        r2[ 'constraints' ][ 'fixedAddress' ] = expectedAddress

        self.assertEqual( r2.address, expectedAddress )
        self.assertEqual( (expectedAddress - self.testModule.baseAddress + 1), self.testModule.spanMemoryUnits )
        self.assertEqual( 3, self.testModule.assignedMemoryUnits )


    def testDiscontiguousRegistersWithMultiunitRegister( self ) :
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 0, self.testModule.assignedMemoryUnits )
        self.assertEqual( 8, self.testSpace.memoryUnitBits )
        self.assertEqual( (self.previousModule.endAddress + 1), self.testModule.baseAddress )

        r1 = self.testModule.addRegister( 'r1' )
        self.assertEqual( 1, self.testModule.spanMemoryUnits )

        r2 = self.testModule.addRegister( 'r2' )
        r2.addField( 'f1', [ 0, 10 ], (0, 10) )
        self.assertEqual( 2, r2.sizeMemoryUnits )
        self.assertEqual( 3, self.testModule.spanMemoryUnits )
        self.assertEqual( 3, self.testModule.assignedMemoryUnits )

        expectedAddress = 0x15
        r2[ 'constraints' ][ 'fixedAddress' ] = expectedAddress

        self.assertEqual( expectedAddress, r2.address )
        self.assertEqual( 6, self.testModule.spanMemoryUnits )
        self.assertEqual( 3, self.testModule.assignedMemoryUnits )


class TestModuleSizePreviousNoneAddresses( unittest.TestCase ) :

    def setUp( self ) :
        self.observer = MockObserver()
        self.previousModule = MockPreviousModule( endAddress = None )
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testModule = Module( self.testSpace, self.setCollection )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDiscontiguousRegisters( self ) :
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 0, self.testModule.assignedMemoryUnits )
        self.assertEqual( 8, self.testSpace.memoryUnitBits )
        self.assertIsNone( self.testModule.baseAddress )

        r1 = self.testModule.addRegister( 'r1' )
        r1.addField( 'f1', [ 0, 10 ], (0, 10) )
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 2, self.testModule.assignedMemoryUnits )

        r2 = self.testModule.addRegister( 'r2' )
        self.assertEqual( 1, r2.sizeMemoryUnits )
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 3, self.testModule.assignedMemoryUnits )

        expectedAddress = 0x15
        r2[ 'constraints' ][ 'fixedAddress' ] = expectedAddress

        self.assertEqual( r2.address, expectedAddress )
        self.assertEqual( 0, self.testModule.spanMemoryUnits )
        self.assertEqual( 3, self.testModule.assignedMemoryUnits )


class TestModuleSpanPreviousAddressChange( unittest.TestCase ) :

    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x0 )
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testModule = Module( self.testSpace, self.setCollection )

        self.testModule.previousElement = self.previousModule

        self.observer = MockObserver()
        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testSpanAfterPreviousAddressChange( self ) :
        r1 = self.testModule.addRegister( 'r1' )
        r1[ 'constraints' ][ 'fixedAddress' ] = 0x15

        self.previousModule.endAddress = 0x10
        # Because of the fixedAddress constraint on the register, the module span is implicitly a function of the
        # base address and the fixed address constraint.
        self.assertEqual( 0x11, self.testModule.baseAddress )
        self.assertEqual( 5, self.testModule.spanMemoryUnits )


if __name__ == '__main__' :
    unittest.main()
