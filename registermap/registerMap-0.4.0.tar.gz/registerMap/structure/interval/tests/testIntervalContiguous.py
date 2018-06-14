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

from ..contiguous import makeContiguous
from ..element import ClosedIntegerInterval


class TestMakeContiguous( unittest.TestCase ) :

    def testContiguousIntervalsUnchanged( self ) :
        inputValue = {
            ClosedIntegerInterval( (3, 4) ),
            ClosedIntegerInterval( (0, 2) ),
            ClosedIntegerInterval( (5, 7) ),
        }

        expectedValues = [
            ClosedIntegerInterval( (0, 2) ).value,
            ClosedIntegerInterval( (3, 4) ).value,
            ClosedIntegerInterval( (5, 7) ).value,
        ]

        contiguousIntervals = makeContiguous( inputValue, 7 )

        actualValues = [ x.value for x in contiguousIntervals ]

        self.assertEqual( expectedValues, actualValues )


    def testNoncontiguousIntervalsAdded( self ) :
        inputValue = {
            ClosedIntegerInterval( (3, 4) ),
            ClosedIntegerInterval( (0, 1) ),
            ClosedIntegerInterval( (7, 7) ),
        }

        expectedValues = [
            ClosedIntegerInterval( (0, 1) ).value,
            ClosedIntegerInterval( (2, 2) ).value,
            ClosedIntegerInterval( (3, 4) ).value,
            ClosedIntegerInterval( (5, 6) ).value,
            ClosedIntegerInterval( (7, 7) ).value,
        ]

        contiguousIntervals = makeContiguous( inputValue, 7 )

        actualValues = [ x.value for x in contiguousIntervals ]

        self.assertEqual( expectedValues, actualValues )


    def testLastNoncontiguousIntervalAdded( self ) :
        inputValue = {
            ClosedIntegerInterval( (3, 4) ),
            ClosedIntegerInterval( (0, 1) ),
            ClosedIntegerInterval( (7, 7) ),
        }

        expectedValues = [
            ClosedIntegerInterval( (0, 1) ).value,
            ClosedIntegerInterval( (2, 2) ).value,
            ClosedIntegerInterval( (3, 4) ).value,
            ClosedIntegerInterval( (5, 6) ).value,
            ClosedIntegerInterval( (7, 7) ).value,
            ClosedIntegerInterval( (8, 10) ).value,
        ]

        contiguousIntervals = makeContiguous( inputValue, 10 )

        actualValues = [ x.value for x in contiguousIntervals ]

        self.assertEqual( expectedValues, actualValues )


if __name__ == '__main__' :
    unittest.main()
