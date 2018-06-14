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


class ModuleInterface( metaclass = abc.ABCMeta ) :

    @property
    @abc.abstractmethod
    def assignedMemoryUnits( self ) :
        """
        The number of memory units in the module or module instance.
        """
        pass


    @property
    @abc.abstractmethod
    def baseAddress( self ) :
        """
        The base (smallest numerical value) address of the module, or module instance.
        """
        pass


    @property
    @abc.abstractmethod
    def canonicalId( self ) :
        pass


    @property
    @abc.abstractmethod
    def endAddress( self ) :
        """
        The address of the last assigned memory unit in the module or module instance.

        In the case of a multibyte register, this would be the address of the last memory unit in the register (the
        address with the highest numerical value).
        """
        pass


    @property
    @abc.abstractmethod
    def memory( self ) :
        """
        Register map memory space.
        """
        return self.__memory


    @property
    @abc.abstractmethod
    def offset( self ) :
        """
        The offset of the module or module instance relative to the base address of the register map.
        """
        pass


    @property
    @abc.abstractmethod
    def previousElement( self ) :
        """
        The element preceding this element in the register map.
        """
        pass


    @previousElement.setter
    @abc.abstractmethod
    def previousElement( self, value ) :
        """
        Set the element preceding this element in the register map.
        :param value:
        :return:
        """
        pass


    @property
    @abc.abstractmethod
    def spanMemoryUnits( self ) :
        """
        The total number of memory units spanned by the module or module instance; including any gaps of unassigned
        memory units. In essence the span is the difference between the base address and end address of the module or
        module instance.

        eg.
          In a module with 4 registers totalling 4 bytes with gaps totalling 2 bytes, the span will be 6 bytes.
        """
        pass


    @abc.abstractmethod
    def __getitem__( self, item ) :
        pass


    @abc.abstractmethod
    def __setitem__( self, key, value ) :
        pass
