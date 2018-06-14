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

from registerMap.structure.memory.space import MemorySpace

from ..memory import Memory as CppMemory


class TestCppMemory( unittest.TestCase ) :

    def setUp( self ) :
        self.memorySpace = MemorySpace()
        self.memorySize = 10

        self.memoryUnderTest = CppMemory( self.memorySpace, self.memorySize )


    def testDefaultAlignmentProperty( self ) :
        self.assertEqual( '', self.memoryUnderTest.alignment )


    def testSizeTypeProperty( self ) :
        self.memorySpace.memoryUnitBits = 32

        self.assertEqual( 'std::uint_least32_t', self.memoryUnderTest.sizeType )


if __name__ == '__main__' :
    unittest.main()
