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

from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace

from registerMap.elements.tests.mockObserver import MockObserver

from ..module import Module

from .mocks import MockPreviousModule


class TestModuleMultipleInstances( unittest.TestCase ) :

    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x10 )

        self.sizeObserver = MockObserver()
        self.addressObserver = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.moduleUnderTest = Module( self.testSpace, self.setCollection )
        self.moduleUnderTest[ 'name' ] = 'module'

        self.moduleUnderTest.sizeChangeNotifier.addObserver( self.sizeObserver )
        self.moduleUnderTest.addressChangeNotifier.addObserver( self.addressObserver )

        self.moduleUnderTest.previousElement = self.previousModule

        r1 = self.moduleUnderTest.addRegister( 'r1' )

        r1.addField( 'r1f1', (2, 4) )
        r1.addField( 'r1f2', (5, 7) )

        r2 = self.moduleUnderTest.addRegister( 'r2' )

        r2.addField( 'r2f1', (2, 9) )
        r2.addField( 'r2f2', (13, 18) )


    def testSingleInstanceSpan( self ) :
        self.assertEqual( 1, self.moduleUnderTest[ 'instances' ] )

        expectedSize = 4

        self.assertEqual( expectedSize, self.moduleUnderTest.spanMemoryUnits )


    def testMultipleInstanceContinuousSpan( self ) :
        # Module in the series are immediately adjacent to each other.
        self.assertEqual( 1, self.moduleUnderTest[ 'instances' ] )

        singleInstanceSize = self.moduleUnderTest.spanMemoryUnits

        self.moduleUnderTest[ 'instances' ] = 4
        self.assertEqual( 4, self.moduleUnderTest[ 'instances' ] )

        expectedMultipleInstanceSize = self.moduleUnderTest[ 'instances' ] * singleInstanceSize

        self.assertEqual( expectedMultipleInstanceSize, self.moduleUnderTest.spanMemoryUnits )


    def testInstanceChangeNotifiesObservers( self ) :
        self.assertEqual( 5, self.sizeObserver.updateCount )
        self.assertEqual( 1, self.addressObserver.updateCount )

        self.moduleUnderTest[ 'instances' ] = 10

        self.assertTrue( 4, self.sizeObserver.updateCount )
        self.assertTrue( 1, self.addressObserver.updateCount )


class TestModuleInstanceAddresses( unittest.TestCase ) :

    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x10 )

        self.observer = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.moduleUnderTest = Module( self.testSpace, self.setCollection )
        self.moduleUnderTest[ 'name' ] = 'm1'

        self.moduleUnderTest.sizeChangeNotifier.addObserver( self.observer )
        self.moduleUnderTest.addressChangeNotifier.addObserver( self.observer )

        self.moduleUnderTest.previousElement = self.previousModule

        self.m2 = Module( self.testSpace, self.setCollection )
        self.m2.previousElement = self.moduleUnderTest


    def testDefaultMultipleInstanceAddress( self ) :
        """
        Since a module has no size until registers are added, changing the number of instances consumes doesn't change
        the addresses.
        """
        self.assertEqual( 0x11, self.moduleUnderTest.baseAddress )
        self.assertEqual( 0x11, self.m2.baseAddress )

        self.moduleUnderTest[ 'instances' ] = 4

        self.assertEqual( 0x11, self.moduleUnderTest.baseAddress )
        self.assertEqual( 0x11, self.m2.baseAddress )


class TestModuleInstancesConstraints( unittest.TestCase ) :

    def setUp( self ) :
        self.mockPreviousModule = MockPreviousModule( endAddress = 0x10 )

        self.observer = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.moduleUnderTest = Module( self.testSpace, self.setCollection )
        self.moduleUnderTest[ 'name' ] = 'module'

        self.moduleUnderTest.sizeChangeNotifier.addObserver( self.observer )
        self.moduleUnderTest.addressChangeNotifier.addObserver( self.observer )

        self.moduleUnderTest.previousElement = self.mockPreviousModule

        r1 = self.moduleUnderTest.addRegister( 'r1' )

        r1.addField( 'r1f1', (2, 4) )
        r1.addField( 'r1f2', (5, 7) )

        r2 = self.moduleUnderTest.addRegister( 'r2' )

        r2.addField( 'r2f1', (2, 10) )

        self.assertEqual( 3, self.moduleUnderTest.spanMemoryUnits )


    def testAlignmentConstrainedInstancesSpan( self ) :
        self.assertEqual( 0x10, self.mockPreviousModule.endAddress )

        # Prior to instances or alignment the span is the size of a single module.
        self.assertEqual( 3, self.moduleUnderTest.spanMemoryUnits )

        numberInstances = 4

        # Applying instances and the size is the instance multiple of the single module size.

        self.moduleUnderTest[ 'instances' ] = numberInstances

        self.assertEqual( 12, self.moduleUnderTest.spanMemoryUnits )

        alignment = 4

        self.moduleUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = alignment

        # 15 = (3 * 4 [span caused by alignment]) + 3 [last instance span]
        expectedInstancesSpan = 15
        self.assertEqual( expectedInstancesSpan, self.moduleUnderTest.spanMemoryUnits )


    def testFixedSizeConstrainedInstancesSpan( self ) :
        expectedModuleSize = 10
        numberInstances = 4

        self.moduleUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = expectedModuleSize

        self.assertEqual( expectedModuleSize, self.moduleUnderTest.spanMemoryUnits )

        self.moduleUnderTest[ 'instances' ] = numberInstances

        expectedInstancesSpan = expectedModuleSize * numberInstances
        self.assertEqual( expectedInstancesSpan, self.moduleUnderTest.spanMemoryUnits )


    def testFixedSizeAndAlignmentInstancesSpan( self ) :
        numberInstances = 4
        expectedModuleSize = 5

        self.moduleUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4
        self.moduleUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = expectedModuleSize

        # Expect 8 memory units to be consumed by each module in the series, except the last module.
        # The next module could start at the next available memory unit, unless it also has an alignment constraint (which
        # would be sensible, but not necessary).

        self.assertEqual( expectedModuleSize, self.moduleUnderTest.spanMemoryUnits )

        self.moduleUnderTest[ 'instances' ] = numberInstances

        expectedInstancesSpan = 8 * (numberInstances - 1) + expectedModuleSize
        self.assertEqual( expectedInstancesSpan, self.moduleUnderTest.spanMemoryUnits )


if __name__ == '__main__' :
    unittest.main()
