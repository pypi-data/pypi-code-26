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
import logging

import registerMap.utility.io.yaml.parameters.parse as ryp
import registerMap.utility.observer as rmo

from registerMap.utility.io import yaml

from registerMap.exceptions import ConstraintError, ParseError

from .constraints import \
    AbstractConstraint, \
    AlignmentMemoryUnits, \
    FixedAddress, \
    FixedSizeMemoryUnits, \
    validatePositive, \
    validatePositiveNonZero


log = logging.getLogger( __name__ )


class ConstraintTable( yaml.Import, yaml.Export ) :
    """
    Express constraints to be applied to RegisterMap, Module, Register or BitField.

    The constraint table notifies registered observers about changes to address or size. The notifications are triggered
     by user modification of a constraint in the table.
    """
    validConstraints = collections.OrderedDict( [ ('fixedAddress', FixedAddress),
                                                  ('alignmentMemoryUnits', AlignmentMemoryUnits),
                                                  ('fixedSizeMemoryUnits', FixedSizeMemoryUnits) ] )


    def __init__( self, memory ) :
        super().__init__()

        self.addressChangeNotifier = rmo.Observable()
        self.sizeChangeNotifier = rmo.Observable()

        self.__memory = memory
        self.__constraints = collections.OrderedDict()
        self.__notifiers = {
            'alignmentMemoryUnits' : self.addressChangeNotifier.notifyObservers,
            'fixedAddress' : self.addressChangeNotifier.notifyObservers,
            'fixedSizeMemoryUnits' : self.sizeChangeNotifier.notifyObservers
        }


    @property
    def isEmpty( self ) :
        return len( self.__constraints ) == 0


    def __delitem__( self, key ) :
        log.debug( 'Deleting constraint, ' + repr( key ) )
        self.__validateGetItem( key )
        del self.__constraints[ key ]
        self.__notifiers[ key ]( self )


    def __getitem__( self, item ) :
        self.__validateGetItem( item )
        return self.__constraints[ item ].value


    def __validateGetItem( self, item ) :
        self.__validateConstraintName( item )
        try :
            self.__constraints[ item ]
        except KeyError as e :
            raise ConstraintError( 'Constraint not applied, {0}'.format( repr( item ) ) ) from e


    def __len__( self ) :
        return len( self.__constraints )


    def __setitem__( self, key, value ) :
        log.debug( 'Setting constraint value, ' + repr( key ) + ', ' + repr( value ) )
        self.__validateConstraintName( key )
        self.__constraints[ key ] = self.validConstraints[ key ]( self.__memory, value )
        self.__validateAddressConstraintConsistency()
        self.__notifiers[ key ]( key )


    def __validateConstraintName( self, name ) :
        if name not in self.validConstraints.keys() :
            raise ConstraintError( 'Not a valid constraint, ' + repr( name ) )


    def __validateAddressConstraintConsistency( self ) :
        if FixedAddress.name in self.__constraints.keys() :
            testAddress = self.__constraints[ FixedAddress.name ].value
        else :
            testAddress = 0

        collectedAddresses = [ ]
        for constraint in self.__constraints.values() :
            if constraint.type == AbstractConstraint.constraintTypes[ 'address' ] :
                collectedAddresses.append( constraint.calculate( testAddress ) )

        if not all( collectedAddresses[ 0 ] == x for x in collectedAddresses ) :
            raise ConstraintError( 'Address constraints conflict' )


    def applyAddressConstraints( self, addressValue ) :
        newAddress = addressValue
        for constraint in self.__constraints.values() :
            if constraint.type == AbstractConstraint.constraintTypes[ 'address' ] :
                newAddress = constraint.calculate( addressValue )
                addressValue = newAddress

        return newAddress


    def applySizeConstraints( self, sizeValue ) :
        newSize = sizeValue
        for constraint in self.__constraints.values() :
            if constraint.type == AbstractConstraint.constraintTypes[ 'size' ] :
                newSize = constraint.calculate( sizeValue )
                sizeValue = newSize

        return newSize


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace,
                       optional = False ) :
        thisConstraints = cls( memorySpace )
        goodResult = thisConstraints.__decodeConstraintTable( yamlData, memorySpace,
                                                              optional = optional )

        if (not goodResult) and (not optional) :
            raise ParseError( 'Processing constraint data failed. Check log for details. ' + repr( yamlData ) )

        return thisConstraints


    def __decodeConstraintTable( self, yamlData, memorySpace,
                                 optional = False ) :
        def recordConstraint( name, value ) :
            nonlocal self

            self[ name ] = value


        def getParameters( thisData ) :
            nonlocal self, memorySpace

            # All constraints are optional
            # Expecting a list of constraints
            for constraintClass in self.validConstraints.values() :
                constraint = constraintClass.from_yamlData( thisData, memorySpace,
                                                            optional = True )
                if constraint is not None :
                    self.__constraints[ constraint.name ] = constraint

            return True


        keyName = 'constraints'

        return ryp.complexParameter( yamlData, keyName, getParameters,
                                     optional = optional )


    def to_yamlData( self ) :
        parameters = list()

        for constraint in self.__constraints.values() :
            parameters.append( constraint.to_yamlData() )

        keyName = 'constraints'
        yamlData = { keyName : { } }

        for thisParameter in parameters :
            yamlData[ keyName ].update( thisParameter )

        return yamlData
