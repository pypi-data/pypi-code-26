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
    DestinationIntervalError

from .mocks import MockBitStore


class TestDestinationRangePersists( unittest.TestCase ) :
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

        self.destinationRanges = [ BitRange( (0, 2) ),
                                   ]
        self.sourceBitOffset = 4
        self.sourceRanges = [ BitRange( (self.sourceBitOffset,
                                         (self.sourceBitOffset + 2)) ),
                              ]

        self.assertNotIn( self.mock_source, self.destinationBitMap.destinations )
        self.assertEqual( self.sourceBitMap.source, self.mock_source )
        self.assertEqual( self.sourceBitMap.destinations, set() )

        self.assertNotIn( self.mock_destination, self.sourceBitMap.destinations )
        self.assertEqual( self.destinationBitMap.source, self.mock_destination )
        self.assertEqual( self.destinationBitMap.destinations, set() )

        self.sourceBitMap.mapBits( self.sourceRanges[ 0 ], self.destinationRanges[ 0 ], self.mock_destination )


    def testDestinationAddedToSource( self ) :
        """
        Creating a mapping stores the destination in the source BitMap.
        """

        self.assertIn( self.mock_destination, self.sourceBitMap.destinations )

        actualIntervalMap = self.sourceBitMap.intervalMap
        self.assertEqual( len( actualIntervalMap ), 1 )

        (actualSourceInterval, actualDestination) = actualIntervalMap.popitem()
        self.assertEqual( actualSourceInterval, self.sourceRanges[ 0 ] )
        self.assertEqual( actualDestination[ 'destination' ], self.mock_destination )
        self.assertEqual( actualDestination[ 'interval' ], self.destinationRanges[ 0 ] )


    def testSourceAddedToDestinationAsDestination( self ) :
        """
        Creating a mapping stores the source in the destination BitMap as a destination.
        """
        self.assertIn( self.mock_source, self.destinationBitMap.destinations )

        actualIntervalMap = self.destinationBitMap.intervalMap
        self.assertEqual( len( actualIntervalMap ), 1 )

        (actualSourceInterval, actualDestination) = actualIntervalMap.popitem()
        self.assertEqual( actualSourceInterval, self.destinationRanges[ 0 ] )
        self.assertEqual( actualDestination[ 'destination' ], self.mock_source )
        self.assertEqual( actualDestination[ 'interval' ], self.sourceRanges[ 0 ] )


    def testDestinationAddedToDestinationAsSource( self ) :
        """
        Creating a mapping stores the destination in the destination BitMap as the source of that BitMap.
        """

        self.assertEqual( self.destinationBitMap.source, self.mock_destination )


class TestAssignOverlappingDestinationIntervals( unittest.TestCase ) :
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


    def testOverlappedDestinationIntervalRaises( self ) :
        destinationRanges = [ BitRange( (0, 2) ),
                              BitRange( (2, 3) ),
                              ]
        sourceBitOffset = 4
        sourceRanges = [ BitRange( (sourceBitOffset,
                                    (sourceBitOffset + 2)) ),
                         BitRange( ((sourceBitOffset + 3),
                                    (sourceBitOffset + 4)) ),
                         ]

        self.sourceBitMap.mapBits( sourceRanges[ 0 ], destinationRanges[ 0 ], self.mock_destination )

        self.assertEqual( len( self.sourceBitMap.intervalMap ), 1 )

        with self.assertRaisesRegex( DestinationIntervalError,
                                     '^Specifed destination interval overlaps existing destination intervals' ) :
            self.sourceBitMap.mapBits( sourceRanges[ 1 ], destinationRanges[ 1 ], self.mock_destination )


if __name__ == '__main__' :
    unittest.main()
