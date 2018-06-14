#
# Copyright 2017 Russell Smiley
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

import collections
import unittest

from registerMap.exceptions import ConfigurationError

from ..register import BitFieldsParameter, Field, ModeParameter, PublicParameter


class TestBitFieldsParameter( unittest.TestCase ) :
    def testInitialization( self ) :
        p = BitFieldsParameter()

        self.assertEqual( p.name, 'bitFields' )
        self.assertTrue( isinstance( p.value, collections.OrderedDict ) )


    def testEmptyBitFieldsToYamlData( self ) :
        p = BitFieldsParameter()

        expectedYamlData = { 'bitFields' : list() }
        actualYamlData = p.to_yamlData()

        self.assertEqual( actualYamlData, expectedYamlData )


    def testSingleBitFieldToYamlData( self ) :
        p = BitFieldsParameter()
        p.value[ 'f1' ] = self.createBitField( 'f1', 3 )

        expectedYamlData = { 'bitFields' : [
            p.value[ 'f1' ].to_yamlData()
        ] }
        actualYamlData = p.to_yamlData()

        self.assertEqual( actualYamlData, expectedYamlData )


    def testMultipleBitFieldToYamlData( self ) :
        p = BitFieldsParameter()
        p.value[ 'f1' ] = self.createBitField( 'f1', 3 )
        p.value[ 'f2' ] = self.createBitField( 'f2', 1 )

        expectedYamlData = { 'bitFields' : [
            p.value[ 'f1' ].to_yamlData(),
            p.value[ 'f2' ].to_yamlData()
        ] }
        actualYamlData = p.to_yamlData()

        self.assertEqual( actualYamlData, expectedYamlData )


    def createBitField( self, name, size ) :
        b = Field()
        b[ 'name' ] = name
        b[ 'size' ] = size

        return b


    def testFromGoodYamlData( self ) :
        p = BitFieldsParameter()
        p.value[ 'f1' ] = self.createBitField( 'f1', 3 )
        p.value[ 'f2' ] = self.createBitField( 'f2', 1 )

        yamlData = p.to_yamlData()
        gp = BitFieldsParameter.from_yamlData( yamlData )

        self.assertEqual( gp.value[ 'f1' ][ 'name' ], 'f1' )
        self.assertEqual( gp.value[ 'f1' ][ 'size' ], 3 )
        self.assertEqual( gp.value[ 'f2' ][ 'name' ], 'f2' )
        self.assertEqual( gp.value[ 'f2' ][ 'size' ], 1 )


    def testOptionalYamlData( self ) :
        yamlData = { 'mode' : 'ro' }
        gp = BitFieldsParameter.from_yamlData( yamlData,
                                                    optional = True )


class TestModeParameter( unittest.TestCase ) :
    def testInitialization( self ) :
        expectedName = 'mode'
        expectedValue = 'rw'
        p = ModeParameter( expectedValue )

        self.assertEqual( p.name, expectedName )
        self.assertEqual( p.value, expectedValue )


    def testInitializationBadValueRaises( self ) :
        badValue = 'badValue'
        with self.assertRaisesRegex( ConfigurationError, '^Invalid value' ) :
            ModeParameter( badValue )


    def testGoodValueInitializationNoRaise( self ) :
        for value in ModeParameter.validModes :
            ModeParameter( value )


    def testValidateBadValueRaises( self ) :
        p = ModeParameter( 'rw' )

        badValue = 'badValue'
        with self.assertRaisesRegex( ConfigurationError, '^Invalid value' ) :
            p.validate( badValue )


    def testToYamlData( self ) :
        expectedValue = 'ro'
        p = ModeParameter( expectedValue )

        expectedYamlData = { 'mode' : expectedValue }
        actualYamlData = p.to_yamlData()

        self.assertEqual( actualYamlData, expectedYamlData )


    def testFromGoodYamlData( self ) :
        expectedValue = 'ro'
        yamlData = { 'mode' : expectedValue }

        p = ModeParameter.from_yamlData( yamlData )

        self.assertEqual( p.name, 'mode' )
        self.assertEqual( p.value, expectedValue )


    def testBadYamlDataRaises( self ) :
        yamlData = { 'mode' : 'badvalue' }

        with self.assertRaisesRegex( ConfigurationError, '^Invalid value' ) :
            ModeParameter.from_yamlData( yamlData )


    def testOptionalYamlData( self ) :
        yamlData = { 'public' : True }

        p = ModeParameter.from_yamlData( yamlData,
                                              optional = True )

        self.assertEqual( p.name, 'mode' )
        self.assertEqual( p.value, 'rw' )


class TestPublicParameter( unittest.TestCase ) :
    def testInitialization( self ) :
        expectedName = 'public'
        expectedValue = True
        p = PublicParameter( expectedValue )

        self.assertEqual( p.name, expectedName )
        self.assertEqual( p.value, expectedValue )


    def testInitializationBadValueRaises( self ) :
        badValue = 1
        with self.assertRaisesRegex( ConfigurationError, '^Public must be specified as boolean' ) :
            PublicParameter( badValue )


    def testValidateBadValueRaises( self ) :
        p = PublicParameter( False )

        badValue = 1
        with self.assertRaisesRegex( ConfigurationError, '^Public must be specified as boolean' ) :
            p.validate( badValue )


    def testToYamlData( self ) :
        expectedValue = True
        p = PublicParameter( expectedValue )

        expectedYamlData = { 'public' : expectedValue }
        actualYamlData = p.to_yamlData()

        self.assertEqual( actualYamlData, expectedYamlData )


    def testFromGoodYamlData( self ) :
        expectedValues = [ True, False ]

        for expectedValue in expectedValues :
            yamlData = { 'public' : expectedValue }

            p = PublicParameter.from_yamlData( yamlData )

            self.assertEqual( p.name, 'public' )
            self.assertEqual( p.value, expectedValue )


    def testBadYamlDataRaises( self ) :
        yamlData = { 'public' : 'true' }

        with self.assertRaisesRegex( ConfigurationError, '^Public must be specified as boolean' ) :
            PublicParameter.from_yamlData( yamlData )


    def testOptionalYamlData( self ) :
        expectedValue = True

        yamlData = { 'other' : 'somevalue' }

        p = PublicParameter.from_yamlData( yamlData,
                                                optional = True )

        self.assertEqual( p.name, 'public' )
        self.assertEqual( p.value, expectedValue )


if __name__ == '__main__' :
    unittest.main()
