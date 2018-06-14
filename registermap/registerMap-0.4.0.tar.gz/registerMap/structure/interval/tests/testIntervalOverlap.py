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

from ..element import ClosedIntegerInterval

from ..overlap import \
    anyOverlap, \
    isEncapsulated, \
    isOverlap


class TestIntervalOverlap( unittest.TestCase ) :
    def testUpperOverlap1( self ) :
        # The first interval overlaps the upper edge of the second interval.
        i1 = ClosedIntegerInterval( (4, 8) )
        i2 = ClosedIntegerInterval( (2, 4) )

        self.assertTrue( isOverlap( i1, i2 ) )


    def testUpperOverlap2( self ) :
        # The second interval overlaps the upper edge of the first interval.
        i1 = ClosedIntegerInterval( (2, 4) )
        i2 = ClosedIntegerInterval( (4, 8) )

        self.assertTrue( isOverlap( i1, i2 ) )


    def testLowerOverlap1( self ) :
        # The first interval overlaps the lower edge of the second interval.
        i1 = ClosedIntegerInterval( (2, 3) )
        i2 = ClosedIntegerInterval( (3, 6) )

        self.assertTrue( isOverlap( i1, i2 ) )


    def testLowerOverlap2( self ) :
        # The second interval overlaps the lower edge of the first interval.
        i1 = ClosedIntegerInterval( (3, 6) )
        i2 = ClosedIntegerInterval( (2, 3) )

        self.assertTrue( isOverlap( i1, i2 ) )


    def testNoOverlap( self ) :
        # The intervals do not overlap.
        i1 = ClosedIntegerInterval( (2, 3) )
        i2 = ClosedIntegerInterval( (4, 7) )

        self.assertFalse( isOverlap( i1, i2 ) )


    def testInsideOverlap1( self ) :
        # The second interval is entirely inside the first interval.
        i1 = ClosedIntegerInterval( (3, 9) )
        i2 = ClosedIntegerInterval( (4, 6) )

        self.assertTrue( isOverlap( i1, i2 ) )


    def testInsideOverlap2( self ) :
        # The first interval is entirely inside the second interval.
        i1 = ClosedIntegerInterval( (4, 6) )
        i2 = ClosedIntegerInterval( (3, 9) )

        self.assertTrue( isOverlap( i1, i2 ) )


    def testEqualOverlap( self ) :
        # The first interval is equal to the second interval.
        i1 = ClosedIntegerInterval( (4, 6) )
        i2 = ClosedIntegerInterval( (4, 6) )

        self.assertTrue( isOverlap( i1, i2 ) )


class TestIsEncapsulated( unittest.TestCase ) :
    def testIsEncapsulated( self ) :
        # The first interval is entirely inside the second interval.
        i1 = ClosedIntegerInterval( (4, 6) )
        i2 = ClosedIntegerInterval( (2, 9) )

        self.assertTrue( isEncapsulated( i1, i2 ) )


    def testIsNotEncapsulated( self ) :
        # The second interval is entirely inside the first interval.
        i1 = ClosedIntegerInterval( (2, 9) )
        i2 = ClosedIntegerInterval( (4, 6) )

        self.assertFalse( isEncapsulated( i1, i2 ) )


    def testEqualOverlap( self ) :
        # The first interval is equal to the second interval.
        i1 = ClosedIntegerInterval( (4, 6) )
        i2 = ClosedIntegerInterval( (4, 6) )

        self.assertTrue( isEncapsulated( i1, i2 ) )


class TestAnyOverlap( unittest.TestCase ) :

    def testOverlapTrue( self ) :
        inputValue = [ ClosedIntegerInterval( (4, 6) ), ClosedIntegerInterval( (6, 8) ) ]

        self.assertTrue( anyOverlap( inputValue ) )


    def testOverlapTrue( self ) :
        inputValue = [ ClosedIntegerInterval( (4, 6) ), ClosedIntegerInterval( (7, 8) ) ]

        self.assertFalse( anyOverlap( inputValue ) )


if __name__ == '__main__' :
    unittest.main()
