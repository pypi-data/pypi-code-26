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

from ..registerMap import RegisterMap


class TestRegisterMapSpan( unittest.TestCase ) :
    def setUp( self ) :
        self.mapUnderTest = RegisterMap()


    def testContiguousRegisterSpan( self ) :
        m1 = self.mapUnderTest.addModule( 'm1' )

        # Two byte register
        r1 = m1.addRegister( 'r1' )
        r1.addField( 'f1', (0, 11) )

        self.assertEqual( 2, r1.sizeMemoryUnits )
        expectedModuleSize = r1.sizeMemoryUnits
        self.assertEqual( expectedModuleSize, m1.spanMemoryUnits )

        # Single byte register
        r2 = m1.addRegister( 'r2' )
        r2.addField( 'f1', (0, 3) )
        r2.addField( 'f2', (4, 6) )

        self.assertEqual( 1, r2.sizeMemoryUnits )

        expectedModuleSize = r1.sizeMemoryUnits + r2.sizeMemoryUnits
        self.assertEqual( expectedModuleSize, m1.spanMemoryUnits )

        self.assertEqual( expectedModuleSize, self.mapUnderTest.spanMemoryUnits )


    def testContiguousRegisterSpanMultipleModules( self ) :
        m1 = self.mapUnderTest.addModule( 'm1' )

        # Two byte register
        r1 = m1.addRegister( 'r1' )
        r1.addField( 'f1', (0, 11) )

        self.assertEqual( 2, r1.sizeMemoryUnits )
        expectedModuleSize = r1.sizeMemoryUnits
        self.assertEqual( expectedModuleSize, m1.spanMemoryUnits )

        m2 = self.mapUnderTest.addModule( 'm2' )

        # Single byte register
        r2 = m2.addRegister( 'r2' )
        r2.addField( 'f1', (0, 3) )
        r2.addField( 'f2', (4, 6) )

        self.assertEqual( 1, r2.sizeMemoryUnits )

        expectedM1Size = r1.sizeMemoryUnits
        self.assertEqual( expectedM1Size, m1.spanMemoryUnits )

        expectedM2Size = r2.sizeMemoryUnits
        self.assertEqual( expectedM2Size, m2.spanMemoryUnits )

        expectedMapSize = expectedM1Size + expectedM2Size

        self.assertEqual( expectedMapSize, self.mapUnderTest.spanMemoryUnits )


    def testDiscontiguousRegisterSpan( self ) :
        m1 = self.mapUnderTest.addModule( 'm1' )

        # Two byte register
        r1 = m1.addRegister( 'r1' )
        r1.addField( 'f1', (0, 11) )

        self.assertEqual( 2, r1.sizeMemoryUnits )
        expectedModuleSize = r1.sizeMemoryUnits
        self.assertEqual( expectedModuleSize, m1.spanMemoryUnits )

        # Three byte register
        r2 = m1.addRegister( 'r2' )
        r2.addField( 'f1', (0, 3) )
        r2.addField( 'f2', (4, 17) )

        self.assertEqual( 3, r2.sizeMemoryUnits )

        r2[ 'constraints' ][ 'fixedAddress' ] = 0x15

        expectedModuleSize = r2.sizeMemoryUnits + r2.offset
        self.assertEqual( expectedModuleSize, m1.spanMemoryUnits )

        self.assertEqual( expectedModuleSize, self.mapUnderTest.spanMemoryUnits )


    def testDiscontiguousRegisterSpanMultipleModules( self ) :
        expectedM2AddressOffset = 0x15

        self.assertEqual( 0, self.mapUnderTest.memory.baseAddress )

        m1 = self.mapUnderTest.addModule( 'm1' )

        # Two byte register
        r1 = m1.addRegister( 'r1' )
        r1.addField( 'f1', (0, 11) )

        self.assertEqual( 2, r1.sizeMemoryUnits )
        expectedModuleSize = r1.sizeMemoryUnits
        self.assertEqual( expectedModuleSize, m1.spanMemoryUnits )

        m2 = self.mapUnderTest.addModule( 'm2' )
        m2[ 'constraints' ][ 'fixedAddress' ] = expectedM2AddressOffset

        # Single byte register
        r2 = m2.addRegister( 'r2' )
        r2.addField( 'f1', (0, 3) )
        r2.addField( 'f2', (4, 6) )

        self.assertEqual( 1, r2.sizeMemoryUnits )

        expectedM1Size = r1.sizeMemoryUnits
        self.assertEqual( expectedM1Size, m1.spanMemoryUnits )

        expectedM2Size = r2.sizeMemoryUnits
        self.assertEqual( expectedM2Size, m2.spanMemoryUnits )

        expectedMapSize = expectedM2AddressOffset + expectedM2Size

        self.assertEqual( expectedMapSize, self.mapUnderTest.spanMemoryUnits )


if __name__ == '__main__' :
    unittest.main()
