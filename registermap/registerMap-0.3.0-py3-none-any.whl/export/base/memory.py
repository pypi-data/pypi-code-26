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

import abc


class MemoryBase( metaclass = abc.ABCMeta ) :
    """
    Representation of MemorySpace for output using jinja2.
    """


    def __init__( self, memoryElement, memorySize ) :
        super().__init__()

        self._element = memoryElement

        self.__memorySize = memorySize


    @property
    def baseAddress( self ) :
        """
        The base address of the memory space.
        """
        return hex( self._element.baseAddress )


    @property
    def memoryUnitBits( self ) :
        """
        The number of bits per memory unit.
        """
        return self._element.memoryUnitBits


    @property
    def size( self ) :
        """
        The number of memory units in the memory space.
        """
        return self.__memorySize


    @property
    @abc.abstractmethod
    def sizeType( self ) :
        """
        The language specific type to declare for the memory units.
        """
        pass
