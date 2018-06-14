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

import unittest.mock

from registerMap.structure.memory.space import MemorySpace

from ..memory import MemoryBase


class MockMemory( MemoryBase ) :

    def __init__( self, memoryElement, memorySize ) :
        super().__init__( memoryElement, memorySize )

        self.mock_sizeType = 'std::uint_least8_t'


    @property
    def sizeType( self ) :
        return self.mock_sizeType


class TestMemory( unittest.TestCase ) :

    def setUp( self ) :
        self.memorySpace = MemorySpace()
        self.memorySize = 10

        self.memoryUnderTest = MockMemory( self.memorySpace, self.memorySize )


    def testBaseAddressProperty( self ) :
        self.assertEqual( hex( self.memorySpace.baseAddress ), self.memoryUnderTest.baseAddress )


    def testMemoryUnitSizeBitsProperty( self ) :
        self.assertEqual( self.memorySpace.memoryUnitBits, self.memoryUnderTest.memoryUnitBits )


    def testSizeProperty( self ) :
        self.assertEqual( self.memorySize, self.memoryUnderTest.size )


if __name__ == '__main__' :
    unittest.main()
