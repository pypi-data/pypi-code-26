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

from registerMap.elements.register import RegisterInstance

from ..field import \
    Field, \
    ParseError

from registerMap.elements.tests.mockObserver import MockObserver


log = logging.getLogger( __name__ )


class TestLoadSaveGlobalField( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.testField = Field()

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testEncodeDecodeGlobalField( self ) :
        self.testField[ 'description' ] = 'some description'
        self.testField[ 'name' ] = 'f1'
        self.testField[ 'size' ] = 8
        self.testField[ 'resetValue' ] = 0x5a
        self.testField[ 'summary' ] = 'a summary'

        self.assertTrue( self.testField[ 'global' ] )

        encodedYamlData = self.testField.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = Field.from_yamlData( encodedYamlData )

        self.assertEqual( decodedData[ 'description' ], self.testField[ 'description' ] )
        self.assertEqual( decodedData[ 'name' ], self.testField[ 'name' ] )
        self.assertEqual( decodedData[ 'resetValue' ], self.testField[ 'resetValue' ] )
        self.assertEqual( decodedData[ 'summary' ], self.testField[ 'summary' ] )
        self.assertTrue( decodedData[ 'global' ] )


    def testEncodeDecodeLocalField( self ) :
        self.testField[ 'description' ] = 'some description'
        self.testField[ 'name' ] = 'f1'
        self.testField[ 'size' ] = 8
        self.testField[ 'resetValue' ] = 0x5a
        self.testField[ 'summary' ] = 'a summary'

        self.assertTrue( self.testField[ 'global' ] )

        encodedYamlData = self.testField.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = Field.from_yamlData( encodedYamlData )

        self.assertEqual( decodedData[ 'description' ], self.testField[ 'description' ] )
        self.assertEqual( decodedData[ 'name' ], self.testField[ 'name' ] )
        self.assertEqual( decodedData[ 'resetValue' ], self.testField[ 'resetValue' ] )
        self.assertEqual( decodedData[ 'summary' ], self.testField[ 'summary' ] )
        self.assertTrue( decodedData[ 'global' ] )


    def testOptionalDescription( self ) :
        self.testField[ 'name' ] = 'f1'
        self.testField[ 'size' ] = 8
        self.testField[ 'resetValue' ] = 0x5a
        self.testField[ 'summary' ] = 'a summary'

        encodedYamlData = self.testField.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = Field.from_yamlData( encodedYamlData )

        self.assertEqual( decodedData[ 'description' ], '' )


    def testOptionalSummary( self ) :
        self.testField[ 'description' ] = 'some description'
        self.testField[ 'name' ] = 'f1'
        self.testField[ 'size' ] = 8
        self.testField[ 'resetValue' ] = 0x5a

        encodedYamlData = self.testField.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = Field.from_yamlData( encodedYamlData )

        self.assertEqual( decodedData[ 'description' ], self.testField[ 'description' ] )
        self.assertEqual( decodedData[ 'name' ], self.testField[ 'name' ] )
        self.assertEqual( decodedData[ 'resetValue' ], self.testField[ 'resetValue' ] )
        self.assertEqual( decodedData[ 'summary' ], '' )


    def testFieldLargerThanOneByte( self ) :
        self.testField[ 'name' ] = 'f1'
        self.testField[ 'size' ] = 11

        encodedYamlData = self.testField.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = Field.from_yamlData( encodedYamlData )

        self.assertEqual( decodedData[ 'name' ], self.testField[ 'name' ] )
        self.assertEqual( decodedData[ 'size' ], self.testField[ 'size' ] )


class TestLoadSaveLocalField( unittest.TestCase ) :
    def setUp( self ) :
        self.parentRegister = self.generateRegister( 'registerName' )
        self.sourceField = Field( parent = self.parentRegister )


    @staticmethod
    def generateRegister( name ) :
        """
        Generate mock parent register for the test.

        :param name:
        :return:
        """
        thisRegister = unittest.mock.create_autospec( RegisterInstance )

        pn = unittest.mock.PropertyMock( return_value = name )
        type( thisRegister ).name = pn

        pci = unittest.mock.PropertyMock( return_value = name )
        type( thisRegister ).canonicalId = pci

        return thisRegister


    def testEncodeDecodeLocalField( self ) :
        self.sourceField[ 'name' ] = 'f1'
        self.sourceField[ 'size' ] = 8
        self.sourceField[ 'resetValue' ] = 0x5a

        self.assertFalse( self.sourceField[ 'global' ] )
        self.assertEqual( self.sourceField.canonicalId, 'registerName.f1' )

        encodedYamlData = self.sourceField.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = Field.from_yamlData( encodedYamlData,
                                           parentRegister = self.parentRegister )

        self.assertFalse( decodedData[ 'global' ] )
        self.assertEqual( decodedData.canonicalId, 'registerName.f1' )


    def testDecodeMissingParentRaises( self ) :
        self.sourceField[ 'name' ] = 'f1'
        self.sourceField[ 'size' ] = 8
        self.sourceField[ 'resetValue' ] = 0x5a

        self.assertFalse( self.sourceField[ 'global' ] )
        self.assertEqual( self.sourceField.canonicalId, 'registerName.f1' )

        encodedYamlData = self.sourceField.to_yamlData()
        with self.assertRaisesRegex( ParseError,
                                     '^Parent register not specified for YAML acquisition of a local field' ) :
            Field.from_yamlData( encodedYamlData )


    def testDecodeWrongParentRaises( self ) :
        self.sourceField[ 'name' ] = 'f1'
        self.sourceField[ 'size' ] = 8
        self.sourceField[ 'resetValue' ] = 0x5a

        self.assertFalse( self.sourceField[ 'global' ] )
        self.assertEqual( self.sourceField.canonicalId, 'registerName.f1' )

        otherRegister = self.generateRegister( 'otherRegister' )

        encodedYamlData = self.sourceField.to_yamlData()
        with self.assertRaisesRegex( ParseError,
                                     '^Parent register does not match YAML specification' ) :
            Field.from_yamlData( encodedYamlData,
                                 parentRegister = otherRegister )


class TestLoadSaveUserDefinedParameters( unittest.TestCase ) :
    def setUp( self ) :
        self.parentRegister = self.generateRegister( 'registerName' )
        self.sourceField = Field( parent = self.parentRegister )


    @staticmethod
    def generateRegister( name ) :
        """
        Generate mock parent register for the test.

        :param name:
        :return:
        """
        thisRegister = unittest.mock.create_autospec( RegisterInstance )

        pn = unittest.mock.PropertyMock( return_value = name )
        type( thisRegister ).name = pn

        pci = unittest.mock.PropertyMock( return_value = name )
        type( thisRegister ).canonicalId = pci

        return thisRegister


    def testEncodeDecodeUserDefinedParameters( self ) :
        expectedValue = 'some value'

        self.sourceField[ 'name' ] = 'f1'
        self.sourceField[ 'size' ] = 8
        self.sourceField[ 'resetValue' ] = 0x5a

        self.assertFalse( self.sourceField[ 'global' ] )
        self.assertEqual( self.sourceField.canonicalId, 'registerName.f1' )

        self.sourceField[ 'my-parameter' ] = expectedValue

        encodedYamlData = self.sourceField.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = Field.from_yamlData( encodedYamlData,
                                           parentRegister = self.parentRegister )

        self.assertEqual( expectedValue, decodedData[ 'my-parameter' ] )


if __name__ == '__main__' :
    unittest.main()
