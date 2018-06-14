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

from registerMap.elements.register import RegisterInstance
from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace

from ..field import ConfigurationError


class TestConvertToGlobal( unittest.TestCase ) :

    def setUp( self ) :
        self.setCollection = SetCollection()
        self.memory = MemorySpace()
        self.register = RegisterInstance( self.memory,
                                          setCollection = self.setCollection )

        self.testField = self.register.addField( 'fieldName', [ 0, 4 ], (0, 4) )

        self.assertFalse( self.testField[ 'global' ] )


    def testConvertLocalToGlobal( self ) :
        self.testField.convertToGlobal()

        self.assertTrue( self.testField[ 'global' ] )


class TestConvertToLocal( unittest.TestCase ) :

    def setUp( self ) :
        self.setCollection = SetCollection()
        self.memory = MemorySpace()
        self.register = RegisterInstance( self.memory,
                                          setCollection = self.setCollection )

        self.testField = self.register.addField( 'fieldName', [ 0, 4 ], (0, 4),
                                                 isGlobal = True )

        self.assertTrue( self.testField[ 'global' ] )


    def testConvertGlobalToLocalSingleRegister( self ) :
        self.testField.convertToLocal( self.register )

        self.assertFalse( self.testField[ 'global' ] )


    def testMultipleRegistersRaises( self ) :
        register2 = RegisterInstance( self.memory,
                                      setCollection = self.setCollection )

        register2.addField( 'fieldName', [ 0, 2 ], (5, 7),
                            isGlobal = True )

        with self.assertRaisesRegex( ConfigurationError, '^Field maps to multiple registers' ) :
            self.testField.convertToLocal( self.register )


    def testAbsentRegister( self ) :
        register2 = RegisterInstance( self.memory,
                                      setCollection = self.setCollection )

        newField = register2.addField( 'otherField', [ 0, 2 ], (5, 7),
                                       isGlobal = True )

        with self.assertRaisesRegex( ConfigurationError, '^Field does not map to the register selected for parent' ) :
            newField.convertToLocal( self.register )


    def testForceSingleParent( self ) :
        register2 = RegisterInstance( self.memory,
                                      setCollection = self.setCollection )

        register2.addField( 'fieldName', [ 0, 2 ], (5, 7),
                            isGlobal = True )

        self.testField.convertToLocal( self.register,
                                       removeOthers = True )

        self.assertFalse( self.testField[ 'global' ] )
        self.assertNotIn( register2, self.testField.bitMap.destinations )


if __name__ == '__main__' :
    unittest.main()
