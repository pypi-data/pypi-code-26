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

import unittest

from ..registerMap import RegisterMap


class TestRegisterMapLen( unittest.TestCase ) :
    def setUp( self ) :
        self.mapUnderTest = RegisterMap()

        self.assertEqual( len( self.mapUnderTest ), 0 )


    def testModuleLen1( self ) :
        self.mapUnderTest.addModule( 'myModule' )

        self.assertEqual( len( self.mapUnderTest ), 1 )


    def testRegisterLen2( self ) :
        myModule = self.mapUnderTest.addModule( 'myModule' )

        myModule.addRegister( 'myRegister' )

        self.assertEqual( len( self.mapUnderTest ), 2 )


    def testFieldLen3( self ) :
        myModule = self.mapUnderTest.addModule( 'myModule' )

        myRegister = myModule.addRegister( 'myRegister' )

        myRegister.addField( 'myField', [ 0, 3 ] )

        self.assertEqual( len( self.mapUnderTest ), 3 )


    def testSecondLocalFieldLen4( self ) :
        myModule = self.mapUnderTest.addModule( 'myModule' )

        myRegister = myModule.addRegister( 'myRegister' )

        myRegister.addField( 'myField', [ 0, 3 ] )
        myRegister.addField( 'myOtherField', [ 0, 3 ] )

        self.assertEqual( len( self.mapUnderTest ), 4 )


    def testGlobalFieldLen3( self ) :
        myModule = self.mapUnderTest.addModule( 'myModule' )

        myRegister = myModule.addRegister( 'myRegister' )

        myRegister.addField( 'myField', [ 0, 3 ], (0, 3),
                             isGlobal = True )
        myRegister.addField( 'myField', [ 4, 6 ], (4, 6),
                             isGlobal = True )

        self.assertEqual( len( self.mapUnderTest ), 3 )


if __name__ == '__main__' :
    unittest.main()
