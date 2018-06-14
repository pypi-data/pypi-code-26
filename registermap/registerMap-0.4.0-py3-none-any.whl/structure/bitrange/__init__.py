"""
Definition of BitRange
"""
#
# Copyright 2016 Russell Smiley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
import re

import registerMap.utility.io.yaml.parameters.encode as rye
import registerMap.utility.io.yaml.parameters.parse as ryp
import registerMap.utility.observer as rmo

from registerMap.structure import interval as rmbi
from registerMap.utility.io import yaml

from registerMap.exceptions import ParseError


log = logging.getLogger( __name__ )


class BitRange( yaml.Export,
                yaml.Import,
                rmbi.ClosedIntegerInterval ) :
    """
    A representation of a closed interval of bit indices. The interval can be imported to, and exported from, a YAML file.
    """

    __yamlName = 'range'


    def __init__( self, value = None ) :
        super().__init__( value = value )

        self.sizeChangeNotifier = rmo.Observable()


    @property
    def maxValue( self ) :
        maxValue = pow( 2, self.numberBits ) - 1

        return maxValue


    @staticmethod
    def __calculateNumberBits( value ) :
        return max( value ) - min( value ) + 1


    @property
    def numberBits( self ) :
        interval = super().value
        if interval is None :
            returnValue = 0
        else :
            returnValue = max( interval ) - min( interval ) + 1
        return returnValue


    @rmbi.ClosedIntegerInterval.value.setter
    def value( self, v ) :
        rmbi.ClosedIntegerInterval.value.fset( self, v )
        log.debug( 'Notifying of a bit range value change' )
        self.sizeChangeNotifier.notifyObservers()


    @classmethod
    def from_yamlData( cls, yamlData ) :
        bitRange = cls()
        goodResult = bitRange.__decodeBitRange( yamlData )

        if not goodResult :
            raise ParseError( 'Processing bit range data failed. Check log for details. ' + repr( yamlData ) )

        return bitRange


    def __decodeBitRange( self, yamlData ) :
        def recordValue( valueData ) :
            nonlocal self

            if valueData == 'None' :
                self.__value = None
            else :
                rangeData = valueData.strip( '[' ).strip( ']' )
                tokens = re.split( r':', rangeData )
                if len( tokens ) != 2 :
                    log.error( 'Range must have only two values: ' + rangeData )

                try :
                    v = [ int( tokens[ 0 ] ), int( tokens[ 1 ] ) ]
                    self.value = v
                except ValueError :
                    log.error( 'Range must be integers: ' + rangeData )


        return ryp.stringParameter( yamlData, self.__yamlName, recordValue,
                                    optional = False )


    def to_yamlData( self ) :
        value = '[' + str( min( super().value ) ) + ':' + str( max( super().value ) ) + ']'

        return rye.parameter( self.__yamlName, value )
