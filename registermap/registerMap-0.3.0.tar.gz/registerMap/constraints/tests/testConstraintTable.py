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
import math
import unittest

import registerMap.constraints.constraintTable as rmc
import registerMap.structure.memory.space as rmm
from registerMap.elements.tests.mockObserver import MockObserver


log = logging.getLogger( __name__ )


class MockItem :
    """
    Mock the interfaces of RegisterMap, Module, Register, BitField that are used by constraints.
    """


    def __init__( self, initialAddress, sizeValue, memory = rmm.MemorySpace( ) ) :
        self.__memory = memory


    @property
    def memory( self ) :
        return self.__memory


class TestConstraintTable( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )
        self.constraints = rmc.ConstraintTable( self.memory )
        self.observer = MockObserver( )

        self.constraints.addressChangeNotifier.addObserver( self.observer )


    def testQueryEmptyConstraintTableRaises( self ) :
        for thisName in rmc.ConstraintTable.validConstraints.keys( ) :
            with self.assertRaisesRegex( rmc.ConstraintError, '^Constraint not applied' ) :
                self.constraints[ thisName ]


    def testInvalidConstraintNameRaises( self ) :
        with self.assertRaisesRegex( rmc.ConstraintError, '^Not a valid constraint' ) :
            self.constraints[ 'badName' ]


    def testAddValidConstraint( self ) :
        expectedValue = 0x10
        self.constraints[ 'fixedAddress' ] = expectedValue

        self.assertEqual( self.constraints[ 'fixedAddress' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 1 )


    def testAddInvalidConstraintRaises( self ) :
        with self.assertRaisesRegex( rmc.ConstraintError, '^Not a valid constraint' ) :
            self.constraints[ 'badName' ] = 0x10


    def testDeleteConstraint( self ) :
        constraintName = 'fixedAddress'
        expectedValue = 0x10
        self.constraints[ constraintName ] = expectedValue

        self.assertEqual( self.constraints[ constraintName ], expectedValue )
        self.assertEqual( self.observer.updateCount, 1 )

        del self.constraints[ constraintName ]
        self.assertEqual( self.observer.updateCount, 2 )

        with self.assertRaisesRegex( rmc.ConstraintError, '^Constraint not applied' ) :
            self.constraints[ constraintName ]


    def testTwoConstraints( self ) :
        initialAddress = 0x10
        self.constraints[ 'alignmentMemoryUnits' ] = 4
        self.constraints[ 'fixedAddress' ] = initialAddress
        self.assertEqual( self.observer.updateCount, 2 )

        # The fixed address constraint takes precedence
        actualAddress = self.constraints.applyAddressConstraints( initialAddress )
        self.assertEqual( actualAddress, initialAddress )


    def testTwoConstraintsDifferentOrder( self ) :
        initialAddress = 0x10
        self.constraints[ 'fixedAddress' ] = initialAddress
        self.constraints[ 'alignmentMemoryUnits' ] = 2
        self.assertEqual( self.observer.updateCount, 2 )

        # The fixed address constraint takes precedence
        actualAddress = self.constraints.applyAddressConstraints( initialAddress )
        self.assertEqual( actualAddress, initialAddress )


    def testAddBadFixedAddressAgainstAlignmentRaises( self ) :
        expectedAddress = 0x1
        self.constraints[ 'alignmentMemoryUnits' ] = 4
        with self.assertRaisesRegex( rmc.ConstraintError, '^Address constraints conflict' ) :
            self.constraints[ 'fixedAddress' ] = expectedAddress


    def testAddAlignmentAgainstBadFixedAddressRaises( self ) :
        expectedAddress = 0x1
        self.constraints[ 'fixedAddress' ] = expectedAddress
        with self.assertRaisesRegex( rmc.ConstraintError, '^Address constraints conflict' ) :
            self.constraints[ 'alignmentMemoryUnits' ] = 4


    def testFixedAddressOnPageRegisterRaises( self ) :
        self.memory.pageSize = 128
        numberMemoryUnits = math.ceil( float( self.memory.addressBits ) / self.memory.memoryUnitBits )
        pageAddresses = [ (self.memory.pageSize - x + 0x800) for x in range( 1, (numberMemoryUnits + 1) ) ]

        for address in pageAddresses :
            with self.assertRaisesRegex( rmc.ConstraintError, '^Cannot constrain address to page register' ) :
                self.constraints[ 'fixedAddress' ] = address


    def testDeleteInvalidConstraintRaises( self ) :
        constraintName = 'badName'
        with self.assertRaisesRegex( rmc.ConstraintError, '^Not a valid constraint' ) :
            del self.constraints[ constraintName ]


    def testDeleteValidConstraintNoAppliedRaises( self ) :
        constraintName = 'fixedAddress'
        with self.assertRaisesRegex( rmc.ConstraintError, '^Constraint not applied' ) :
            del self.constraints[ constraintName ]


    def testIsEmpty( self ) :
        self.assertTrue( self.constraints.isEmpty )

        self.constraints[ 'fixedAddress' ] = 0x10

        self.assertFalse( self.constraints.isEmpty )


class TestApplyConstraints( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )
        self.constraints = rmc.ConstraintTable( self.memory )
        self.observer = MockObserver( )

        self.constraints.addressChangeNotifier.addObserver( self.observer )


    def testApplyAddressConstraintsNoConstraints( self ) :
        # with no constraints, the initial address is unchanged.
        expectedAddress = 0x10

        actualAddress = self.constraints.applyAddressConstraints( expectedAddress )

        self.assertEqual( actualAddress, expectedAddress )


    def testApplySizeConstraintNoConstraints( self ) :
        # with no constraints, the initial address is unchanged.
        expectedSize = 0x10

        actualSize = self.constraints.applySizeConstraints( expectedSize )

        self.assertEqual( actualSize, expectedSize )


class TestApplyFixedAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )
        self.constraints = rmc.ConstraintTable( self.memory )
        self.observer = MockObserver( )

        self.constraints.addressChangeNotifier.addObserver( self.observer )


    def testFixedAddressChanges( self ) :
        expectedAddress = 0x10

        self.constraints[ 'fixedAddress' ] = expectedAddress

        self.assertEqual( self.constraints[ 'fixedAddress' ], expectedAddress )
        self.assertTrue( self.observer.updateCount, 1 )


    def testNegativeRaises( self ) :
        with self.assertRaisesRegex( rmc.ConstraintError, '^Fixed address constraint must be a positive integer' ) :
            self.constraints[ 'fixedAddress' ] = -1


    def testCurrentAddressExceedsFixedAddressRaises( self ) :
        currentAddress = 0x11
        fixedAddress = 0x10

        self.constraints[ 'fixedAddress' ] = fixedAddress

        with self.assertRaisesRegex( rmc.ConstraintError, '^Fixed address exceeded' ) :
            self.constraints.applyAddressConstraints( currentAddress )


    def testCurrentAddressEqualsFixedAddress( self ) :
        expectedAddress = 0x11

        self.constraints[ 'fixedAddress' ] = expectedAddress

        actualAddress = self.constraints.applyAddressConstraints( expectedAddress )

        self.assertEqual( actualAddress, expectedAddress )


    def testCurrentAddressIsNone( self ) :
        expectedAddress = 0x11

        self.constraints[ 'fixedAddress' ] = expectedAddress

        actualAddress = self.constraints.applyAddressConstraints( None )

        self.assertEqual( actualAddress, expectedAddress )


class TestApplyAddressAlignment( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )
        self.constraints = rmc.ConstraintTable( self.memory )
        self.observer = MockObserver( )

        self.constraints.addressChangeNotifier.addObserver( self.observer )


    def testAddressAlignmentChange( self ) :
        alignmentValue = 4
        initialAddress = 0x6
        expectedAddress = 0x8
        self.assertTrue( (initialAddress < expectedAddress) )
        self.assertTrue( (initialAddress % alignmentValue) != 0 )

        self.constraints[ 'alignmentMemoryUnits' ] = alignmentValue

        self.assertTrue( self.observer.updateCount, 1 )

        actualAddress = self.constraints.applyAddressConstraints( initialAddress )

        self.assertEqual( actualAddress, expectedAddress )


    def testAddressAlignmentNoChange( self ) :
        alignmentValue = 3
        initialAddress = 0x6
        expectedAddress = initialAddress
        self.assertTrue( (initialAddress % alignmentValue) == 0 )

        self.constraints[ 'alignmentMemoryUnits' ] = alignmentValue

        actualAddress = self.constraints.applyAddressConstraints( initialAddress )

        self.assertEqual( actualAddress, expectedAddress )


    def testZeroRaises( self ) :
        with self.assertRaisesRegex( rmc.ConstraintError, '^Alignment must be a positive non-zero integer' ) :
            self.constraints[ 'alignmentMemoryUnits' ] = 0


    def testNegativeRaises( self ) :
        with self.assertRaisesRegex( rmc.ConstraintError, '^Alignment must be a positive non-zero integer' ) :
            self.constraints[ 'alignmentMemoryUnits' ] = -1


class TestApplySize( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )
        self.constraints = rmc.ConstraintTable( self.memory )
        self.observer = MockObserver( )

        self.constraints.sizeChangeNotifier.addObserver( self.observer )


    def testUnderSizeOk( self ) :
        fixedSize = 6
        self.constraints[ 'fixedSizeMemoryUnits' ] = fixedSize
        self.assertEqual( self.observer.updateCount, 1 )


    def testZeroNoRaise( self ) :
        self.constraints[ 'fixedSizeMemoryUnits' ] = 0


    def testNegativeRaises( self ) :
        with self.assertRaisesRegex( rmc.ConstraintError, '^Fixed size must be a positive integer' ) :
            self.constraints[ 'fixedSizeMemoryUnits' ] = -1


    def testOverSizeRaises( self ) :
        fixedSize = 6
        currentSize = 8

        self.assertGreater( currentSize, fixedSize )

        self.constraints[ 'fixedSizeMemoryUnits' ] = fixedSize

        with self.assertRaisesRegex( rmc.ConstraintError, '^Fixed size exceeded' ) :
            self.constraints.applySizeConstraints( currentSize )


class TestConstraintTableLen( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )
        self.constraints = rmc.ConstraintTable( self.memory )
        self.observer = MockObserver( )

        self.constraints.addressChangeNotifier.addObserver( self.observer )


    def testEmptyEqualsZero( self ) :
        self.assertEqual( len( self.constraints ), 0 )


    def testAddOneConstraintLenEqualsOne( self ) :
        self.assertEqual( len( self.constraints ), 0 )

        self.constraints[ 'fixedAddress' ] = 0x10
        self.assertEqual( len( self.constraints ), 1 )


class TestLoadSave( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = rmm.MemorySpace( )
        self.constraints = rmc.ConstraintTable( self.memory )
        self.observer = MockObserver( )

        self.constraints.addressChangeNotifier.addObserver( self.observer )


    def testEncodeDecode( self ) :
        self.constraints[ 'fixedAddress' ] = 0x10
        self.constraints[ 'fixedSizeMemoryUnits' ] = 0x7
        self.constraints[ 'alignmentMemoryUnits' ] = 2

        encodedYamlData = self.constraints.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = rmc.ConstraintTable.from_yamlData( encodedYamlData, self.memory )

        self.assertEqual( decodedData[ 'fixedAddress' ], self.constraints[ 'fixedAddress' ] )
        self.assertEqual( decodedData[ 'fixedSizeMemoryUnits' ], self.constraints[ 'fixedSizeMemoryUnits' ] )
        self.assertEqual( decodedData[ 'alignmentMemoryUnits' ], self.constraints[ 'alignmentMemoryUnits' ] )


    def testDecodeEmpty( self ) :
        emptyConstraintsYamlData = { 'constraints' : { } }
        table = rmc.ConstraintTable.from_yamlData( emptyConstraintsYamlData, self.memory )

        self.assertTrue( table.isEmpty )


if __name__ == '__main__' :
    unittest.main( )
