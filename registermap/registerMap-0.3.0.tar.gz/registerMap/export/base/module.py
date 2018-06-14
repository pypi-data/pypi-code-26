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


class ModuleRegistersIndirection :

    def __init__( self, registerElements, RegisterType, FieldType ) :
        self.__elements = registerElements

        self.__FieldType = FieldType
        self.__RegisterType = RegisterType


    def __getitem__( self, item ) :
        return self.__RegisterType( self.__elements[ item ], self.__FieldType )


    def __len__( self ) :
        return len( self.__elements )


class ModuleBase( metaclass = abc.ABCMeta ) :
    """
    Representation of a Module for output using jinja2.
    """


    def __init__( self, moduleElement, RegisterType, FieldType ) :
        self._element = moduleElement

        self.__FieldType = FieldType
        self.__RegisterType = RegisterType


    @property
    def name( self ) :
        return self._element[ 'name' ]


    @property
    def registers( self ) :
        return ModuleRegistersIndirection( list( self._element[ 'registers' ].values() ),
                                           self.__RegisterType,
                                           self.__FieldType )


    @property
    @abc.abstractmethod
    def address( self ) :
        """
        The absolute base address of the module formatted for the target language.
        """
        pass


    @property
    @abc.abstractmethod
    def offset( self ) :
        """
        The offset of the module formatted for the target language, relative to the base address of the register map.
        """
        pass
