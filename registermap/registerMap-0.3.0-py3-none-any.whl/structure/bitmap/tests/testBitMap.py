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
import unittest.mock

import registerMap.structure.bitmap as rmbm

from .mocks import MockBitStore


class TestBitMapRegisterSize( unittest.TestCase ) :
    def setUp( self ) :
        self.sourceSize = 16
        self.sourceId = 'testSource'
        self.mock_source = MockBitStore( self.sourceId, self.sourceSize )


    def testRegisterSize( self ) :
        bm = rmbm.BitMap( self.mock_source )

        self.assertEqual( bm.source, self.mock_source )


if __name__ == '__main__' :
    unittest.main()
