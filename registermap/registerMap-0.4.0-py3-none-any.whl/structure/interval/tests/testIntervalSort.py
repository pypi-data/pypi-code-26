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

from ..element import ClosedIntegerInterval
from ..sort import sortIntervals


class TestIntervalSort( unittest.TestCase ) :

    def testSortIntervalList( self ) :
        inputValue = [
            ClosedIntegerInterval( (3, 4) ),
            ClosedIntegerInterval( (0, 2) ),
            ClosedIntegerInterval( (5, 7) ),
        ]

        actualValue = sortIntervals( inputValue )

        expectedValue = [
            ClosedIntegerInterval( (0, 2) ),
            ClosedIntegerInterval( (3, 4) ),
            ClosedIntegerInterval( (5, 7) ),
        ]

        self.assertEqual( expectedValue, actualValue )


    def testSortContiguousIntervalSet( self ) :
        inputValue = {
            ClosedIntegerInterval( (3, 4) ),
            ClosedIntegerInterval( (0, 2) ),
            ClosedIntegerInterval( (5, 7) ),
        }

        actualValue = sortIntervals( inputValue )

        expectedValue = [
            ClosedIntegerInterval( (0, 2) ),
            ClosedIntegerInterval( (3, 4) ),
            ClosedIntegerInterval( (5, 7) ),
        ]

        self.assertEqual( expectedValue, actualValue )


    def testSortNoncontiguousIntervalSet( self ) :
        inputValue = {
            ClosedIntegerInterval( (4, 4) ),
            ClosedIntegerInterval( (0, 1) ),
            ClosedIntegerInterval( (6, 7) ),
        }

        actualValue = sortIntervals( inputValue )

        expectedValue = [
            ClosedIntegerInterval( (0, 1) ),
            ClosedIntegerInterval( (4, 4) ),
            ClosedIntegerInterval( (6, 7) ),
        ]

        self.assertEqual( expectedValue, actualValue )


    def testOverlappingIntervalAsserts( self ) :
        inputValue = {
            ClosedIntegerInterval( (3, 5) ),
            ClosedIntegerInterval( (0, 2) ),
            ClosedIntegerInterval( (5, 7) ),
        }

        with self.assertRaises( AssertionError ) :
            sortIntervals( inputValue )


if __name__ == '__main__' :
    unittest.main()
