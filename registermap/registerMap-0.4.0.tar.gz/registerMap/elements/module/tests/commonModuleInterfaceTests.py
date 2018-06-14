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

import abc
import unittest.mock

from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace

from .mocks import MockPreviousModule

from ..module import Module


class CommonModuleInterfaceTests :
    class CommonTestInterface( metaclass = abc.ABCMeta ) :

        @abc.abstractmethod
        def constructInstanceUnderTest( self ) :
            """
            Instantiate the module class object to be tested.

            :return: Instance of module class under test.
            """
            pass


    class TestModuleConstraints( unittest.TestCase,
                                 metaclass = abc.ABCMeta ) :

        @abc.abstractmethod
        def constructInstanceUnderTest( self ) :
            """
            Instantiate the module class object to be tested.

            :return: Instance of module class under test.
            """
            pass


        def setUp( self ) :
            self.mock_memory = MemorySpace()
            self.mock_setCollection = SetCollection()

            self.mock_previousElement = MockPreviousModule( endAddress = None )

            self.moduleUnderTest = self.constructInstanceUnderTest()

            self.moduleUnderTest.previousElement = self.mock_previousElement


        def testFixedAddress( self ) :
            self.mock_previousElement.endAddress = 0x10

            expectedValue = 0x15

            self.assertGreater( expectedValue, self.mock_previousElement.endAddress )
            self.assertNotEqual( expectedValue, self.moduleUnderTest.baseAddress )

            self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = expectedValue

            self.assertEqual( expectedValue, self.moduleUnderTest.baseAddress )


        def testAlignedAddress( self ) :
            self.mock_previousElement.endAddress = 0x10

            alignmentValue = 2
            expectedValue = self.mock_previousElement.endAddress + 2

            self.assertEqual( 0, (expectedValue % alignmentValue) )
            self.assertLess( self.moduleUnderTest.baseAddress, expectedValue )

            self.assertNotEqual( expectedValue, self.moduleUnderTest.baseAddress )

            self.moduleUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = alignmentValue

            self.assertEqual( expectedValue, self.moduleUnderTest.baseAddress )


        def testFixedAddressConstraintPreviousElementNone( self ) :
            """
            Fixed address constraint returns None if the previous element end address is None.
            """
            self.mock_previousElement.endAddress = None

            expectedValue = 0x500

            self.assertNotEqual( expectedValue, self.moduleUnderTest.baseAddress )

            self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = expectedValue

            self.assertEqual( expectedValue, self.moduleUnderTest.baseAddress )


    class TestModuleOffsetProperty( unittest.TestCase,
                                    CommonTestInterface ) :

        def setUp( self ) :
            self.setCollection = SetCollection()
            self.testSpace = MemorySpace()
            self.testSpace.baseAddress = 0x100

            self.mock_previousElement = MockPreviousModule( endAddress = 0xff )

            self.moduleUnderTest = self.constructInstanceUnderTest()

            self.moduleUnderTest.previousElement = self.mock_previousElement


        def testDefault( self ) :
            self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = self.testSpace.baseAddress

            self.assertEqual( self.testSpace.baseAddress, self.moduleUnderTest.baseAddress )
            self.assertEqual( 0, self.moduleUnderTest.offset )


        def testAddressChanged( self ) :
            expectedAddress = 0x300
            expectedOffset = expectedAddress - self.testSpace.baseAddress

            self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = expectedAddress

            self.assertEqual( expectedAddress, self.moduleUnderTest.baseAddress )
            self.assertEqual( expectedOffset, self.moduleUnderTest.offset )


        def testOffsetProperty( self ) :
            self.mock_previousElement.endAddress = 0x1ff

            expectedOffset = 0x100
            expectedAddress = 0x200

            self.assertEqual( expectedOffset, self.moduleUnderTest.offset )
            self.assertEqual( expectedAddress, self.moduleUnderTest.baseAddress )


    class TestModulePreviousElementProperty( unittest.TestCase, CommonTestInterface ) :

        def setUp( self ) :
            self.setCollection = SetCollection()
            self.mock_memory = MemorySpace()
            self.mock_memory.baseAddress = 0x100

            self.mock_previousElement = MockPreviousModule( endAddress = 0xff )

            self.moduleUnderTest = self.constructInstanceUnderTest()


        def testPreviousElementAssignment( self ) :
            self.moduleUnderTest.previousElement = self.mock_previousElement

            self.assertEqual( self.mock_previousElement, self.moduleUnderTest.previousElement )


        def testDefaultValue( self ) :
            self.assertIsNone( self.moduleUnderTest.previousElement )


        def testAssignPreviousModuleNoneEndAddress( self ) :
            previousModule = MockPreviousModule()
            self.moduleUnderTest.previousElement = previousModule

            self.assertIsNone( self.moduleUnderTest.endAddress )


        def testUpdatePreviousModuleEndAddress( self ) :
            previousModule = MockPreviousModule()
            self.moduleUnderTest.previousElement = previousModule

            expectedAddress = 0x10
            previousModule.endAddress = expectedAddress - 1

            self.assertEqual( expectedAddress, self.moduleUnderTest.baseAddress )


    class TestModuleNameParameter( unittest.TestCase, CommonTestInterface ) :

        def setUp( self ) :
            self.setCollection = SetCollection()
            self.mock_memory = MemorySpace()

            self.moduleUnderTest = self.constructInstanceUnderTest()


        def testDefaultValue( self ) :
            self.assertIsNone( self.moduleUnderTest[ 'name' ] )


        def testNameAssignment( self ) :
            expectedValue = 'some-name'

            self.moduleUnderTest[ 'name' ] = expectedValue

            self.assertEqual( expectedValue, self.moduleUnderTest[ 'name' ] )
