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

from registerMap.export.base import MemoryBase


class Memory( MemoryBase ) :
    __knownTypes = {
        8 : 'std::uint_least8_t',
        16 : 'std::uint_least16_t',
        32 : 'std::uint_least32_t',
        64 : 'std::uint_least64_t',
    }


    def __init__( self, memoryElement, memorySize ) :
        super().__init__( memoryElement, memorySize )

        self.alignment = ''


    @property
    def sizeType( self ) :
        assert self.memoryUnitBits <= max( [ x for x in self.__knownTypes.keys() ] )

        leastSize = min( [ x for x in self.__knownTypes.keys() if x >= self.memoryUnitBits ] )

        thisType = self.__knownTypes[ leastSize ]

        return thisType
