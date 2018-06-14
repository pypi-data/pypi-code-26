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

from registerMap.elements.base import IdentityElement


class MockBitStore( IdentityElement ) :
    def __init__( self, id, sizeBits,
                  bitMap = None ) :
        self.__bitMap = bitMap
        self.__id = id
        self.__sizeBits = sizeBits


    @property
    def bitMap( self ) :
        return self.__bitMap


    @bitMap.setter
    def bitMap( self, value ) :
        self.__bitMap = value


    @property
    def canonicalId( self ) :
        return self.__id


    @property
    def sizeBits( self ) :
        return self.__sizeBits
