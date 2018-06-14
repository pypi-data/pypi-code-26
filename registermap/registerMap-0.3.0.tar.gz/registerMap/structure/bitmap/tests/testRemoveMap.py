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

from registerMap.elements.field import Field
from registerMap.elements.register import RegisterInstance
from registerMap.structure.bitrange import BitRange

from ..bitmap import \
    BitMap, \
    ConfigurationError


class TestBitMapRemoveMap( unittest.TestCase ) :
    def setUp( self ) :
        self.mockRegister = unittest.mock.create_autospec( RegisterInstance )
        self.mockField = unittest.mock.create_autospec( Field )

        self.mapUnderTest = BitMap( self.mockRegister )


    def testNeitherDestinationNorIntervalAsserts( self ) :
        with self.assertRaises( AssertionError ) :
            self.mapUnderTest.removeDestination()


    def testRemoveDestination( self ) :
        def checkRemovedFromSourceMapping() :
            nonlocal self

            destinationMappings = self.mapUnderTest.intervalMap.values()
            for k in destinationMappings :
                self.assertNotEqual( k[ 'destination' ], self.mockField )


        # Removing an entire destination object also removes the corresponding source intervals.
        with unittest.mock.patch.object( self.mapUnderTest, '_BitMap__validateBitRange' ) as br :
            with unittest.mock.patch.object( self.mapUnderTest, '_BitMap__validateSourceOverlaps' ) as so :
                self.mapUnderTest.mapBits( BitRange( [ 0, 4 ] ), BitRange( [ 0, 4 ] ), self.mockField )

                self.assertIn( self.mockField, self.mapUnderTest.destinations )

                self.mapUnderTest.removeDestination( self.mockField )

                self.assertNotIn( self.mockField, self.mapUnderTest.destinations )
                checkRemovedFromSourceMapping()

                # Check that the Field (destination) has been reciprocally called for source removal.
                self.assertEqual( self.mockField.method_calls[ -1 ][ 0 ], 'bitMap._removeReciprocalMap' )


    def testRemoveNonexistentDestinationIntervalRaises( self ) :
        # Removing a nonexistent destination interval raises an exception
        with self.assertRaisesRegex( ConfigurationError,
                                     '^Specified destination does not exist in bit map and cannot be removed' ) :
            self.mapUnderTest.removeDestination( self.mockField )


    def testRemoveDestinationInterval( self ) :
        # Removing a valid destination interval also removes the corresponding source interval.
        with unittest.mock.patch.object( self.mapUnderTest, '_BitMap__validateBitRange' ) as br :
            with unittest.mock.patch.object( self.mapUnderTest, '_BitMap__validateSourceOverlaps' ) as so :
                self.mapUnderTest.mapBits( BitRange( [ 0, 4 ] ), BitRange( [ 0, 4 ] ), self.mockField )
                self.mapUnderTest.mapBits( BitRange( [ 5, 6 ] ), BitRange( [ 5, 6 ] ), self.mockField )

                self.assertIn( self.mockField, self.mapUnderTest.destinations )

                self.mapUnderTest.removeDestination( destination = self.mockField,
                                                     interval = [ 0, 4 ] )

                # The actual objects must not have been removed.
                self.assertIn( self.mockField, self.mapUnderTest.destinations )
                self.assertEqual( self.mockRegister, self.mapUnderTest.source )

                # But the interval must have been removed.
                self.checkRemovedSourceInterval( BitRange( [ 0, 4 ] ) )
                self.checkRemovedDestinationInterval( BitRange( [ 0, 4 ] ) )

                # Check that the Field (destination) has been reciprocally called for interval removal.
                self.assertEqual( self.mockField.method_calls[ -1 ][ 0 ], 'bitMap._removeReciprocalMap' )


    def checkRemovedSourceInterval( self, range ) :
        sourceMappings = self.mapUnderTest.intervalMap.keys()
        self.assertNotIn( range, sourceMappings )


    def checkRemovedDestinationInterval( self, range ) :
        destinationMappings = self.mapUnderTest.intervalMap.values()
        for k in destinationMappings :
            self.assertNotEqual( k[ 'interval' ], range )


    def testRemoveSourceInterval( self ) :
        # Removing a valid source interval also removes the corresponding destination interval.
        with unittest.mock.patch.object( self.mapUnderTest, '_BitMap__validateBitRange' ) as br :
            with unittest.mock.patch.object( self.mapUnderTest, '_BitMap__validateSourceOverlaps' ) as so :
                self.mapUnderTest.mapBits( BitRange( [ 0, 4 ] ), BitRange( [ 0, 4 ] ), self.mockField )
                self.mapUnderTest.mapBits( BitRange( [ 5, 6 ] ), BitRange( [ 5, 6 ] ), self.mockField )

                self.assertIn( self.mockField, self.mapUnderTest.destinations )

                self.mapUnderTest.removeSource( interval = [ 0, 4 ] )

                # The actual objects must not have been removed.
                self.assertIn( self.mockField, self.mapUnderTest.destinations )
                self.assertEqual( self.mockRegister, self.mapUnderTest.source )

                # But the interval must have been removed.
                self.checkRemovedSourceInterval( BitRange( [ 0, 4 ] ) )
                self.checkRemovedDestinationInterval( BitRange( [ 0, 4 ] ) )

                # Check that the Field (destination) has been reciprocally called for interval removal.
                self.assertEqual( self.mockField.method_calls[ -1 ][ 0 ], 'bitMap._removeReciprocalMap' )


    def testRemoveSourceRaises( self ) :
        # Removing a source object raises an exception.
        with self.assertRaisesRegex( ConfigurationError, '^Cannot remove source from bit map' ) :
            self.mapUnderTest.removeSource( self.mockRegister )


if __name__ == '__main__' :
    unittest.main()
