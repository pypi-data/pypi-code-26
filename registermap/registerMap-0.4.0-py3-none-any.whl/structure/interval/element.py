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

import logging

from registerMap.exceptions import ConfigurationError


log = logging.getLogger( __name__ )


class ClosedIntegerInterval :
    """
    An integer mathematically closed interval.

    The internal representation is `frozenset`, but `set`, `list` and `tuple` can be used to initialise the interval,
    and for comparison.
    """

    __validContainers = (set, tuple, list)


    def __init__( self, value = None ) :
        if value is not None :
            self.__validateValue( value )
            self.__value = frozenset( value )
        else :
            self.__value = value


    @property
    def size( self ) :
        if self.__value is None :
            thisSize = 0
        else :
            thisSize = max( self.__value ) - min( self.value ) + 1

        return thisSize


    @property
    def value( self ) :
        return self.__value


    @value.setter
    def value( self, value ) :
        self.__validateValue( set( value ) )
        self.__value = frozenset( value )


    def __validateValue( self, value ) :
        errorMessage = 'Interval must be a set of one or two positive integers, {0}'.format( value )
        if not isinstance( value, self.__validContainers ) :
            raise ConfigurationError( errorMessage )

        if any( [ not isinstance( x, int ) for x in value ] ) :
            raise ConfigurationError( errorMessage )

        if any( [ x < 0 for x in value ] ) :
            raise ConfigurationError( errorMessage )

        if len( value ) not in [ 1, 2 ] :
            raise ConfigurationError( errorMessage )


    def __eq__( self, other ) :
        if other is None :
            isEqual = self.__value is other
        elif isinstance( other, self.__validContainers ) :
            isEqual = self.__value == frozenset( other )
        elif other.__value is None :
            isEqual = self.__value is other.__value
        else :
            isEqual = self.__value == other.__value

        return isEqual


    def __ne__( self, other ) :
        return not (self == other)


    def __hash__( self ) :
        # Python seems to think the ClosedIntegerInterval class is not hashable (when used as an index in a dict), so
        # explicitly defining __hash__ method and returning the object id fixes that.
        return hash( self.__value )


    def __add__( self, other ) :
        if isinstance( other, int ) :
            result = ClosedIntegerInterval( value = [ x + other for x in self.__value ] )
        else :
            raise ConfigurationError( 'Must add int to ClosedIntegerInterval' )

        return result


    def __sub__( self, other ) :
        if isinstance( other, int ) :
            result = ClosedIntegerInterval( value = [ x - other for x in self.__value ] )
        else :
            raise ConfigurationError( 'Must add int to ClosedIntegerInterval' )

        return result
