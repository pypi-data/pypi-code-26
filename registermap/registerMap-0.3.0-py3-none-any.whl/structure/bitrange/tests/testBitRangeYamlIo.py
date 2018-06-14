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
import unittest

import registerMap.structure.bitrange as rmbr


log = logging.getLogger( __name__ )


class TestBitRangeLoadSave( unittest.TestCase ) :
    def setUp( self ) :
        self.expectedValue = [ 3, 7 ]
        self.testBitRange = rmbr.BitRange( value = self.expectedValue )


    def testLoadSave( self ) :
        encodedYamlData = self.testBitRange.to_yamlData()
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = rmbr.BitRange.from_yamlData( encodedYamlData )

        self.assertEqual( decodedData.value, self.testBitRange.value )


    def testNoneValueDecode( self ) :
        yamlData = { 'range' : None }
        decodedData = rmbr.BitRange.from_yamlData( yamlData )

        self.assertIsNone( decodedData.value )


if __name__ == '__main__' :
    unittest.main()
