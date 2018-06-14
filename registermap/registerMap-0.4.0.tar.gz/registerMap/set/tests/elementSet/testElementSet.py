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

import registerMap.set.elementSet as rmese


class MockElement( object ) :
    def __init__( self,
                  name = 'testElement' ) :
        self.__data = dict()

        self.__data[ 'name' ] = name


    def __getitem__( self, item ) :
        return self.__data[ item ]


class TestConstructElementSet( unittest.TestCase ) :
    def testDefaultConstructor( self ) :
        s = rmese.ElementSet()

        self.assertEqual( len( s ), 0 )


class ElementSetTestBase( object ) :
    def getTestType( self ) :
        """
        Children may override this method to deliver their class under test for testing.

        :return: Type to be used for testing.
        """
        return rmese.ElementSet


    def generateElement( self,
                         name = None ) :
        """
        Children may override this method to deliver a set element for test.

        :param name:
        :return:
        """
        if name is None :
            return MockElement()
        else :
            return MockElement( name = name )


class TestElementSetAdd( unittest.TestCase,
                         ElementSetTestBase ) :
    def setUp( self ) :
        self.testSet = self.getTestType()()


    def testAddElement( self ) :
        self.assertEqual( len( self.testSet ), 0 )

        self.testSet.add( self.generateElement() )

        self.assertEqual( len( self.testSet ), 1 )


class TestElementSetDiscard( unittest.TestCase,
                             ElementSetTestBase ) :
    def setUp( self ) :
        self.element = self.generateElement()

        self.testSet = self.getTestType()()

        self.testSet.add( self.element )


    def testDiscardElement( self ) :
        self.assertEqual( len( self.testSet ), 1 )

        self.testSet.discard( self.element )

        self.assertEqual( len( self.testSet ), 0 )


    def testDiscardAbsentElement( self ) :
        self.assertEqual( len( self.testSet ), 1 )

        self.testSet.discard( self.generateElement() )

        # The element in the set is not the same element being discarded, so the set doesn't change.
        self.assertEqual( len( self.testSet ), 1 )


class TestElementSetRemove( unittest.TestCase,
                            ElementSetTestBase ) :
    def setUp( self ) :
        self.element = self.generateElement()

        self.testSet = self.getTestType()()

        self.testSet.add( self.element )


    def testRemoveElement( self ) :
        self.assertEqual( len( self.testSet ), 1 )

        self.testSet.remove( self.element )

        self.assertEqual( len( self.testSet ), 0 )


    def testRemoveAbsentElementRaises( self ) :
        self.assertEqual( len( self.testSet ), 1 )

        with self.assertRaises( KeyError ) :
            self.testSet.remove( self.generateElement() )


class TestElementSetOrder( unittest.TestCase,
                           ElementSetTestBase ) :
    def setUp( self ) :
        self.testSet = self.getTestType()()


    def testSetOrder( self ) :
        numberElements = 5
        expectedOrderedNames = [ ]
        # Add the elements in order
        for x in range( 0, numberElements ) :
            expectedOrderedNames.append( repr( x ) )
            self.testSet.add( self.generateElement( name = expectedOrderedNames[ x ] ) )

        elements = list( self.testSet )

        actualOrderedNames = [ x[ 'name' ] for x in elements ]

        self.assertEqual( actualOrderedNames, expectedOrderedNames )


class TestElementSetSingleElement( unittest.TestCase,
                                   ElementSetTestBase ) :
    def setUp( self ) :
        self.testSet = self.getTestType()()

        numberElements = 1

        for thisIndex in range( 0, numberElements ) :
            thisName = '{0}'.format( thisIndex )

            self.testSet.add( self.generateElement( name = thisName ) )


    def testFindSingleItem( self ) :
        self.assertEqual( len( self.testSet ), 1 )
        x = list( self.testSet )

        self.assertEqual( x[ 0 ][ 'name' ], '0' )

        # Look for the only item known to be in the set.
        actualItemsFound = self.testSet.find( '0' )

        self.assertEqual( len( actualItemsFound ), 1 )

        y = list( actualItemsFound )
        self.assertEqual( y[ 0 ][ 'name' ], '0' )


    def testItemsFoundEmptyWhenElementNotInSet( self ) :
        self.assertEqual( len( self.testSet ), 1 )
        x = list( self.testSet )

        self.assertEqual( x[ 0 ][ 'name' ], '0' )

        # Look for an item known to not be in the set.
        actualItemsFound = self.testSet.find( 'a' )

        # Items found is empty.
        self.assertEqual( len( actualItemsFound ), 0 )


class TestElementSetMultipleElements( unittest.TestCase,
                                      ElementSetTestBase ) :
    def setUp( self ) :
        self.testSet = self.getTestType()()

        for i in range( 0, 4 ) :
            self.testSet.add( self.generateElement( name = repr( i ) ) )

        self.numberRepeatedElements = 3
        for i in range( 0, self.numberRepeatedElements ) :
            self.testSet.add( self.generateElement( name = 'a' ) )


    def testFindMultipleItems( self ) :
        # Look for the items known to be in the set.
        actualItemsFound = self.testSet.find( 'a' )

        self.assertEqual( len( actualItemsFound ), self.numberRepeatedElements )


if __name__ == '__main__' :
    unittest.main()
