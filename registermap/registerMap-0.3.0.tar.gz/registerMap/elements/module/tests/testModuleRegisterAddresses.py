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

from .mocks import MockPreviousModule

from ..module import \
    ConfigurationError, \
    Module


class TestModuleAddRegisterNoneAddresses( unittest.TestCase ) :

    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = None )
        self.observer = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.moduleUnderTest = Module( self.testSpace, self.setCollection )

        self.moduleUnderTest.previousElement = self.previousModule

        self.moduleUnderTest.sizeChangeNotifier.addObserver( self.observer )
        self.moduleUnderTest.addressChangeNotifier.addObserver( self.observer )


    def testAddSingleRegister( self ) :
        expectedName = 'r1'

        self.assertEqual( 0, len( self.moduleUnderTest[ 'registers' ] ) )

        addedRegister = self.moduleUnderTest.addRegister( expectedName )

        self.assertEqual( 1, len( self.moduleUnderTest[ 'registers' ] ) )
        self.assertEqual( expectedName, self.moduleUnderTest[ 'registers' ][ expectedName ][ 'name' ] )
        # The addRegister method returns the created register
        self.assertEqual( addedRegister, self.moduleUnderTest[ 'registers' ][ expectedName ] )

        self.assertIsNone( addedRegister.address )


    def testAddDuplicateRegisterRaises( self ) :
        # A register name is unique to its module
        expectedName = 'r1'
        self.moduleUnderTest.addRegister( expectedName )
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Created register names must be unique within a module' ) :
            self.moduleUnderTest.addRegister( expectedName )


    def testAddMultipleRegistersWithSubsequentConcreteAddress( self ) :
        r1 = self.moduleUnderTest.addRegister( 'r1' )
        self.assertIsNone( r1.address )
        r2 = self.moduleUnderTest.addRegister( 'r2' )
        self.assertIsNone( r2.address )

        previousModule = MockPreviousModule( endAddress = 0x10 )

        self.moduleUnderTest.previousElement = previousModule

        self.assertEqual( 0x11, self.moduleUnderTest.baseAddress )
        self.assertEqual( 0x11, r1.address )
        self.assertEqual( 0x12, r2.address )


class TestModuleAddRegisterConcreteAddresses( unittest.TestCase ) :

    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x10 )
        self.observer = MockObserver()
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.moduleUnderTest = Module( self.testSpace, self.setCollection )

        self.moduleUnderTest.previousElement = self.previousModule

        self.moduleUnderTest.sizeChangeNotifier.addObserver( self.observer )
        self.moduleUnderTest.addressChangeNotifier.addObserver( self.observer )


    def testAddSingleRegister( self ) :
        expectedName = 'r1'

        self.assertEqual( 0, len( self.moduleUnderTest[ 'registers' ] ) )

        addedRegister = self.moduleUnderTest.addRegister( expectedName )

        self.assertEqual( 1, len( self.moduleUnderTest[ 'registers' ] ) )
        self.assertEqual( expectedName, self.moduleUnderTest[ 'registers' ][ expectedName ][ 'name' ] )
        # The addRegister method returns the created register
        self.assertEqual( addedRegister, self.moduleUnderTest[ 'registers' ][ expectedName ] )

        self.assertEqual( self.moduleUnderTest.baseAddress, addedRegister.address )


    def testAddRegisterAfterMultibyte( self ) :
        r1 = self.moduleUnderTest.addRegister( 'r1' )

        r1.addField( 'f1', (0, 10) )

        self.assertEqual( self.moduleUnderTest.baseAddress, r1.address )
        self.assertEqual( 2, r1.sizeMemoryUnits )

        r2 = self.moduleUnderTest.addRegister( 'r2' )

        expectedR2Address = self.moduleUnderTest.baseAddress + r1.sizeMemoryUnits

        self.assertEqual( expectedR2Address, r2.address )


if __name__ == '__main__' :
    unittest.main()
