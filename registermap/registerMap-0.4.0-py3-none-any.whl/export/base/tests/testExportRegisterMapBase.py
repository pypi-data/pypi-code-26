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

import unittest.mock

from registerMap import RegisterMap

from ..registerMap import RegisterMapBase
from ..memory import MemoryBase

from .mocks import \
    MockField, \
    MockMemory, \
    MockModule, \
    MockRegister


MOCK_TYPE_CONFIGURATION = {
    'field' : MockField,
    'memory' : MockMemory,
    'module' : MockModule,
    'register' : MockRegister,
}


class TestRegisterMapBase( unittest.TestCase ) :

    def setUp( self ) :
        self.registerMap = RegisterMap()

        m1 = self.registerMap.addModule( 'm1' )
        m1 = self.registerMap.addModule( 'm2' )


    def testMemoryProperty( self ) :
        exporterUnderTest = RegisterMapBase( 'thisRegisterMap', self.registerMap, MOCK_TYPE_CONFIGURATION )

        self.assertTrue( isinstance( exporterUnderTest.memory, MemoryBase ) )
        self.assertEqual(self.registerMap.spanMemoryUnits, exporterUnderTest.memory.size)


    def testModuleIndirection( self ) :
        exporterUnderTest = RegisterMapBase( 'thisRegisterMap', self.registerMap, MOCK_TYPE_CONFIGURATION )

        for expectedName, thisModule in zip( [ 'm1', 'm2' ], exporterUnderTest.modules ) :
            self.assertEqual( expectedName, thisModule.name )


    def testSpanMemoryUnitsProperty( self ) :
        exporterUnderTest = RegisterMapBase( 'thisRegisterMap', self.registerMap, MOCK_TYPE_CONFIGURATION )

        self.assertEqual( self.registerMap.spanMemoryUnits, exporterUnderTest.spanMemoryUnits )


if __name__ == '__main__' :
    unittest.main()
