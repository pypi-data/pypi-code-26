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

import logging
import unittest

from registerMap.elements.tests.mockObserver import MockObserver
from registerMap.exceptions import ParseError
from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace

from registerMap.elements.register.tests.mocks import MockPreviousRegister


log = logging.getLogger( __name__ )


class MockModule :
    def __init__( self, name ) :
        self.__name = name


    def __getitem__( self, item ) :
        assert item == 'name'

        return self.__name


class CommonYamlIoTests :
    class TestRegisterYamlLoadSave( unittest.TestCase ) :
        # The tests will fail unless a test case loader correctly fulfills this value.
        RegisterType = None


        def setUp( self ) :
            self.sourceCollection = SetCollection()
            self.testSpace = MemorySpace()
            self.testRegister = self.RegisterType( self.testSpace,
                                                   setCollection = self.sourceCollection )

            self.observer = MockObserver()
            self.testRegister.sizeChangeNotifier.addObserver( self.observer )

            self.acquiredCollection = SetCollection()


        def testEncodeDecode( self ) :
            def checkFields() :
                """
                Test the register fields have been recovered correctly.
                """
                nonlocal self, decodedRegister

                self.assertEqual( decodedRegister[ 'fields' ][ 'f1' ][ 'name' ],
                                  self.testRegister[ 'fields' ][ 'f1' ][ 'name' ] )
                self.assertEqual( decodedRegister[ 'fields' ][ 'f1' ][ 'size' ],
                                  self.testRegister[ 'fields' ][ 'f1' ][ 'size' ] )
                self.assertEqual( decodedRegister[ 'fields' ][ 'f2' ][ 'name' ],
                                  self.testRegister[ 'fields' ][ 'f2' ][ 'name' ] )
                self.assertEqual( decodedRegister[ 'fields' ][ 'f2' ][ 'size' ],
                                  self.testRegister[ 'fields' ][ 'f2' ][ 'size' ] )

                # Ensure that acquired fields have been added to the field set.
                self.assertEqual( len( self.sourceCollection.fieldSet ), len( self.testRegister[ 'fields' ] ) )
                fieldSetIds = [ x.canonicalId for x in self.sourceCollection.fieldSet ]
                for thisField in decodedRegister[ 'fields' ].values() :
                    self.assertIn( thisField.canonicalId, fieldSetIds )


            def checkParameters() :
                """
                Test the register parameters, other than 'fields', have been recovered correctly.
                """
                nonlocal self, decodedRegister

                self.assertEqual( decodedRegister[ 'constraints' ][ 'fixedAddress' ],
                                  self.testRegister[ 'constraints' ][ 'fixedAddress' ] )
                self.assertEqual( decodedRegister[ 'description' ], self.testRegister[ 'description' ] )
                self.assertEqual( decodedRegister[ 'mode' ], self.testRegister[ 'mode' ] )
                self.assertEqual( decodedRegister[ 'name' ], self.testRegister[ 'name' ] )
                self.assertEqual( decodedRegister[ 'public' ], self.testRegister[ 'public' ] )
                self.assertEqual( decodedRegister[ 'summary' ], self.testRegister[ 'summary' ] )


            def checkBitMap() :
                nonlocal self, decodedRegister

                for thisField in self.acquiredCollection.fieldSet :
                    # Assume that this test indicates the bitmap has acquired itself from YAML correctly;
                    # other bit map specific tests will exhaustively test bit map YAML acquisition.
                    self.assertIn( thisField, decodedRegister.bitMap.destinations )

                    # Check that the reciprocal map has been established.
                    self.assertIn( decodedRegister.bitMap.source, thisField.bitMap.destinations )


            self.testRegister[ 'constraints' ][ 'fixedAddress' ] = 0x10
            self.testRegister[ 'description' ] = 'some description'
            self.testRegister[ 'mode' ] = 'ro'
            self.testRegister[ 'name' ] = 'registerName'
            self.testRegister[ 'public' ] = False
            self.testRegister[ 'summary' ] = 'a summary'

            self.testRegister.addField( 'f1', [ 3, 5 ], (0, 2) )
            self.testRegister.addField( 'f2', [ 7, 7 ], (0, 0) )

            self.assertEqual( self.testRegister.canonicalId, self.testRegister[ 'name' ] )

            encodedYamlData = self.testRegister.to_yamlData()
            log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
            decodedRegister = self.RegisterType.from_yamlData( encodedYamlData, self.testSpace,
                                                               self.acquiredCollection )

            checkFields()
            checkParameters()
            checkBitMap()


        def testDefaultEncodeDecode( self ) :
            encodedYamlData = self.testRegister.to_yamlData()
            log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
            decodedRegister = self.RegisterType.from_yamlData( encodedYamlData, self.testSpace, self.sourceCollection )

            self.assertEqual( len( decodedRegister[ 'fields' ] ), 0 )
            self.assertEqual( len( decodedRegister[ 'constraints' ] ), 0 )
            self.assertEqual( decodedRegister[ 'description' ], '' )
            self.assertEqual( decodedRegister[ 'mode' ], 'rw' )
            self.assertIsNone( decodedRegister[ 'name' ] )
            self.assertEqual( decodedRegister[ 'public' ], True )
            self.assertEqual( decodedRegister[ 'summary' ], '' )


        def testBadYamlDataRaises( self ) :
            yamlData = { 'mode' : 'ro' }
            with self.assertRaisesRegex( ParseError, '^Yaml data does not specify register' ) :
                self.RegisterType.from_yamlData( yamlData, self.testSpace, self.sourceCollection,
                                                 optional = False )


        def testOptionalYamlData( self ) :
            # Specifying an optional YAML decoding when a register YAML encoding is not present must result in a Register
            # populated with default values.
            yamlData = { 'mode' : 'ro' }
            decodedRegister = self.RegisterType.from_yamlData( yamlData, self.testSpace, self.acquiredCollection,
                                                               optional = True )
            self.assertEqual( len( decodedRegister[ 'fields' ] ), 0 )
            self.assertEqual( len( decodedRegister[ 'constraints' ] ), 0 )
            self.assertEqual( decodedRegister[ 'description' ], '' )
            self.assertEqual( decodedRegister[ 'mode' ], 'rw' )
            self.assertIsNone( decodedRegister[ 'name' ] )
            self.assertEqual( decodedRegister[ 'public' ], True )
            self.assertEqual( decodedRegister[ 'summary' ], '' )


        def testRegisterWithFieldLargerThanOneByte( self ) :
            expectedRegisterSizeBits = 16

            self.testRegister[ 'name' ] = 'registerName'

            self.testRegister.addField( 'f1', (0, 11) )

            self.assertEqual( expectedRegisterSizeBits, self.testRegister.sizeBits )

            self.assertEqual( self.testRegister.canonicalId, self.testRegister[ 'name' ] )

            encodedYamlData = self.testRegister.to_yamlData()
            log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
            decodedRegister = self.RegisterType.from_yamlData( encodedYamlData, self.testSpace,
                                                               self.acquiredCollection )

            self.assertEqual( self.testRegister[ 'name' ], decodedRegister[ 'name' ] )
            self.assertEqual( expectedRegisterSizeBits, decodedRegister.sizeBits )


        def testRegisterWithMultiplesFieldsAcrossByteBoundary( self ) :
            expectedRegisterSizeBits = 16

            self.testRegister[ 'name' ] = 'registerName'

            # This field allocation implies a two byte register required to encapsulate them.
            self.testRegister.addField( 'f1', (3, 5) )
            self.testRegister.addField( 'f2', (10, 11) )

            self.assertEqual( expectedRegisterSizeBits, self.testRegister.sizeBits )

            self.assertEqual( self.testRegister.canonicalId, self.testRegister[ 'name' ] )

            encodedYamlData = self.testRegister.to_yamlData()
            log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
            decodedRegister = self.RegisterType.from_yamlData( encodedYamlData, self.testSpace,
                                                               self.acquiredCollection )

            self.assertEqual( self.testRegister[ 'name' ], decodedRegister[ 'name' ] )
            self.assertEqual( expectedRegisterSizeBits, decodedRegister.sizeBits )


    class TestRegisterYamlParameters( unittest.TestCase ) :
        # The tests will fail unless a test case loader correctly fulfills this value.
        RegisterType = None


        def setUp( self ) :
            self.setCollection = SetCollection()
            self.testSpace = MemorySpace()
            self.testRegister = self.RegisterType( self.testSpace,
                                                   setCollection = self.setCollection )

            self.previousRegister = MockPreviousRegister( endAddress = 0x3e7,
                                                          sizeMemoryUnits = 4 )
            self.testRegister.previousElement = self.previousRegister

            self.observer = MockObserver()
            self.testRegister.sizeChangeNotifier.addObserver( self.observer )


        def testYamlDataSpan( self ) :
            # The address data is automatically generated so it is prefixed by '_'.
            expectedName = '_sizeMemoryUnits'
            expectedValue = 1

            self.assertEqual( expectedValue, self.testRegister.sizeMemoryUnits )

            yamlData = self.testRegister.to_yamlData()
            self.assertEqual( expectedValue, yamlData[ 'register' ][ expectedName ] )


    class TestRegisterYamlLoadSaveCanonicalId( unittest.TestCase ) :
        # The tests will fail unless a test case loader correctly fulfills this value.
        RegisterType = None


        def setUp( self ) :
            self.sourceCollection = SetCollection()
            self.space = MemorySpace()
            self.module = MockModule( 'module' )

            self.acquiredCollection = SetCollection()


        def testEncodeDecode( self ) :
            """
            The canonical ID of the decoded register much match that of the encoded register and is expected to include the
            module canonical ID.
            :return:
            """
            testRegister = self.RegisterType( self.space,
                                              parent = self.module,
                                              setCollection = self.sourceCollection )
            testRegister[ 'name' ] = 'register'

            self.sourceCollection.registerSet.add( testRegister )

            self.assertEqual( 'module.register', testRegister.canonicalId )

            encodedYamlData = testRegister.to_yamlData()
            log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
            decodedRegister = self.RegisterType.from_yamlData( encodedYamlData, self.space, self.acquiredCollection,
                                                               parent = self.module )

            self.assertEqual( testRegister.canonicalId, decodedRegister.canonicalId )
            self.assertEqual( 'module.register', testRegister.canonicalId )


    class TestLoadSaveUserDefinedParameter( unittest.TestCase ) :
        # The tests will fail unless a test case loader correctly fulfills this value.
        RegisterType = None


        def setUp( self ) :
            self.sourceCollection = SetCollection()
            self.testSpace = MemorySpace()
            self.registerUnderTest = self.RegisterType( self.testSpace,
                                                        setCollection = self.sourceCollection )

            self.observer = MockObserver()
            self.registerUnderTest.sizeChangeNotifier.addObserver( self.observer )

            self.acquiredCollection = SetCollection()


        def testEncodeDecode( self ) :
            expectedValue = 'some value'

            self.registerUnderTest[ 'my-parameter' ] = expectedValue

            encodedYamlData = self.registerUnderTest.to_yamlData()
            log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
            decodedRegister = self.RegisterType.from_yamlData( encodedYamlData, self.testSpace,
                                                               self.acquiredCollection )

            self.assertEqual( expectedValue, decodedRegister[ 'my-parameter' ] )
