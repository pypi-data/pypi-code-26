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
import logging


log = logging.getLogger( __name__ )


class RegisterMapModulesIndirection :

    def __init__( self, moduleElements, ModuleType, RegisterType, FieldType ) :
        self.__elements = moduleElements

        self.__FieldType = FieldType
        self.__ModuleType = ModuleType
        self.__RegisterType = RegisterType


    def __getitem__( self, item ) :
        return self.__ModuleType( self.__elements[ item ], self.__RegisterType, self.__FieldType )


    def __len__( self ) :
        return len( self.__elements )


class RegisterMapBase( metaclass = abc.ABCMeta ) :
    """
    Representation of a RegisterMap for output using jinja2.
    """


    def __init__( self, name, registerMapElement, typeConfiguration ) :
        super().__init__()

        self.name = name
        self._element = registerMapElement

        self.__typeConfiguration = typeConfiguration
        self.__memory = self.__typeConfiguration[ 'memory' ]( self._element.memory, self._element.spanMemoryUnits )


    @property
    def memory( self ) :
        return self.__memory


    @property
    def modules( self ) :
        return RegisterMapModulesIndirection(
            list( self._element[ 'modules' ].values() ),
            self.__typeConfiguration[ 'module' ],
            self.__typeConfiguration[ 'register' ],
            self.__typeConfiguration[ 'field' ] )


    @property
    def spanMemoryUnits( self ) :
        return self._element.spanMemoryUnits
