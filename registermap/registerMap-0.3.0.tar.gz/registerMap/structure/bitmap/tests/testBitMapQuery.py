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

import unittest.mock

from ..bitmap import \
    BitMap, \
    BitRange

from .mocks import MockBitStore


class TestQueryRanges( unittest.TestCase ) :
    def setUp( self ) :
        self.sourceSize = 16
        self.sourceId = 'testSource'
        self.mock_source = MockBitStore( self.sourceId, self.sourceSize )
        self.sourceBitMap = BitMap( self.mock_source )
        self.mock_source.bitMap = self.sourceBitMap

        self.destinationSize = 4
        self.destinationId = 'testDestination'
        self.mock_destination = MockBitStore( self.destinationId, self.destinationSize )
        self.destinationBitMap = BitMap( self.mock_destination )
        self.mock_destination.bitMap = self.destinationBitMap


    def testAssignedSourceRangePersists( self ) :
        # The assigned source range can be queried.

        fieldRange = BitRange( (0,
                                (self.destinationSize - 1)) )
        registerBitOffset = 4
        registerRange = BitRange( (registerBitOffset,
                                   (registerBitOffset + self.destinationSize - 1)) )

        self.sourceBitMap.mapBits( registerRange, fieldRange, self.mock_destination )

        actualIntervals = self.sourceBitMap.sourceIntervals

        self.assertTrue( len( actualIntervals ), 1 )
        actualValue = actualIntervals.pop()

        self.assertEqual( actualValue, registerRange )


    def testAssignedDestinationRangePersists( self ) :
        # The assigned destination range can be queried.

        fieldRange = BitRange( (0,
                                (self.destinationSize - 1)) )
        registerBitOffset = 4
        registerRange = BitRange( (registerBitOffset,
                                   (registerBitOffset + self.destinationSize - 1)) )

        self.sourceBitMap.mapBits( registerRange, fieldRange, self.mock_destination )

        actualIntervals = self.sourceBitMap.destinationIntervals

        self.assertTrue( len( actualIntervals ), 1 )
        (sourceInterval, actualValue) = actualIntervals.popitem()

        self.assertEqual( actualValue, fieldRange )
        self.assertEqual( sourceInterval, registerRange )


    def testAssignedRangesPersists( self ) :
        # The assigned destination range can be queried.

        fieldRange = BitRange( (0,
                                (self.destinationSize - 1)) )
        registerBitOffset = 4
        registerRange = BitRange( (registerBitOffset,
                                   (registerBitOffset + self.destinationSize - 1)) )

        self.sourceBitMap.mapBits( registerRange, fieldRange, self.mock_destination )

        actualIntervals = self.sourceBitMap.intervalMap

        self.assertTrue( len( actualIntervals ), 1 )
        (sourceRange, destinationValue) = actualIntervals.popitem()

        self.assertEqual( destinationValue[ 'destination' ], self.mock_destination )
        self.assertEqual( sourceRange, registerRange )
        self.assertEqual( destinationValue[ 'interval' ], fieldRange )


if __name__ == '__main__' :
    unittest.main()
