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

from registerMap.exceptions import ConfigurationError
from registerMap.utility.observer import \
    Observable, \
    SizeChangeObserver

from ..base.parameter import Parameter


class BooleanParameter( Parameter ) :
    def __init__( self,
                  name = None,
                  value = True ) :
        super().__init__( name = name,
                          value = value )


    def validate( self, value ) :
        if not isinstance( value, bool ) :
            raise ConfigurationError( 'Must be specified as boolean' )


class GlobalParameter( Parameter ) :
    __parameterName = 'global'


    def __init__( self, element ) :
        self.__element = element
        super().__init__( name = self.__parameterName,
                          value = self.__evaluateGlobal() )


    def __evaluateGlobal( self ) :
        isGlobal = False
        if self.__element.parent is None :
            isGlobal = True

        return isGlobal


    @property
    def value( self ) :
        return self.__evaluateGlobal()


class IntParameter( Parameter ) :
    def __init__( self,
                  name = None,
                  value = 0 ) :
        super().__init__( name = name,
                          value = value )


    def validate( self, value ) :
        if not isinstance( value, int ) :
            raise ConfigurationError( 'Must be an int, not {0}'.format( value ) )


class PositiveIntParameter( IntParameter ) :
    def __init__( self,
                  name = None,
                  value = 0 ) :
        super().__init__( name = name,
                          value = value )


    def validate( self, value ) :
        super().validate( value )

        if value < 0 :
            raise ConfigurationError( 'Must be a positive int, not {0}'.format( value ) )


class StringParameter( Parameter ) :
    def __init__( self,
                  name = None,
                  value = '' ) :
        super().__init__( name = name,
                          value = value )


    def validate( self, value ) :
        if not isinstance( value, str ) :
            raise ConfigurationError( 'Must be a string, not {0}'.format( type( value ) ) )


class NameParameter( StringParameter ) :
    __parameterName = 'name'


    def __init__( self,
                  value = 'unassigned' ) :
        super().__init__( name = self.__parameterName,
                          value = value )


class ResetValueParameter( PositiveIntParameter ) :
    __parameterName = 'resetValue'


    def __init__( self,
                  value = 0,
                  size = 0 ) :
        """

        :type value: int
        :type size: int
        """
        self.__validateSize( size )
        self.__numberBits = size

        super().__init__( name = self.__parameterName,
                          value = value )


    @property
    def maxValue( self ) :
        thisMax = pow( 2, self.__numberBits ) - 1

        return thisMax


    @property
    def size( self ) :
        return self.__numberBits


    def __validateSize( self, value ) :
        if (not isinstance( value, int )) \
                or (value < 0) :
            raise ConfigurationError( 'Size must be positive int, {0}'.format( value ) )


    @size.setter
    def size( self, value ) :
        self.__validateSize( value )
        self.__numberBits = value


    def validate( self, value ) :
        super().validate( value )

        maxValue = self.maxValue
        if value > maxValue :
            raise ConfigurationError(
                'Reset value cannot exceed number of bits of field, {0} maximum, {1} specified'.format( maxValue,
                                                                                                        value ) )


class SizeParameter( Parameter ) :
    __parameterName = 'size'


    def __init__( self, sizeResetParameter ) :
        super().__init__( name = self.__parameterName )
        assert isinstance( sizeResetParameter, ResetValueParameter )

        self.__sizeChangeObserver = SizeChangeObserver( self )
        self.__sizeResetParameter = sizeResetParameter

        self.sizeChangeNotifier = Observable()


    @property
    def value( self ) :
        return self.__sizeResetParameter.size


    @value.setter
    def value( self, v ) :
        self.__sizeResetParameter.size = v


    def reviewSizeChange( self ) :
        # Cascade the size change
        self.sizeChangeNotifier.notifyObservers()
