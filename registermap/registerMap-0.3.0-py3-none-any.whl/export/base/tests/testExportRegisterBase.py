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

from registerMap import RegisterMap

from ..register import RegisterBase

from .mocks import \
    MockField, \
    MockRegister


class TestExportRegisterBase( unittest.TestCase ) :

    def setUp( self ) :
        self.registerMap = RegisterMap()
        self.module1 = self.registerMap.addModule( 'm1' )

        self.register1 = self.module1.addRegister( 'r1' )

        self.exportUnderTest = MockRegister( self.register1, MockField )


    def testName( self ) :
        self.assertEqual( self.register1[ 'name' ], self.exportUnderTest.name )


    def testEmptyRegister( self ) :
        self.assertEqual( 0, len( self.exportUnderTest.fields ) )


    def testAddressProperty( self ) :
        self.assertEqual( self.exportUnderTest.expectedAddress, self.exportUnderTest.address )


    def testOffsetProperty( self ) :
        self.assertEqual( self.exportUnderTest.expectedOffset, self.exportUnderTest.offset )


    def testFields( self ) :
        self.register1.addField( 'f1', (0, 2) )
        self.register1.addField( 'f2', (3, 4) )
        self.register1.addField( 'f3', (5, 7) )

        for expectedName, expectedSize, thisField in zip( [ 'f1', 'f2', 'f3' ], [ 3, 2, 3 ],
                                                          self.exportUnderTest.fields ) :
            self.assertEqual( expectedName, thisField.name )
            self.assertEqual( expectedSize, thisField.size )


class TestRegisterBasePrecedingGapProperty( unittest.TestCase ) :

    def setUp( self ) :
        self.registerMap = RegisterMap()
        self.module1 = self.registerMap.addModule( 'm1' )

        self.register1 = self.module1.addRegister( 'r1' )

        self.assertEqual( 0, self.register1.address )


    def testType( self ) :
        r2 = self.module1.addRegister( 'r2' )

        self.assertEqual( 1, r2.address )

        exportUnderTest = RegisterBase( r2, MockField )

        self.assertTrue( isinstance( exportUnderTest.precedingGapBytes, int ) )


    def testZeroGap( self ) :
        r2 = self.module1.addRegister( 'r2' )

        self.assertEqual( 1, r2.address )

        exportUnderTest = RegisterBase( r2, MockField )

        self.assertEqual( 0, exportUnderTest.precedingGapBytes )


    def testNonZeroGap( self ) :
        r2 = self.module1.addRegister( 'r2' )
        r2[ 'constraints' ][ 'fixedAddress' ] = 0x10

        self.assertEqual( 0x10, r2.address )

        exportUnderTest = RegisterBase( r2, MockField )

        self.assertEqual( (0x10 - 1), exportUnderTest.precedingGapBytes )


    def testNonZeroGap16BitMemoryUnit( self ) :
        self.module1.memory.memoryUnitBits = 16

        r2 = self.module1.addRegister( 'r2' )
        r2[ 'constraints' ][ 'fixedAddress' ] = 0x10

        self.assertEqual( 0x10, r2.address )

        exportUnderTest = RegisterBase( r2, MockField )

        self.assertEqual( ((0x10 - 1) * 2), exportUnderTest.precedingGapBytes )


if __name__ == '__main__' :
    unittest.main()
