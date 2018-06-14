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


class TestRemoveField( unittest.TestCase ) :
    def setUp( self ) :
        self.memory = MemorySpace()

        self.setUnderTest = FieldSet()

        self.register = RegisterInstance( self.memory,
                                          setCollection = self.setUnderTest )


    def testNonexistentFieldRemoveRaises( self ) :
        """
        When: a bit field is removed And: the bit field does not exist in the bit field set Then: an exception is raised
        """
        bf = Field()

        self.assertEqual( len( self.setUnderTest ), 0 )

        with self.assertRaisesRegex( ConfigurationError, '^Field does not exist in set' ) :
            self.setUnderTest.remove( bf )


    def testSingleNonGlobalFieldRemove( self ) :
        """
        When: a bit field is removed And: the bit field exists in the bit field set And: the bit field is defined as non-global Then: the size of the bit field set is reduced by 1
        """


        def checkInitialSet() :
            nonlocal self, expectedName

            self.assertEqual( len( self.setUnderTest ), 1 )

            bitFields = self.setUnderTest.find( expectedName )
            self.assertEqual( len( bitFields ), 1 )

            thisField = bitFields.pop()

            self.assertEqual( thisField[ 'global' ], False )


        expectedName = 'test'
        bf = Field( parent = self.register )
        bf[ 'name' ] = expectedName

        self.setUnderTest.add( bf )

        checkInitialSet()

        self.setUnderTest.remove( bf )

        self.assertEqual( len( self.setUnderTest ), 0 )


    def testSingleGlobalFieldRemove( self ) :
        """
        When: a bit field is removed And: there is a single bit field in the bit field set And: the bit field is defined as non-global Then: the size of the bit field set is reduced by 1
        """


        def checkInitialSet() :
            nonlocal self, expectedName

            self.assertEqual( len( self.setUnderTest ), 1 )

            bitFields = self.setUnderTest.find( expectedName )
            self.assertEqual( len( bitFields ), 1 )

            thisField = bitFields.pop()

            self.assertEqual( thisField[ 'global' ], True )


        expectedName = 'test'
        bf = Field()
        bf[ 'name' ] = expectedName
        self.assertTrue( bf[ 'global' ] )

        self.setUnderTest.add( bf )

        checkInitialSet()

        self.setUnderTest.remove( bf )

        self.assertEqual( len( self.setUnderTest ), 0 )


if __name__ == '__main__' :
    unittest.main()
