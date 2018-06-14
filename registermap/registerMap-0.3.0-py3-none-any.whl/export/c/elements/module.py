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

from registerMap.export.base import ModuleBase

from .field import Field
from .register import Register


class Module( ModuleBase ) :

    def __init__( self, moduleElement, RegisterType, FieldType ) :
        super().__init__( moduleElement, RegisterType, FieldType )


    @property
    def address( self ) :
        """
        The absolute base address of the module formatted for C, in hexadecimal.
        """
        return hex( self._element.baseAddress )


    @property
    def offset( self ) :
        """
        The offset of the module formated for C, relative to the base address of the register map.
        """
        return hex( self._element.offset )
