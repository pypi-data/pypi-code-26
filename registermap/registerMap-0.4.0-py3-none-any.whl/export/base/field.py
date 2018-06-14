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


class FieldBase( metaclass = abc.ABCMeta ) :
    """
    Representation of a Field for output using jinja2.
    """


    def __init__( self, element ) :
        super().__init__()

        self._element = element


    @property
    def name( self ) :
        """
        The name of the bit field.
        """
        return self._element[ 'name' ]


    @property
    def size( self ) :
        """
        The number of bits in the bit field.
        """
        return self._element[ 'size' ]


    @property
    @abc.abstractmethod
    def type( self ) :
        """
        The data type to be used in the declaration of the bit field.

        Many languages require a type to be declared for the bit field element, so this method is added to provide
        for that.
        """
        pass
