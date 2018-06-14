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

from registerMap.elements.field import Field
from registerMap.elements.register import RegisterInstance
from registerMap.set.fieldSet import FieldSet

from registerMap.structure.memory.space import MemorySpace

from registerMap.set.tests.elementSet import testElementSet as rmstes


class TestConstructFieldSet( unittest.TestCase ) :
    def testDefaultConstructor( self ) :
        b = FieldSet()

        self.assertEqual( len( b ), 0 )


class TestSetAdd( rmstes.TestElementSetAdd ) :
    def getTestType( self ) :
        return FieldSet


    def generateElement( self,
                         name = None ) :
        f = Field()

        return f


class TestSetDiscard( rmstes.TestElementSetDiscard ) :
    def getTestType( self ) :
        return FieldSet


    def generateElement( self,
                         name = None ) :
        f = Field()

        return f


class TestSetSingleElement( rmstes.TestElementSetSingleElement ) :
    def getTestType( self ) :
        return FieldSet


    def generateElement( self,
                         name = None ) :
        f = Field()
        f[ 'name' ] = name

        return f


class TestSetMultipleElements( rmstes.TestElementSetMultipleElements ) :
    memory = MemorySpace()
    registers = list()
    fieldSet = FieldSet()


    def getTestType( self ) :
        return FieldSet


    def generateElement( self,
                         name = None ) :
        self.registers.append( RegisterInstance( self.memory,
                                                 setCollection = self.fieldSet ) )
        f = Field( parent = self.registers[ -1 ] )
        f[ 'name' ] = name

        return f


if __name__ == '__main__' :
    unittest.main()
