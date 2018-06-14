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
import registerMap.registerMap as rm
import registerMap.structure.memory.space as rmm

from registerMap.set import SetCollection


class TestModulesParameter( unittest.TestCase ) :
    def setUp( self ) :
        self.sourceFieldSet = SetCollection()
        self.testMemory = rmm.MemorySpace()
        self.registerMap = rm.RegisterMap()

        self.acquiredFieldSet = SetCollection()


    def testInitialization( self ) :
        p = rm.ModulesParameter( self.registerMap )

        self.assertEqual( p.name, 'modules' )
        self.assertTrue( isinstance( p.value, rmbs.ElementList ) )


    def testEmptyYamlLoadSave( self ) :
        p = rm.ModulesParameter( self.registerMap )

        generatedYamlData = p.to_yamlData()
        decodedModules = rm.ModulesParameter.from_yamlData(
            generatedYamlData, self.registerMap, self.testMemory, self.acquiredFieldSet )

        self.assertEqual( len( decodedModules.value ), 0 )


    def testSingleModuleYamlLoadSave( self ) :
        module = self.createSampleModule( 'm1' )

        p = rm.ModulesParameter( self.registerMap )
        p.value[ module[ 'name' ] ] = module

        generatedYamlData = p.to_yamlData()
        decodedModules = rm.ModulesParameter.from_yamlData(
            generatedYamlData, self.registerMap, self.testMemory, self.acquiredFieldSet )

        self.assertEqual( decodedModules.value[ 'm1' ][ 'description' ], p.value[ 'm1' ][ 'description' ] )
        self.assertEqual( decodedModules.value[ 'm1' ][ 'name' ], p.value[ 'm1' ][ 'name' ] )
        self.assertEqual( decodedModules.value[ 'm1' ][ 'summary' ], p.value[ 'm1' ][ 'summary' ] )


    def createSampleModule( self, name ) :
        module = rm.Module( self.testMemory, self.sourceFieldSet )

        module[ 'name' ] = name

        register = module.addRegister( 'r1' )

        register.addField( 'f1', [ 3, 5 ], (3, 5) )
        register.addField( 'f2', [ 7, 7 ], (7, 7) )

        return module


    def testFromOptionalYamlData( self ) :
        yamlData = { 'mode' : 'ro' }
        decodedModules = rm.ModulesParameter.from_yamlData(
            yamlData, self.registerMap, self.testMemory, self.acquiredFieldSet,
            optional = True )

        self.assertEqual( len( decodedModules.value ), 0 )


if __name__ == '__main__' :
    unittest.main()
