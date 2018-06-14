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
from registerMap.set.fieldSet import \
    ConfigurationError, \
    FieldSet

from registerMap.structure.memory.space import MemorySpace


class TestAddField( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()

        self.setUnderTest = FieldSet()

        self.register = RegisterInstance( self.memory,
                                          setCollection = self.setUnderTest )


    def testAddSingleFieldOkay( self ) :
        """
        When: a first bit field with the default name is added Then: the size of the bit field set is 1
        """
        b = Field( parent = self.register )

        self.assertEqual( len( self.setUnderTest ), 0 )

        self.setUnderTest.add( b )

        self.assertEqual( len( self.setUnderTest ), 1 )


    def testAddNonGlobalFieldsOkay( self ) :
        """
        When: a second bit field is added And: the new bit field has the same name as the first bit field And: the new bit field is defined as non-global And: the first bit field is defined as non-global Then: the size of the bit field set is 2
        """
        b1 = Field( parent = self.register )
        b2 = Field( parent = self.register )

        self.assertEqual( len( self.setUnderTest ), 0 )

        self.setUnderTest.add( b1 )
        self.setUnderTest.add( b2 )

        self.assertEqual( len( self.setUnderTest ), 2 )


    def testAddGlobalFieldsRaises( self ) :
        """
        When: a second bit field is added And: the new bit field has the same name as the first bit field And: the new bit field is defined as global And: the first bit field is defined as global Then: an exception is raised
        """
        b1 = Field()

        b2 = Field()

        self.assertEqual( len( self.setUnderTest ), 0 )

        self.setUnderTest.add( b1 )

        with self.assertRaisesRegex( ConfigurationError, '^Only one global field of a name can exist' ) :
            self.setUnderTest.add( b2 )


    def testAddGlobalFieldNonGlobalBitFieldOkay( self ) :
        """
        When: a second bit field is added And: the new bit field has the same name as the first bit field And: the new bit field is defined as global And: the first bit field is defined as non-global Then: the size of the bit field set is 2
        """
        b1 = Field( parent = self.register )
        self.assertFalse( b1[ 'global' ] )

        b2 = Field()
        self.assertTrue( b2[ 'global' ] )

        self.assertEqual( len( self.setUnderTest ), 0 )

        self.setUnderTest.add( b1 )
        self.setUnderTest.add( b2 )

        self.assertEqual( len( self.setUnderTest ), 2 )


    def testAddNonGlobalFieldGlobalBitFieldOkay( self ) :
        """
        When: a second bit field is added And: the new bit field has the same name as the first bit field And: the new bit field is defined as non-global And: the first bit field is defined as global Then: the size of the bit field set is 2
        """
        b1 = Field()

        b2 = Field( parent = self.register )

        self.assertEqual( len( self.setUnderTest ), 0 )

        self.setUnderTest.add( b1 )
        self.setUnderTest.add( b2 )

        self.assertEqual( len( self.setUnderTest ), 2 )


class TestFieldSetMultipleElements( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()

        self.setUnderTest = FieldSet()

        self.numberUniqueElements = 4
        for i in range( 0, self.numberUniqueElements ) :
            f = Field()
            f[ 'name' ] = repr( i )

            self.setUnderTest.add( f )

        self.numberRepeatedElements = 3
        self.registers = list()
        for i in range( 0, self.numberRepeatedElements ) :
            self.registers.append( RegisterInstance( self.memory,
                                                     setCollection = self.setUnderTest ) )
            f = Field( parent = self.registers[ i ] )
            f[ 'name' ] = 'a'

            self.setUnderTest.add( f )


    def testFindMultipleItems( self ) :
        # Look for the items known to be in the set.
        actualItemsFound = self.setUnderTest.find( 'a' )

        self.assertEqual( len( self.setUnderTest ), (self.numberRepeatedElements + self.numberUniqueElements) )
        self.assertEqual( len( actualItemsFound ), self.numberRepeatedElements )


if __name__ == '__main__' :
    unittest.main()
