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
    BitRange, \
    ConfigurationError

from .mocks import MockBitStore


class TestBitMapAssignRanges( unittest.TestCase ) :
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


    def testMapBitRange( self ) :
        # Mapping two intervals of equal size generates no errors
        fieldRange = BitRange( (0,
                                (self.destinationSize - 1)) )
        registerBitOffset = 4
        registerRange = BitRange( (registerBitOffset,
                                   (registerBitOffset + self.destinationSize - 1)) )

        self.sourceBitMap.mapBits( registerRange, fieldRange, self.mock_destination )


    def testAssignBadSourceBitsTypeRaises( self ) :
        # Specifying "not BitRange" for the source range raises.
        with self.assertRaisesRegex( RuntimeError, '^Incorrect bits type for source' ) :
            self.sourceBitMap.mapBits( 5, BitRange( (4, 6) ), self.mock_destination )


    def testSourceBitsExceedsSourceSizeRaises( self ) :
        # Specifying register/source range that exceed the source size raises.
        fieldRange = BitRange( (0, 5) )
        registerRange = BitRange( (0, (self.sourceSize + 1)) )
        with self.assertRaisesRegex( RuntimeError, '^Range source cannot exceed size' ) :
            self.sourceBitMap.mapBits( registerRange, fieldRange, self.mock_destination )


    def testDestinationBitsExceedsDestinationSizeRaises( self ) :
        # Specifying field/destination range that exceeds the destination size raises.
        destinationRange = BitRange( (0, (self.destinationSize + 1)) )
        sourceRange = BitRange( (0, 5) )
        with self.assertRaisesRegex( RuntimeError, '^Range destination cannot exceed size' ) :
            self.sourceBitMap.mapBits( sourceRange, destinationRange, self.mock_destination )


    def testAssignBadDestinationBitsTypeRaises( self ) :
        # Specifying "not BitRange" type for destination range raises.
        with self.assertRaisesRegex( RuntimeError, '^Incorrect bits type for destination' ) :
            self.sourceBitMap.mapBits( BitRange( (4, 6) ), 8, self.mock_destination )


    def testAssignMismatchedSizes( self ) :
        # Specifying source and destination ranges that don't have the same size raises.
        destinationRange = BitRange( (0, (self.destinationSize - 1)) )
        sourceRange = BitRange( (4, 10) )

        with self.assertRaisesRegex( ConfigurationError, '^Mismatched bit range sizes' ) :
            self.sourceBitMap.mapBits( sourceRange, destinationRange, self.mock_destination )


if __name__ == '__main__' :
    unittest.main()
