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
import unittest

from ..module import \
    Module, \
    ParseError
from registerMap.structure.memory.space import MemorySpace
from registerMap.set import SetCollection

from registerMap.elements.tests.mockObserver import MockObserver

from .mocks import MockPreviousModule


log = logging.getLogger( __name__ )


class TestModuleYamlLoadSave( unittest.TestCase ) :

    def setUp( self ) :
        self.observer = MockObserver()
        self.previousModule = MockPreviousModule( endAddress = 0x0 )
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.moduleUnderTest = Module( self.testSpace, self.setCollection )

        self.moduleUnderTest.previousElement = self.previousModule
        self.moduleUnderTest[ 'name' ] = 'module'
        self.moduleUnderTest.sizeChangeNotifier.addObserver( self.observer )

        self.setCollection.moduleSet.add( self.moduleUnderTest )

        self.acquiredSetCollection = SetCollection()


    def testEncodeDecode( self ) :
        self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x10
        self.createRegister( 'r1' )

        encodedYamlData = self.moduleUnderTest.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedModule = Module.from_yamlData( encodedYamlData, self.testSpace, self.acquiredSetCollection )

        self.assertEqual( decodedModule[ 'constraints' ][ 'fixedAddress' ],
                          self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] )
        self.assertEqual( decodedModule[ 'description' ], self.moduleUnderTest[ 'description' ] )
        self.assertEqual( decodedModule[ 'summary' ], self.moduleUnderTest[ 'summary' ] )

        self.assertEqual( len( self.acquiredSetCollection.moduleSet ), 1 )

        decodedModule.previousElement = self.previousModule
        # No exceptions should be thrown
        decodedModule.reviewAddressChange()


    def createRegister( self, name ) :
        self.moduleUnderTest.addRegister( name )

        self.moduleUnderTest[ 'registers' ][ name ][ 'constraints' ][ 'fixedAddress' ] = 0x10
        self.moduleUnderTest[ 'registers' ][ name ][ 'description' ] = 'some description'
        self.moduleUnderTest[ 'registers' ][ name ][ 'mode' ] = 'ro'
        self.moduleUnderTest[ 'registers' ][ name ][ 'public' ] = False
        self.moduleUnderTest[ 'registers' ][ name ][ 'summary' ] = 'a summary'

        self.moduleUnderTest[ 'registers' ][ name ].addField( 'f1', [ 3, 5 ], (3, 5) )
        self.moduleUnderTest[ 'registers' ][ name ].addField( 'f2', [ 7, 7 ], (7, 7) )


    def testFromBadYamlData( self ) :
        yamlData = { 'mode' : 'ro' }

        with self.assertRaisesRegex( ParseError, '^Yaml data does not specify module' ) :
            Module.from_yamlData( yamlData, self.testSpace, self.acquiredSetCollection )


    def testFromOptionalYamlData( self ) :
        yamlData = { 'mode' : 'ro' }

        decodedModule = Module.from_yamlData( yamlData, self.testSpace, self.acquiredSetCollection,
                                              optional = True )

        self.assertEqual( len( decodedModule[ 'constraints' ] ), 0 )
        self.assertEqual( decodedModule[ 'description' ], '' )
        self.assertIsNone( decodedModule[ 'name' ] )
        self.assertEqual( len( decodedModule[ 'registers' ] ), 0 )
        self.assertEqual( decodedModule[ 'summary' ], '' )


class TestModuleYamlParameters( unittest.TestCase ) :

    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x215 )
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.moduleUnderTest = Module( self.testSpace, self.setCollection )

        self.moduleUnderTest.previousElement = self.previousModule


    def testYamlDataAddress( self ) :
        # The address data is automatically generated so it is prefixed by '_'.
        self.assertEqual( self.previousModule.endAddress, 0x215 )

        expectedName = '_address'
        expectedValue = 0x216

        self.assertEqual( self.moduleUnderTest.baseAddress, expectedValue )

        yamlData = self.moduleUnderTest.to_yamlData()
        self.assertEqual( yamlData[ 'module' ][ expectedName ], expectedValue )


    def testYamlDataSpan( self ) :
        # The address data is automatically generated so it is prefixed by '_'.
        expectedName = '_spanMemoryUnits'
        expectedValue = 0

        self.assertEqual( self.moduleUnderTest.spanMemoryUnits, expectedValue )

        yamlData = self.moduleUnderTest.to_yamlData()
        self.assertEqual( yamlData[ 'module' ][ expectedName ], expectedValue )


    def testYamlDataNoneAddress( self ) :
        testModule = Module( self.testSpace, self.setCollection )

        yamlData = testModule.to_yamlData()
        self.assertIsNone( yamlData[ 'module' ][ '_address' ] )


class TestLoadSaveUserDefinedParameters( unittest.TestCase ) :

    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x0 )
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.moduleUnderTest = Module( self.testSpace, self.setCollection )

        self.moduleUnderTest.previousElement = self.previousModule
        self.moduleUnderTest[ 'name' ] = 'module'

        self.setCollection.moduleSet.add( self.moduleUnderTest )

        self.acquiredSetCollection = SetCollection()


    def testEncodeDecode( self ) :
        expectedValue = 'some value'

        self.moduleUnderTest[ 'my-parameter' ] = expectedValue

        encodedYamlData = self.moduleUnderTest.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedModule = Module.from_yamlData( encodedYamlData, self.testSpace, self.acquiredSetCollection )

        self.assertEqual( expectedValue, decodedModule[ 'my-parameter' ] )


class TestModuleYamlAddressRestoration( unittest.TestCase ) :

    def setUp( self ) :
        self.observer = MockObserver()
        self.previousModule = MockPreviousModule( endAddress = 0x0 )
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.moduleUnderTest = Module( self.testSpace, self.setCollection )

        self.moduleUnderTest.previousElement = self.previousModule
        self.moduleUnderTest[ 'name' ] = 'module'
        self.moduleUnderTest.sizeChangeNotifier.addObserver( self.observer )

        self.setCollection.moduleSet.add( self.moduleUnderTest )

        self.acquiredSetCollection = SetCollection()


    def testEncodeDecodeAddressesRestored( self ) :
        self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x10

        r1 = self.moduleUnderTest.addRegister( 'r1' )

        r1.addField( 'f1', (5, 11) )

        r2 = self.moduleUnderTest.addRegister( 'r2' )

        r2.addField( 'f2', (3, 5) )
        r2.addField( 'f3', (6, 7) )

        encodedYamlData = self.moduleUnderTest.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedModule = Module.from_yamlData( encodedYamlData, self.testSpace, self.acquiredSetCollection )

        # This is needed to have the sizes from the export registered correctly.
        decodedModule.reviewAddressChange()
        decodedModule.reviewSizeChange()

        self.assertEqual( self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ],
                          decodedModule[ 'constraints' ][ 'fixedAddress' ] )
        self.assertEqual( self.moduleUnderTest[ 'description' ], decodedModule[ 'description' ] )
        self.assertEqual( self.moduleUnderTest[ 'summary' ], decodedModule[ 'summary' ] )

        self.assertEqual( 1, len( self.acquiredSetCollection.moduleSet ) )

        decodedR1 = decodedModule[ 'registers' ][ 'r1' ]
        self.assertEqual( r1.address, decodedR1.address )

        decodedR2 = decodedModule[ 'registers' ][ 'r2' ]
        self.assertEqual( r2.address, decodedR2.address )


if __name__ == '__main__' :
    unittest.main()
