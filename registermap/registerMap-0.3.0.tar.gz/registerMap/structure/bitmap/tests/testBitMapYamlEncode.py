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

import logging
import unittest.mock

from registerMap.elements.field import Field
from registerMap.structure.bitrange import BitRange

from .mocks import MockBitStore

from .. import BitMap


log = logging.getLogger( __name__ )


class TestEncodeYamlBitMap( unittest.TestCase ) :
    def setUp( self ) :
        self.mockSource = MockBitStore( 'module.register', 10 )
        self.bitMapUnderTest = BitMap( self.mockSource )

        self.mockSource.bitMap = self.bitMapUnderTest


    def testEncodeEmptyBitMap( self ) :
        # An empty bitmap encodes only the source info

        encodedYamlData = self.bitMapUnderTest.to_yamlData()

        self.assertEqual( encodedYamlData[ 'bitmap' ], list() )


class TestEncodeYamlBitMapIntervals( unittest.TestCase ) :
    """
    Demonstrate YAML encoding BitMap intervals.
    """


    def setUp( self ) :
        def constructMockDestination() :
            nonlocal self

            self.destinationMockBitmap = unittest.mock.create_autospec( BitMap )

            self.mockDestination = unittest.mock.create_autospec( Field )

            idp = unittest.mock.PropertyMock( return_value = 'module.register.field' )
            type( self.mockDestination ).canonicalId = idp

            idbm = unittest.mock.PropertyMock( return_value = self.destinationMockBitmap )
            type( self.mockDestination ).bitMap = idbm


        self.mockSource = MockBitStore( 'module.register', 10 )
        self.bitMapUnderTest = BitMap( self.mockSource )

        self.mockSource.bitMap = self.bitMapUnderTest

        constructMockDestination()


    def testEncodeMapping( self ) :
        with unittest.mock.patch.object( self.bitMapUnderTest, '_BitMap__validateBitRange' ) :
            with unittest.mock.patch.object( self.bitMapUnderTest, '_BitMap__validateSourceOverlaps' ) :
                self.bitMapUnderTest.mapBits( BitRange( [ 4, 7 ] ), BitRange( (0, 3) ), self.mockDestination )

                encodedYamlData = self.bitMapUnderTest.to_yamlData()

                self.assertEqual( len( encodedYamlData[ 'bitmap' ] ), 1 )
                self.assertEqual( encodedYamlData[ 'bitmap' ][ 0 ][ 'source' ], '[4:7]' )
                self.assertEqual( encodedYamlData[ 'bitmap' ][ 0 ][ 'destination' ], '[0:3]' )
                self.assertEqual( encodedYamlData[ 'bitmap' ][ 0 ][ 'destinationId' ],
                                  self.mockDestination.canonicalId )


if __name__ == '__main__' :
    unittest.main()
