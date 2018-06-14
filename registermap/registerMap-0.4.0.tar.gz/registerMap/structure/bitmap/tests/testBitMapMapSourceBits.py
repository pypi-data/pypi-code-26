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


class TestAssignOverlappingSourceIntervals( unittest.TestCase ) :
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


    def testOverlappedSourceIntervalRaises( self ) :
        fieldRanges = [ BitRange( (0, 1) ),
                        BitRange( (2, 3) ),
                        ]
        registerBitOffset = 4
        registerRanges = [ BitRange( (registerBitOffset,
                                      (registerBitOffset + self.destinationSize - 1 - 2)) ),
                           BitRange( ((registerBitOffset + self.destinationSize - 1 - 2),
                                      (registerBitOffset + self.destinationSize - 1)) ),
                           ]

        self.sourceBitMap.mapBits( registerRanges[ 0 ], fieldRanges[ 0 ], self.mock_destination )

        self.assertEqual( len( self.sourceBitMap.intervalMap ), 1 )

        with self.assertRaisesRegex( ConfigurationError,
                                     '^Specifed source interval overlaps existing source intervals' ) :
            self.sourceBitMap.mapBits( registerRanges[ 1 ], fieldRanges[ 1 ], self.mock_destination )


    def testIdenticalSourceIntervalWritesNewMapping( self ) :
        # Equal source interval writes the new mapping.
        fieldRanges = [ BitRange( (0, 1) ),
                        BitRange( (2, 3) ),
                        ]
        registerBitOffset = 4
        registerRange = BitRange( (registerBitOffset,
                                   (registerBitOffset + self.destinationSize - 1 - 2)) )

        self.sourceBitMap.mapBits( registerRange, fieldRanges[ 0 ], self.mock_destination )

        self.assertEqual( len( self.sourceBitMap.intervalMap ), 1 )

        self.sourceBitMap.mapBits( registerRange, fieldRanges[ 1 ], self.mock_destination )

        self.assertEqual( len( self.sourceBitMap.intervalMap ), 1 )
        actualIntervals = self.sourceBitMap.intervalMap

        self.assertTrue( len( actualIntervals ), 1 )
        actualSourceRange, destinationData = actualIntervals.popitem()

        self.assertEqual( actualSourceRange, registerRange )

        self.checkDestinationData( destinationData, self.mock_destination, fieldRanges[ 1 ] )


    def checkDestinationData( self, actualData, expectedObject, expectedInterval ) :
        self.assertEqual( actualData[ 'destination' ], expectedObject )
        self.assertEqual( actualData[ 'interval' ], expectedInterval )


    def testAddingDifferentIntervalsIncreasesSize( self ) :
        fieldRanges = [ BitRange( (0, 1) ),
                        BitRange( (2, 3) ),
                        ]
        registerBitOffset = 4
        registerRanges = [ BitRange( (registerBitOffset,
                                      (registerBitOffset + self.destinationSize - 1 - 2)) ),
                           BitRange( ((registerBitOffset + self.destinationSize - 1 - 1),
                                      (registerBitOffset + self.destinationSize - 1)) ),
                           ]

        self.sourceBitMap.mapBits( registerRanges[ 0 ], fieldRanges[ 0 ], self.mock_destination )
        self.assertEqual( len( self.sourceBitMap.intervalMap ), 1 )

        self.sourceBitMap.mapBits( registerRanges[ 1 ], fieldRanges[ 1 ], self.mock_destination )

        actualIntervals = self.sourceBitMap.intervalMap
        self.assertTrue( len( actualIntervals ), 2 )

        destinationData = actualIntervals[ registerRanges[ 0 ] ]
        self.checkDestinationData( destinationData, self.mock_destination, fieldRanges[ 0 ] )

        destinationData = actualIntervals[ registerRanges[ 1 ] ]
        self.checkDestinationData( destinationData, self.mock_destination, fieldRanges[ 1 ] )


if __name__ == '__main__' :
    unittest.main()
