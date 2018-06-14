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

import collections

from registerMap.exceptions import ConfigurationError

from ..field import Field
from ..base.parameter import Parameter


class BitFieldsParameter( Parameter ) :
    __parameterName = 'bitFields'


    def __init__( self ) :
        super().__init__( self.__parameterName, collections.OrderedDict() )


    @classmethod
    def from_yamlData( cls, yamlData,
                       optional = False,
                       parent = None ) :
        parameter = cls()
        if (not optional) and (cls.__parameterName not in yamlData.keys()) :
            raise ConfigurationError( 'Bitfields not defined in yaml data' )
        elif cls.__parameterName in yamlData.keys() :
            for bitFieldYamlData in yamlData[ cls.__parameterName ] :
                bitField = Field.from_yamlData( bitFieldYamlData,
                                                parentRegister = parent )
                parameter.value[ bitField[ 'name' ] ] = bitField

        return parameter


    def to_yamlData( self ) :
        yamlData = { self.__parameterName : list() }

        for bitField in self.value.values() :
            yamlData[ self.__parameterName ].append( bitField.to_yamlData() )

        return yamlData


class ModeParameter( Parameter ) :
    # The default to_yamlData method implemented in Parameter is adequate for this child.
    validModes = [ 'ro', 'rw', 'wo', 'w1c', 'w0c' ]

    __parameterName = 'mode'


    def __init__( self,
                  value = 'rw' ) :
        super().__init__( self.__parameterName, value )
        self.validate( value )


    def validate( self, value ) :
        if value not in self.validModes :
            raise ConfigurationError(
                'Invalid value, ' + repr( value ) + ' valid value are, ' + repr( self.validModes ) )


    @classmethod
    def from_yamlData( cls, yamlData,
                       optional = False ) :
        parameter = super( ModeParameter, cls ).from_yamlData( yamlData, cls.__parameterName,
                                                               optional = optional )
        if optional and (parameter.value is None) :
            parameter.value = 'rw'
        elif not optional :
            parameter.validate( parameter.value )

        return parameter


class GlobalParameter( Parameter ) :
    __parameterName = 'global'


    def __init__( self, element ) :
        super().__init__( self.__parameterName, element )

        self.__element = element


    def validate( self, value ) :
        pass


    @property
    def value( self ) :
        isGlobal = False
        if self.__element.parent is None :
            isGlobal = True

        return isGlobal


    @value.setter
    def value( self, v ) :
        # This method cannot be used, but need to override the behaviour from parent class.
        assert False


    @classmethod
    def from_yamlData( cls, yamlData,
                       optional = True ) :
        pass


class PublicParameter( Parameter ) :
    # The default to_yamlData method implemented in Parameter is adequate for this child.
    __parameterName = 'public'


    def __init__( self,
                  value = True ) :
        super().__init__( self.__parameterName, value )
        self.validate( value )


    def validate( self, value ) :
        if not isinstance( value, bool ) :
            raise ConfigurationError( 'Public must be specified as boolean' )


    @classmethod
    def from_yamlData( cls, yamlData,
                       optional = False ) :
        parameter = super( PublicParameter, cls ).from_yamlData( yamlData, cls.__parameterName,
                                                                 optional = optional )
        if optional and (parameter.value is None) :
            parameter.value = True
        elif not optional :
            parameter.validate( parameter.value )

        return parameter
