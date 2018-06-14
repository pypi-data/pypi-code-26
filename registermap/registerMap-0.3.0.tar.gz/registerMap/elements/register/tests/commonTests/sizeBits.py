#
# Copyright 2018 Russell Smiley
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

import unittest

from registerMap.elements.tests.mockObserver import MockObserver
from registerMap.exceptions import ConstraintError
from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace


class CommonSizeBitsTests :
    class TestRegisterSizeBits( unittest.TestCase ) :
        # The tests will fail unless a test case loader correctly fulfills this value.
        RegisterType = None


        def setUp( self ) :
            self.observer = MockObserver()
            self.setCollection = SetCollection()
            self.testSpace = MemorySpace()
            self.registerUnderTest = self.RegisterType( self.testSpace,
                                                        setCollection = self.setCollection )

            self.registerUnderTest.sizeChangeNotifier.addObserver( self.observer )


        def testCorrectSizeForFieldsAdded( self ) :
            self.assertEqual( 0, self.observer.updateCount )

            memoryUnitsSizeBits = self.testSpace.memoryUnitBits

            self.registerUnderTest.addField( 'f1', [ 0, 7 ], (0, 7) )
            self.assertEqual( memoryUnitsSizeBits, self.registerUnderTest.sizeBits )

            self.registerUnderTest.addField( 'f2', [ 8, 10 ], (0, 2) )
            self.assertEqual( (2 * memoryUnitsSizeBits), self.registerUnderTest.sizeBits )


    class TestRegisterSize( unittest.TestCase ) :
        # The tests will fail unless a test case loader correctly fulfills this value.
        RegisterType = None


        def setUp( self ) :
            self.observer = MockObserver()
            self.setCollection = SetCollection()
            self.testSpace = MemorySpace()
            self.registerUnderTest = self.RegisterType( self.testSpace,
                                                        setCollection = self.setCollection )

            self.registerUnderTest.sizeChangeNotifier.addObserver( self.observer )


        def testDefaultValue( self ) :
            # A register with no bit fields must allocate one memory unit for itself.
            self.assertEqual( 1, self.registerUnderTest.sizeMemoryUnits )


        def testCorrectSizeForBitFieldsAdded1( self ) :
            # Adding two intervals to a register increases the register size:
            #  - from different fields
            #  - the second register interval exceeds the existing register size
            self.assertEqual( 8, self.testSpace.memoryUnitBits )
            self.assertEqual( 0, self.observer.updateCount )

            self.registerUnderTest.addField( 'f1', [ 0, 7 ], (0, 7) )
            self.assertEqual( 1, self.registerUnderTest.sizeMemoryUnits )
            # No notifications because the field addition didn't change the register size.
            self.assertEqual( 0, self.observer.updateCount )

            self.registerUnderTest.addField( 'f2', [ 8, 10 ], (0, 2) )
            self.assertEqual( 2, self.registerUnderTest.sizeMemoryUnits )
            self.assertEqual( 1, self.observer.updateCount )
            self.assertEqual( 8, self.registerUnderTest[ 'fields' ][ 'f1' ][ 'size' ] )
            self.assertEqual( 3, self.registerUnderTest[ 'fields' ][ 'f2' ][ 'size' ] )


        def testCorrectSizeForBitFieldsAdded2( self ) :
            # Adding two intervals to a register increases the register size:
            #  - from different fields
            #  - the first register interval does not exceed the register size, but the second interval does
            self.assertEqual( 8, self.testSpace.memoryUnitBits )
            self.assertEqual( 0, self.observer.updateCount )

            self.registerUnderTest.addField( 'f1', [ 0, 3 ], (0, 3) )
            self.assertEqual( 1, self.registerUnderTest.sizeMemoryUnits )
            self.assertEqual( 0, self.observer.updateCount )

            self.registerUnderTest.addField( 'f2', [ 8, 10 ], (0, 2) )
            self.assertEqual( 2, self.registerUnderTest.sizeMemoryUnits )
            self.assertEqual( 1, self.observer.updateCount )
            self.assertEqual( 4, self.registerUnderTest[ 'fields' ][ 'f1' ][ 'size' ] )
            self.assertEqual( 3, self.registerUnderTest[ 'fields' ][ 'f2' ][ 'size' ] )


        def testCorrectSizeForBitFieldsAdded3( self ) :
            # Adding two intervals to a register does not increase the register size:
            #  - from the same field
            #  - the extent of the new register intervals is less than the size of the register
            #  - the extent of the second field interval changes the size of the field
            #  - the FieldSet does not change size
            self.assertEqual( 8, self.testSpace.memoryUnitBits )
            self.assertEqual( 0, self.observer.updateCount )

            self.registerUnderTest.addField( 'f1', [ 0, 3 ], (0, 3) )
            self.assertEqual( 1, self.registerUnderTest.sizeMemoryUnits )
            self.assertEqual( 4, self.registerUnderTest[ 'fields' ][ 'f1' ][ 'size' ] )
            # No notifications because the field addition didn't change the register size.
            self.assertEqual( 0, self.observer.updateCount )
            self.registerUnderTest.addField( 'f1', [ 6, 7 ], (5, 6) )

            self.assertEqual( 1, self.registerUnderTest.sizeMemoryUnits )
            self.assertEqual( 0, self.observer.updateCount )
            self.assertEqual( 7, self.registerUnderTest[ 'fields' ][ 'f1' ][ 'size' ] )
            self.assertEqual( 1, len( self.setCollection.fieldSet ) )
            self.assertEqual( 2, len( self.registerUnderTest.bitMap.sourceIntervals ) )


        def testFixedSizeExceededAddBitfieldRaises( self ) :
            self.assertEqual( 8, self.testSpace.memoryUnitBits )

            self.registerUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = 1
            self.registerUnderTest.addField( 'f1', [ 0, 6 ], [ 0, 6 ] )
            with self.assertRaisesRegex( ConstraintError, '^Fixed size exceeded' ) :
                self.registerUnderTest.addField( 'f2', [ 8, 10 ], (0, 2) )


        def testFixedSizeConstraintReportsAsSize( self ) :
            self.assertEqual( 8, self.testSpace.memoryUnitBits )

            expectedSize = 2
            updateCountBeforeAddField = self.observer.updateCount

            self.registerUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = expectedSize

            self.assertEqual( self.registerUnderTest.sizeMemoryUnits, expectedSize )
            self.assertEqual( (updateCountBeforeAddField + 1), self.observer.updateCount )


        def testSingleFieldSpansMultipleBytes( self ) :
            self.assertEqual( 8, self.testSpace.memoryUnitBits )

            expectedSize = 2
            updateCountBeforeAddField = self.observer.updateCount

            self.registerUnderTest.addField( 'f1', [ 0, 10 ] )

            self.assertEqual( self.registerUnderTest.sizeMemoryUnits, expectedSize )
            self.assertEqual( (updateCountBeforeAddField + 1), self.observer.updateCount )
