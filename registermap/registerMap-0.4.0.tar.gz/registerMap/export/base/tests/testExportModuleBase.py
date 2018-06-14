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

from .mocks import \
    MockField, \
    MockModule, \
    MockRegister


class TestExportModuleBase( unittest.TestCase ) :
    def setUp( self ) :
        self.registerMap = RegisterMap()
        self.module1 = self.registerMap.addModule( 'm1' )

        self.exportUnderTest = MockModule( self.module1, MockRegister, MockField )


    def testName( self ) :
        self.assertEqual( self.module1[ 'name' ], self.exportUnderTest.name )


    def testEmptyModule( self ) :
        self.assertEqual( 0, len( self.exportUnderTest.registers ) )


    def testHexAddress( self ) :
        self.assertEqual( self.exportUnderTest.expectedAddress, self.exportUnderTest.address )


    def testOffset( self ) :
        self.assertEqual( self.exportUnderTest.expectedOffset, self.exportUnderTest.offset )


    def testRegisters( self ) :
        self.register1 = self.module1.addRegister( 'r1' )
        self.register1.addField( 'f1', (0, 2) )
        self.register1.addField( 'f2', (3, 4) )
        self.register1.addField( 'f3', (5, 7) )

        self.register2 = self.module1.addRegister( 'r2' )
        self.register2.addField( 'f1', (0, 2) )
        self.register2.addField( 'f2', (3, 4) )
        self.register2.addField( 'f3', (5, 7) )

        for expectedRegisterName, thisRegister in zip( [ 'r1', 'r2' ], self.exportUnderTest.registers ) :
            self.assertEqual( expectedRegisterName, thisRegister.name )

            for expectedFieldName, thisField in zip( [ 'f1', 'f2', 'f3' ], thisRegister.fields ) :
                self.assertEqual( expectedFieldName, thisField.name )


if __name__ == '__main__' :
    unittest.main()
