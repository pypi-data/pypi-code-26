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

from registerMap.registerMap import \
    ParseError, \
    RegisterMap


log = logging.getLogger( __name__ )


class TestYamlLoadSave( unittest.TestCase ) :
    def testEncodeDecode( self ) :
        m = RegisterMap()

        m.memory.addressBits = 48
        m.memory.baseAddress = 0x1000
        m.memory.memoryUnitBits = 16
        m.memory.pageSize = 128
        m[ 'description' ] = 'some description'
        m[ 'summary' ] = 'a summary'
        self.createSampleModule( m, 'm1' )

        encodedYamlData = m.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedMap = RegisterMap.from_yamlData( encodedYamlData )

        self.assertEqual( decodedMap.memory.addressBits, m.memory.addressBits )
        self.assertEqual( decodedMap.memory.baseAddress, m.memory.baseAddress )
        self.assertEqual( decodedMap.memory.memoryUnitBits, m.memory.memoryUnitBits )
        self.assertEqual( decodedMap.memory.pageSize, m.memory.pageSize )
        self.assertEqual( decodedMap[ 'description' ], m[ 'description' ] )
        self.assertEqual( decodedMap[ 'summary' ], m[ 'summary' ] )

        self.assertEqual( len( decodedMap[ 'modules' ] ), len( m[ 'modules' ] ) )
        self.assertEqual( decodedMap[ 'modules' ][ 'm1' ][ 'name' ], 'm1' )


    def createSampleModule( self, thisMap, moduleName ) :
        sampleModule = thisMap.addModule( moduleName )

        registerName = 'r1'
        sampleModule.addRegister( registerName )

        sampleModule[ 'registers' ][ registerName ][ 'constraints' ][ 'fixedAddress' ] = 0x1010
        sampleModule[ 'registers' ][ registerName ][ 'description' ] = 'some description'
        sampleModule[ 'registers' ][ registerName ][ 'mode' ] = 'ro'
        sampleModule[ 'registers' ][ registerName ][ 'public' ] = False
        sampleModule[ 'registers' ][ registerName ][ 'summary' ] = 'a summary'

        sampleModule[ 'registers' ][ registerName ].addField( 'f1', [ 3, 5 ], (3, 5) )
        sampleModule[ 'registers' ][ registerName ].addField( 'f2', [ 7, 7 ], (7, 7) )


    def testFromBadYamlDataRaises( self ) :
        yamlData = { 'mode' : 'ro' }

        with self.assertRaisesRegex( ParseError, '^RegisterMap is not defined in yaml data' ) :
            RegisterMap.from_yamlData( yamlData,
                                       optional = False )


    def testOptionalYamlData( self ) :
        yamlData = { 'mode' : 'ro' }

        m = RegisterMap.from_yamlData( yamlData,
                                          optional = True )

        self.assertEqual( m.memory.addressBits, 32 )
        self.assertEqual( m.memory.baseAddress, 0 )
        self.assertEqual( m.memory.memoryUnitBits, 8 )
        self.assertIsNone( m.memory.pageSize )
        self.assertEqual( len( m[ 'modules' ] ), 0 )


    def testSynchronization( self ) :
        thisMap = RegisterMap()

        thisMap.memory.addressBits = 48
        thisMap.memory.baseAddress = 0
        thisMap.memory.memoryUnitBits = 8
        thisMap.memory.pageSize = None

        m1 = thisMap.addModule( 'm1' )
        r1 = m1.addRegister( 'r1' )
        m2 = thisMap.addModule( 'm2' )
        r2 = m2.addRegister( 'r2' )
        r2.addField( 'f2', [ 3, 10 ], (3, 10) )
        r2[ 'constraints' ][ 'fixedAddress' ] = 0x15

        encodedYamlData = thisMap.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedMap = RegisterMap.from_yamlData( encodedYamlData )

        # Changing the base address for each map must mean that elements end up with the same addresses.
        thisMap.memory.baseAddress = 0x10
        decodedMap.memory.baseAddress = 0x10

        # Existing registers and modules must reflect the base address change.
        self.assertEqual( decodedMap[ 'modules' ][ 'm1' ].baseAddress, m1.baseAddress )
        self.assertEqual( decodedMap[ 'modules' ][ 'm1' ][ 'registers' ][ 'r1' ].address, r1.address )
        self.assertEqual( decodedMap[ 'modules' ][ 'm2' ].baseAddress, m2.baseAddress )
        self.assertEqual( decodedMap[ 'modules' ][ 'm2' ][ 'registers' ][ 'r2' ].address, r2.address )


if __name__ == '__main__' :
    unittest.main()
