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

import collections
import logging
import unittest

from registerMap.elements.tests.mockObserver import MockObserver
from registerMap.exceptions import ConfigurationError
from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace


log = logging.getLogger( __name__ )


class CommonFieldTests :
    class TestRegisterFields( unittest.TestCase ) :
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
            self.assertEqual( self.registerUnderTest[ 'fields' ], collections.OrderedDict() )


        def testMultipleFieldsAddedToArbitrarySizeWithoutConstraint( self ) :
            self.assertEqual( self.testSpace.memoryUnitBits, 8 )
            self.assertEqual( len( self.registerUnderTest[ 'fields' ] ), 0 )

            self.registerUnderTest.addField( 'testField1', [ 0, 3 ], (0, 3) )
            self.registerUnderTest.addField( 'testField2', [ 4, 10 ], (0, 6) )
            self.registerUnderTest.addField( 'testField3', [ 11, 25 ], (0, 14) )

            self.assertEqual( self.registerUnderTest.sizeMemoryUnits, 4 )


        def testOverlappingRegisterIntervalRaises( self ) :
            self.registerUnderTest.addField( 'field1', [ 0, 5 ], (0, 5) )
            self.assertEqual( len( self.registerUnderTest[ 'fields' ] ), 1 )

            with self.assertRaisesRegex( ConfigurationError,
                                         '^Specifed source interval overlaps existing source intervals' ) :
                self.registerUnderTest.addField( 'field2', [ 5, 6 ], (0, 1) )


        def testOverlappingFieldIntervalRaises( self ) :
            self.registerUnderTest.addField( 'field1', [ 0, 5 ], (0, 5) )
            self.assertEqual( len( self.registerUnderTest[ 'fields' ] ), 1 )

            with self.assertRaisesRegex( ConfigurationError,
                                         '^Specifed destination interval overlaps existing destination intervals' ) :
                self.registerUnderTest.addField( 'field1', [ 6, 7 ], (5, 6) )


    class TestFieldsMultipleRegisters( unittest.TestCase ) :
        # The tests will fail unless a child class correctly fulfills this value.
        RegisterType = None


        def setUp( self ) :
            self.setCollection = SetCollection()
            self.testSpace = MemorySpace()


        def testAddLocalFieldsToDifferentRegisters( self ) :
            self.assertEqual( len( self.setCollection.fieldSet ), 0 )

            register1 = self.RegisterType( self.testSpace, setCollection =
            self.setCollection )
            register1.addField( 'field1', [ 5, 6 ], (0, 1) )

            self.assertEqual( len( self.setCollection.fieldSet ), 1 )
            self.assertEqual( list( self.setCollection.fieldSet )[ 0 ][ 'name' ], 'field1' )

            register2 = self.RegisterType( self.testSpace,
                                           setCollection = self.setCollection )
            register2.addField( 'field1', [ 3, 5 ], (4, 6) )

            self.assertEqual( len( self.setCollection.fieldSet ), 2 )
            self.assertEqual( list( self.setCollection.fieldSet )[ 0 ][ 'name' ], 'field1' )
            self.assertEqual( list( self.setCollection.fieldSet )[ 1 ][ 'name' ], 'field1' )


        def testAddLocalFieldsToSameRegisters( self ) :
            self.assertEqual( len( self.setCollection.fieldSet ), 0 )

            register1 = self.RegisterType( self.testSpace,
                                           setCollection = self.setCollection )
            register1.addField( 'field1', [ 5, 6 ], (0, 1) )

            self.assertEqual( len( self.setCollection.fieldSet ), 1 )
            self.assertEqual( list( self.setCollection.fieldSet )[ 0 ][ 'name' ], 'field1' )

            register1.addField( 'field1', [ 2, 4 ], (4, 6) )

            self.assertEqual( len( self.setCollection.fieldSet ), 1 )
            self.assertEqual( list( self.setCollection.fieldSet )[ 0 ][ 'name' ], 'field1' )


        def testAddGlobalFieldToRegisters( self ) :
            self.assertEqual( len( self.setCollection.fieldSet ), 0 )

            register1 = self.RegisterType( self.testSpace,
                                           setCollection = self.setCollection )
            register1.addField( 'field1', [ 5, 6 ], (0, 1),
                                isGlobal = True )

            self.assertEqual( len( self.setCollection.fieldSet ), 1 )
            self.assertEqual( list( self.setCollection.fieldSet )[ 0 ][ 'name' ], 'field1' )

            register2 = self.RegisterType( self.testSpace,
                                           setCollection = self.setCollection )
            register2.addField( 'field1', [ 2, 4 ], (2, 4),
                                isGlobal = True )

            # The bit field set should not have changed since the initial bitfield was defined as global.
            self.assertEqual( len( self.setCollection.fieldSet ), 1 )
