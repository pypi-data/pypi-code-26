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


class IdentityElement( metaclass = abc.ABCMeta ) :
    """
    Provide a unique, numerical identity for a register map element.
    """
    __idCounter = 0


    def __init__( self ) :
        self.__id = IdentityElement.assignId()


    @property
    @abc.abstractmethod
    def canonicalId( self ) :
        """
        Text identity based on the register map structure.

        eg.

            'm1' for a module
            'm1.r1' for a register inside a module
            'm1.r1.f1' for a field inside a register
        """
        pass


    @property
    def id( self ) :
        """
        Unique, numerical (integer) identity.
        """
        return self.__id


    @staticmethod
    def assignId() :
        IdentityElement.__idCounter += 1

        return IdentityElement.__idCounter
