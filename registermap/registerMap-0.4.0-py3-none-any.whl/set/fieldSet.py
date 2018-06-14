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

import registerMap.set.elementSet as rmese

from registerMap.exceptions import ConfigurationError


class FieldSet( rmese.ElementSet ) :
    def __init__( self ) :
        super().__init__()


    def add( self, bitField ) :
        """
        Add a specified bit field.

        :param bitField:
        :return:
        """
        globalStateOfSameName = self.findGlobalStateSameName( bitField[ 'name' ] )

        if (not any( globalStateOfSameName )) \
                or (not bitField[ 'global' ]) :
            # A non-global bit field must always be added.
            # A global bit field can only be added if there is no existing global bit field with that name.
            super().add( bitField )
        else :
            raise ConfigurationError(
                'Only one global field of a name can exist, {0}'.format( bitField[ 'name' ] ) )


    def remove( self, bitField ) :
        """
        Remove a specified bit field.
        
        :param bitField:
        :return:
        """
        try :
            super().remove( bitField )
        except KeyError as e :
            raise ConfigurationError( 'Field does not exist in set, {0}'.format( bitField[ 'name' ] ) )


    def findGlobalStateSameName( self, name ) :
        """
        Find the global state of Bit Fields with the same name.

        :param name: Bit Field name to search for.
        :return: List of the global state of each found Bit Field.
        """
        sameName = self.find( name )
        globalSame = list()
        for x in sameName :
            globalSame.append( x[ 'global' ] )

        return globalSame
