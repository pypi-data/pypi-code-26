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

from registerMap.elements.tests.mockObserver import MockObserver

from ..field import Field


class TestFieldSizeParameter( unittest.TestCase ) :
    def setUp( self ) :
        self.fieldUnderTest = Field()


    def testDefaultSize( self ) :
        expectedSize = 0

        actualSize = self.fieldUnderTest[ 'size' ]

        self.assertEqual( actualSize, expectedSize )


    def testAssignSize( self ) :
        expectedSize = 15

        self.assertNotEqual( self.fieldUnderTest, expectedSize )

        self.fieldUnderTest[ 'size' ] = expectedSize
        actualSize = self.fieldUnderTest[ 'size' ]

        self.assertEqual( actualSize, expectedSize )


class TestFieldSizeParameterNotification( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver()
        self.fieldUnderTest = Field()

        self.fieldUnderTest.sizeChangeNotifier.addObserver( self.observer )


    def testSizeChangeNotification( self ) :
        expectedSize = 15

        self.assertNotEqual( self.fieldUnderTest, expectedSize )

        self.fieldUnderTest[ 'size' ] = expectedSize
        actualSize = self.fieldUnderTest[ 'size' ]

        self.assertEqual( actualSize, expectedSize )
        self.assertEqual( self.observer.updateCount, 1 )


class TestFieldSizeBitsMethod( unittest.TestCase ) :
    def setUp( self ) :
        self.fieldUnderTest = Field()


    def testDefaultSizeBits( self ) :
        expectedSize = 0

        actualSize = self.fieldUnderTest.sizeBits

        self.assertEqual( actualSize, expectedSize )


    def testAssignSize( self ) :
        expectedSize = 15

        self.assertNotEqual( self.fieldUnderTest, expectedSize )

        self.fieldUnderTest[ 'size' ] = expectedSize
        actualSizeBits = self.fieldUnderTest.sizeBits

        self.assertEqual( actualSizeBits, expectedSize )


if __name__ == '__main__' :
    unittest.main()
