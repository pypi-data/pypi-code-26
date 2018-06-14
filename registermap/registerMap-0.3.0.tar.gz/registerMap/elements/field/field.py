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

import collections
import logging

from registerMap.structure.bitmap import BitMap
from registerMap.utility.io import yaml
from registerMap.utility.io.yaml.parameters.encode import \
    HexInt, \
    parameter
from registerMap.utility.io.yaml.parameters.parse import \
    complexParameter, \
    integerParameter, \
    stringParameter
from registerMap.utility.observer import \
    Observable, \
    SizeChangeObserver

from registerMap.exceptions import \
    ConfigurationError, \
    ParseError

from ..base import \
    BitStoreInterface, \
    IdentityElement

from .parameters import \
    GlobalParameter, \
    NameParameter, \
    Parameter, \
    ResetValueParameter, \
    SizeParameter, \
    StringParameter


log = logging.getLogger( __name__ )


class Field( IdentityElement,
             BitStoreInterface,
             yaml.Export,
             yaml.Import ) :
    """
    Representation of a bit field in a register.

    The following parameters are available for every BitField:

    # description (str) - Expanded description of the BitField object.
    # global (bool) - Assert whether or not the BitField object is global.
    # name (str) - Alphanumeric name of the BitField object.
    # public (bool) - Assert whether or not the BitField object is public.
    # resetValue (int) - Reset (default) value of the BitField object.
    # size (int) - The number of bits in the BitField object.
    # summary (str) - Short description of the BitField object.
    """
    __defaultName = 'unassigned'
    __keyName = 'field'


    def __init__( self,
                  parent = None ) :
        super().__init__()

        self.sizeChangeNotifier = Observable()

        self.__bitMap = BitMap( self )
        self.__parentRegister = parent
        self.__sizeChangeObserver = SizeChangeObserver( self )

        self.__coreData = {
            'description' : StringParameter( name = 'description',
                                             value = '' ),
            'global' : GlobalParameter( self ),
            'name' : NameParameter( value = self.__defaultName ),
            'resetValue' : ResetValueParameter( value = 0,
                                                size = 0 ),
            'summary' : StringParameter( name = 'summary',
                                         value = '' ),
        }
        self.__coreData[ 'size' ] = SizeParameter( self.__coreData[ 'resetValue' ] )

        self.__userData = collections.OrderedDict()


    def __getitem__( self, item ) :
        if item in self.__coreData :
            value = self.__coreData[ item ].value
        elif item in self.__userData :
            value = self.__userData[ item ].value
        else :
            raise KeyError( 'Field parameter not in core or user data, {0} ({1})'.format( item, self.canonicalId ) )

        return value


    def __setitem__( self, key, value ) :
        if key in self.__coreData :
            self.__coreData[ key ].value = value
        else :
            assert not key.startswith( '_' )

            # Assume user data
            self.__userData[ key ] = Parameter( name = key,
                                                value = value )

        if key == 'size' :
            log.debug( 'Notifying on field size change, {0}: {1}'.format( self.__coreData[ 'name' ].value,
                                                                          value ) )
            self.sizeChangeNotifier.notifyObservers()


    @property
    def bitMap( self ) :
        return self.__bitMap


    @property
    def canonicalId( self ) :
        if self.__parentRegister is not None :
            canonicalName = '{0}.{1}'.format( self.__parentRegister.canonicalId,
                                              self.__coreData[ 'name' ].value )
        else :
            canonicalName = '{0}'.format( self.__coreData[ 'name' ].value )

        return canonicalName


    @property
    def parent( self ) :
        return self.__parentRegister


    @property
    def sizeBits( self ) :
        return self.__coreData[ 'size' ].value


    def reviewSizeChange( self ) :
        # Cascade the size change
        self.sizeChangeNotifier.notifyObservers()


    @classmethod
    def from_yamlData( cls, yamlData,
                       parentRegister = None ) :
        field = cls()
        goodResult = field.__decodeField( yamlData, parentRegister )

        if not goodResult :
            raise ParseError( 'Processing field data failed. Check log for details. ' + repr( yamlData ) )

        return field


    def __decodeField( self, yamlData, parentRegister ) :
        def acquireDescription( thisData ) :
            nonlocal self
            self.__coreData[ 'description' ] = StringParameter.from_yamlData( thisData, 'description',
                                                                              optional = True )


        def recordParent( value ) :
            nonlocal parentRegister

            assert value is not None

            if parentRegister is None :
                # Must specify a parent register for local fields.
                raise ParseError( 'Parent register not specified for YAML acquisition of a local field' )
            elif parentRegister.canonicalId != value :
                raise ParseError( 'Parent register does not match YAML specification, spec({0}), yaml({1})'.format(
                    parentRegister.canonicalId,
                    value ) )

            self.__parentRegister = parentRegister


        def acquireName( thisData ) :
            nonlocal self
            self.__coreData[ 'name' ] = NameParameter.from_yamlData( thisData, 'name' )


        def acquireResetValue( thisData ) :
            nonlocal self
            self.__coreData[ 'resetValue' ] = ResetValueParameter.from_yamlData( thisData, 'resetValue' )


        def recordSize( value ) :
            nonlocal self
            self.__coreData[ 'size' ] = SizeParameter( self.__coreData[ 'resetValue' ] )
            self.__coreData[ 'size' ].value = value

            # Make sure that we subscribe to notification of bit range size changes.
            self.__coreData[ 'size' ].sizeChangeNotifier.addObserver( self.__sizeChangeObserver )


        def acquireSummary( thisData ) :
            nonlocal self
            self.__coreData[ 'summary' ] = StringParameter.from_yamlData( thisData, 'summary',
                                                                          optional = True )


        def acquireUserParameters( thisData ) :
            nonlocal self
            for name, value in thisData.items() :
                if (name not in self.__coreData) \
                        and (not name.startswith( '_' )) :
                    # Assume a user defined parameter.
                    self.__userData[ name ] = Parameter( name = name,
                                                         value = value )


        def getParameters( thisData ) :
            nonlocal self

            acquireName( thisData )
            acquireResetValue( thisData )

            # The size record is tightly coupled to the reset value, but it needs a separate parsing implementation.
            goodResult = integerParameter( thisData, 'size', recordSize )

            acquireDescription( thisData )
            acquireSummary( thisData )

            stringParameter( thisData, 'parent', recordParent,
                             optional = True )

            acquireUserParameters( thisData )

            return goodResult


        return complexParameter( yamlData, Field.__keyName, getParameters )


    def convertToLocal( self, parentRegister,
                        removeOthers = False ) :
        """
        Convert field to non-global, that is, dedicated bit maps to a single register.
        """


        def removeOtherRegisters() :
            nonlocal parentRegister

            otherRegisters = [ x for x in self.__bitMap.destinations if x != parentRegister.bitMap.source ]

            assert len( otherRegisters ) == (len( self.__bitMap.destinations ) - 1)

            for thisRegister in otherRegisters :
                self.__bitMap.removeDestination( thisRegister )


        if parentRegister.bitMap.source not in self.__bitMap.destinations :
            raise ConfigurationError( 'Field does not map to the register selected for parent' )
        if not removeOthers :
            if (parentRegister.bitMap.source in self.__bitMap.destinations) \
                    and (len( self.__bitMap.destinations ) > 1) :
                raise ConfigurationError( 'Field maps to multiple registers' )
        else :
            removeOtherRegisters()

        self.__parentRegister = parentRegister


    def convertToGlobal( self ) :
        """
        Convert field to global, that is, allowing bit maps to multiple registers.
        """
        self.__parentRegister = None


    def __encodeCoreParameters( self ) :
        """
        Prepare core parameters for output to YAML.

        :return: List of encoded parameters.
        """
        encodedParameters = [ parameter( 'size', self.__coreData[ 'size' ].value ),
                              parameter( 'name', self.__coreData[ 'name' ].value ),
                              parameter( 'resetValue', HexInt( self.__coreData[ 'resetValue' ].value ) ) ]

        if self.__coreData[ 'description' ] != '' :
            encodedParameters.append( parameter( 'description', self.__coreData[ 'description' ].value ) )
        if self.__coreData[ 'summary' ] != '' :
            encodedParameters.append( parameter( 'summary', self.__coreData[ 'summary' ].value ) )

        if not self.__coreData[ 'global' ].value :
            assert self.__parentRegister.canonicalId is not None

            encodedParameters.append( parameter( 'parent', self.__parentRegister.canonicalId ) )

        return encodedParameters


    def __encodeUserParameters( self ) :
        """
        Prepare user parameters for output to YAML.

        :return: List of encoded parameters.
        """
        encodedParameters = list()
        for name, element in self.__userData.items() :
            encodedParameters.append( parameter( name, element.value ) )

        return encodedParameters


    def to_yamlData( self ) :
        """
        Generate YAML data structure representation of Field ready for use with yaml.dump.

        :return: YAML data structure.
        """
        coreParameters = self.__encodeCoreParameters()
        userParameters = self.__encodeUserParameters()

        parameters = coreParameters + userParameters

        yamlData = { Field.__keyName : { } }

        for thisParameter in parameters :
            yamlData[ Field.__keyName ].update( thisParameter )

        return yamlData
