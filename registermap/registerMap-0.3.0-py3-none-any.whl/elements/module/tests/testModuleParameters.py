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

import unittest

import registerMap.elements.base as rmbs
import registerMap.structure.memory.space as rmms

from registerMap.set import SetCollection

from ..module import \
    Module, \
    ParseError, \
    RegisterInstance
from ..parameters import RegistersParameter

class TestModuleRegistersParameter( unittest.TestCase ) :
    def setUp( self ) :
        self.sourceCollection = SetCollection()
        self.memorySpace = rmms.MemorySpace()
        self.module = Module( self.memorySpace, self.sourceCollection )

        self.acquiredCollection = SetCollection()


    def testInitialization( self ) :
        p = RegistersParameter( self.module )

        self.assertEqual( p.name, 'registers' )
        self.assertTrue( isinstance( p.value, rmbs.ElementList ) )


    def testEmptyBitFieldsToYamlData( self ) :
        p = RegistersParameter( self.module )

        expectedYamlData = { 'registers' : list() }
        actualYamlData = p.to_yamlData()

        self.assertEqual( actualYamlData, expectedYamlData )


    def testSingleRegisterToYamlData( self ) :
        p = RegistersParameter( self.module )
        p.value[ 'r1' ] = self.createRegister( 'r1' )

        expectedYamlData = { 'registers' : [
            p.value[ 'r1' ].to_yamlData()
        ] }
        actualYamlData = p.to_yamlData()

        self.assertEqual( actualYamlData, expectedYamlData )


    def testMultipleRegistersToYamlData( self ) :
        p = RegistersParameter( self.module )
        p.value[ 'r1' ] = self.createRegister( 'r1' )
        p.value[ 'r2' ] = self.createRegister( 'r2', 0x12 )

        expectedYamlData = { 'registers' : [
            p.value[ 'r1' ].to_yamlData(),
            p.value[ 'r2' ].to_yamlData()
        ] }
        actualYamlData = p.to_yamlData()

        self.assertEqual( actualYamlData, expectedYamlData )


    def createRegister( self, name,
                        fixedAddress = 0x10 ) :
        register = RegisterInstance( self.memorySpace,
                                     setCollection = self.sourceCollection )
        register[ 'constraints' ][ 'fixedAddress' ] = fixedAddress
        register[ 'description' ] = 'some description'
        register[ 'mode' ] = 'ro'
        register[ 'name' ] = name
        register[ 'public' ] = False
        register[ 'summary' ] = 'a summary'

        register.addField( 'f1', [ 3, 5 ], (0, 2) )
        register.addField( 'f2', [ 7, 7 ], (0, 0) )

        return register


    def testFromGoodYamlData( self ) :
        p = RegistersParameter( self.module )
        p.value[ 'r1' ] = self.createRegister( 'r1' )
        p.value[ 'r2' ] = self.createRegister( 'r2', 0x12 )

        yamlData = p.to_yamlData()
        gp = RegistersParameter.from_yamlData( yamlData, self.module, self.memorySpace, self.acquiredCollection )

        self.assertEqual( gp.value[ 'r1' ][ 'fields' ][ 'f1' ][ 'name' ], 'f1' )
        self.assertEqual( gp.value[ 'r1' ][ 'fields' ][ 'f1' ][ 'size' ], 3 )
        self.assertEqual( gp.value[ 'r1' ][ 'fields' ][ 'f2' ][ 'name' ], 'f2' )
        self.assertEqual( gp.value[ 'r1' ][ 'fields' ][ 'f2' ][ 'size' ], 1 )

        self.assertEqual( gp.value[ 'r2' ][ 'fields' ][ 'f1' ][ 'name' ], 'f1' )
        self.assertEqual( gp.value[ 'r2' ][ 'fields' ][ 'f1' ][ 'size' ], 3 )
        self.assertEqual( gp.value[ 'r2' ][ 'fields' ][ 'f2' ][ 'name' ], 'f2' )
        self.assertEqual( gp.value[ 'r2' ][ 'fields' ][ 'f2' ][ 'size' ], 1 )


    def testFromBadYamlData( self ) :
        yamlData = { 'mode' : 'ro' }
        with self.assertRaisesRegex( ParseError, '^Registers not defined in yaml data' ) :
            RegistersParameter.from_yamlData( yamlData, self.module, self.memorySpace, self.acquiredCollection )


    def testOptionalYamlData( self ) :
        yamlData = { 'mode' : 'ro' }
        gp = RegistersParameter.from_yamlData( yamlData, self.module, self.memorySpace, self.sourceCollection,
                                                   optional = True )


if __name__ == '__main__' :
    unittest.main()
