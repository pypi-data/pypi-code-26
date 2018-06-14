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
import math

from registerMap.exceptions import ParseError
from registerMap.elements.field import Field
from registerMap.structure.bitmap import BitMap
from registerMap.structure.bitrange import BitRange
from registerMap.structure.memory.element import Size
from registerMap.utility.io import yaml
from registerMap.utility.io.yaml.parameters.encode import parameter
from registerMap.utility.io.yaml.parameters.parse import complexParameter
from registerMap.utility.observer import \
    Observable, \
    SizeChangeObserver

from ..base import \
    BitStoreInterface, \
    IdentityElement, \
    SizeObservableInterface
from ..base.parameter import \
    ConstraintsParameter, \
    Parameter

from .parameters import \
    BitFieldsParameter, \
    GlobalParameter, \
    ModeParameter, \
    PublicParameter


log = logging.getLogger( __name__ )


class Register( IdentityElement,
                BitStoreInterface,
                SizeObservableInterface,
                yaml.Export,
                yaml.Import ) :
    """
    Representation of the size of a register, it's fields and "core" and user defined parameters. Fields and constraints
    define the registers size.
    """
    __DEFAULT_SIZE = 1
    __YAML_NAME = 'register'


    def __init__( self, memorySpace, setCollection,
                  parent = None ) :
        super().__init__()

        self.sizeChangeNotifier = Observable()

        self.__setCollection = setCollection
        self.__bitMap = BitMap( self )

        # self.__element is only used here for tracking the size.
        self.__elementSizeMemoryUnits = Size()
        self.__elementSizeMemoryUnits.value = self.__DEFAULT_SIZE

        self.__memory = memorySpace
        self.__parentModule = parent
        self.__sizeChangeMade = False
        self.__sizeObserver = SizeChangeObserver( self )

        self.__coreData = {
            'fields' : BitFieldsParameter(),
            'constraints' : ConstraintsParameter( self.__memory ),
            'description' : Parameter( 'description', '' ),
            'global' : GlobalParameter( self ),
            'mode' : ModeParameter( 'rw' ),
            'name' : Parameter( 'name', None ),
            'public' : PublicParameter( True ),
            'summary' : Parameter( 'summary', '' )
        }

        self.__userData = collections.OrderedDict()

        self.__registerConstraintNotifiers()


    def __registerConstraintNotifiers( self ) :
        """
        Subscribe to size change notificatioins from constraints.
        """
        self.__coreData[ 'constraints' ].value.sizeChangeNotifier.addObserver( self.__sizeObserver )


    def reviewSizeChange( self ) :
        """
        Used by size change subscriptions to notify a Register object that it may need to reconsider it's size.

        The Register notifies its own subscribers if there is a change.
        """
        newSize = self.__calculateExtentMemoryUnits()
        if newSize != self.__elementSizeMemoryUnits.value :
            self.__elementSizeMemoryUnits.value = newSize
            self.sizeChangeNotifier.notifyObservers()


    def __calculateExtentMemoryUnits( self ) :
        """
        The total number of memory units in the register after any constraints have been applied.

        Since the number of memory units is quantized to the memory unit size, then the result of this function
        implicitly includes both assigned and unassigned bits.
        """
        allBits = self.sizeAllocatedFields

        sizeMemoryUnits = math.ceil( float( allBits ) / self.__memory.memoryUnitBits )

        finalSize = self.__coreData[ 'constraints' ].value.applySizeConstraints( sizeMemoryUnits )
        if finalSize != sizeMemoryUnits :
            log.info( 'Constraint applied in calculating register size, {0}'.format( self[ 'name' ] ) )

        return finalSize


    @property
    def bitMap( self ) :
        return self.__bitMap


    @property
    def canonicalId( self ) :
        if self.__parentModule is not None :
            canonicalName = '{0}.{1}'.format( self.__parentModule[ 'name' ],
                                              self.__coreData[ 'name' ].value )
        else :
            canonicalName = '{0}'.format( self.__coreData[ 'name' ].value )
        return canonicalName


    @property
    def memory( self ) :
        return self.__memory


    @property
    def parent( self ) :
        return self.__parentModule


    @property
    def size( self ) :
        """
        Size object used for tracking Register size.
        """
        return self.__elementSizeMemoryUnits


    @property
    def sizeAllocatedFields( self ) :
        """
        The total number of bits in the field intervals allocated to this register.
        """
        allocatedBits = 0
        for thisInterval in self.__bitMap.sourceIntervals :
            allocatedBits += thisInterval.numberBits

        return allocatedBits


    @property
    def sizeBits( self ) :
        """
        The number of bits in the memory units used by the register.
        """
        numberBits = self.__elementSizeMemoryUnits.value * self.__memory.memoryUnitBits
        return numberBits


    @property
    def sizeMemoryUnits( self ) :
        """
        The integer number of memory units used by the register.
        """
        return self.__elementSizeMemoryUnits.value


    def addField( self, name, registerBitInterval,
                  fieldBitInterval = None,
                  isGlobal = False ) :
        """
        :param name: Name of new field. Must be unique to the register the field is a member of, except special
        names 'reserved' and 'unassigned'. If isGlobal is True then the name must be unique in the set of global
        fields, otherwise the specified ranges will be added to the existing global field definition.
        :param registerBitInterval: Range of register bits allocated to the new field.
        :param fieldBitInterval: Range of field bits allocated to the register.
        :param isGlobal: Is the new field referencing a global field definition?
        :return:
        """


        def createNewField() :
            nonlocal fieldBitInterval, isGlobal, name, registerBitInterval, self

            log.debug(
                'Creating new bit field, {0}.{1}, {2}<=>{3}'.format( self[ 'name' ],
                                                                     name,
                                                                     registerBitInterval,
                                                                     fieldBitInterval ) )
            if fieldBitInterval is None :
                fieldBitInterval = ((max( registerBitInterval ) - min( registerBitInterval )), 0)

            if not isGlobal :
                newField = Field( parent = self )
            else :
                newField = Field()

            newField[ 'name' ] = name
            newField[ 'size' ] = max( fieldBitInterval ) + 1

            # Need to consider the impact of the new field on register size now, otherwise mapping bits can raise.
            self.__reviewRegisterSize( registerBitInterval )

            self.__bitMap.mapBits( BitRange( registerBitInterval ), BitRange( fieldBitInterval ), newField )

            self.__setCollection.fieldSet.add( newField )
            self.__coreData[ 'fields' ].value[ newField[ 'name' ] ] = newField

            return newField


        def linkToExistingGlobalField() :
            """
            Link existing global Field to Register.

            :return:
            """
            nonlocal existingFields, fieldBitInterval, name, registerBitInterval, self

            log.debug( 'Modifying the existing global field, {0}'.format( name ) )
            globalField = [ x for x in existingFields if x[ 'global' ] ]

            # If there's 0, or >1 then something has gone wrong in the function above.
            assert len( globalField ) == 1

            revisedField = self.__createFieldToRegisterMapping( globalField[ 0 ],
                                                                registerBitInterval,
                                                                fieldBitInterval )

            return revisedField


        def linkToExistingLocalField( localField ) :
            """
            Link local (non-global) Field to Register.

            :param localField:
            :return:
            """
            nonlocal name, self

            log.debug( 'Modifying the existing local field, {0}'.format( name ) )

            revisedField = self.__createFieldToRegisterMapping( localField, registerBitInterval, fieldBitInterval )

            return revisedField


        existingFields = self.__setCollection.fieldSet.find( name )
        existingFieldsThisRegister = [ x for x in existingFields if
                                       (not x[ 'global' ]) and all( [ y == self for y in x.bitMap.destinations ] ) ]
        if existingFields \
                and (not isGlobal) \
                and any( existingFieldsThisRegister ) :
            # User has requested a local field

            # If there's 0, or >1 then something has gone wrong; there can be only one local field with a given name
            # in a register.
            assert len( existingFieldsThisRegister ) == 1

            field = linkToExistingLocalField( existingFieldsThisRegister[ 0 ] )
        elif existingFields \
                and isGlobal \
                and any( [ x[ 'global' ] for x in existingFields ] ) :
            # User has requested a global field and one already exists.
            field = linkToExistingGlobalField()
        else :
            # Create a new field.
            field = createNewField()

        log.debug( 'Subscribing to field changes, {0}, for {1}'.format(
            field[ 'name' ],
            self.__coreData[ 'name' ] ) )
        # Watch the field for size changes.
        field.sizeChangeNotifier.addObserver( self.__sizeObserver )

        if self.__sizeChangeMade:
            self.sizeChangeNotifier.notifyObservers()
            self.__sizeChangeMade = False

        return field


    def __createFieldToRegisterMapping( self, thisField, registerBitInterval, fieldBitInterval ) :
        """
        Creating mapping of Field to Register.

        :param thisField:
        :return:
        """
        assert fieldBitInterval is not None

        # Need to consider the impact of the new field on register and field size now, otherwise mapping bits can raise.
        self.__reviewRegisterSize( registerBitInterval )
        self.__reviewFieldSize( thisField, fieldBitInterval )

        self.__bitMap.mapBits( BitRange( registerBitInterval ), BitRange( fieldBitInterval ), thisField )

        return thisField


    def __reviewRegisterSize( self, registerInterval ) :
        # Register size only needs to be increased by the size of the interval being allocated to the register.
        # The field size could be larger even though it is new, for various reasons.
        #   eg. register[2:4] <=> field[5:7] => field size = 8, interval size = 3
        #       therefore the register potentially only needs to increase by 3 bits (interval size)
        proposedRegisterExtent = max( registerInterval ) + 1

        if proposedRegisterExtent > self.sizeBits :
            # Increase the size of the register to accommodate.
            log.debug( 'Register size increasing from adding new field, {0}'.format( self[ 'name' ] ) )

            newSizeChangeMemoryUnits = math.ceil(
                float( proposedRegisterExtent - self.sizeBits ) / self.__memory.memoryUnitBits )
            newSizeMemoryUnits = self.__elementSizeMemoryUnits.value + newSizeChangeMemoryUnits
            finalSize = self.__coreData[ 'constraints' ].value.applySizeConstraints( newSizeMemoryUnits )

            self.__elementSizeMemoryUnits.value = finalSize
            self.__sizeChangeMade = True


    def __reviewFieldSize( self, existingField, fieldInterval ) :
        # A field interval defines the bits in the field being assigned.
        # The max of the interval indicates the extent of the field.
        # If the extent from the interval is greater than the current field size (extent) then the field must be resized.
        proposedFieldExtent = max( fieldInterval ) + 1
        if proposedFieldExtent > existingField.sizeBits :
            log.debug( 'Existing field size increasing with new interval, {0}'.format( existingField[ 'name' ] ) )
            existingField[ 'size' ] = proposedFieldExtent

            existingField.sizeChangeNotifier.notifyObservers()


    def fieldExists( self, name ) :
        fieldInData = name in self.__coreData[ 'fields' ].value

        return fieldInData


    def __getitem__( self, item ) :
        if item in self.__coreData :
            value = self.__coreData[ item ].value
        elif item in self.__userData :
            value = self.__userData[ item ].value
        else :
            raise KeyError( 'Register parameter not in core or user data, {0} ({1})'.format( item, self.canonicalId ) )

        return value


    def __setitem__( self, key, value ) :
        if key in self.__coreData :
            self.__coreData[ key ].validate( value )

            self.__coreData[ key ].value = value
        else :
            assert not key.startswith( '_' )

            # Assume user data
            log.info( 'Creating register user defined parameter, {0}={1} ({2})'.format( key, value, self.canonicalId ) )

            self.__userData[ key ] = Parameter( name = key,
                                                value = value )
        # Assume that any change events in bit fields or constraints will be taken care of using registered observers
        # of the relevant objects.


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace, setCollection,
                       optional = False,
                       parent = None ) :

        register = cls( memorySpace, setCollection,
                        parent = parent )

        goodResult = register.__decodeRegister( yamlData,
                                                optional = optional )

        if (not goodResult) \
                and (not optional) :
            raise ParseError( 'Error parsing Register YAML data' )

        return register


    def __decodeRegister( self, yamlData,
                          optional = True ) :
        def acquireFields( thisData ) :
            nonlocal self
            self.__coreData[ 'fields' ] = BitFieldsParameter.from_yamlData( thisData,
                                                                            optional = True,
                                                                            parent = self )

            for field in self.__coreData[ 'fields' ].value.values() :
                self.__setCollection.fieldSet.add( field )


        def acquireBitMap( thisData ) :
            """
            Acquire the register to field bit interval mapping from YAML data.

            :param thisData: Register YAML data
            """
            nonlocal self

            try :
                for thisIntervalData in thisData[ 'bitmap' ] :
                    sourceRangeData = thisIntervalData[ 'source' ]
                    destinationRangeData = thisIntervalData[ 'destination' ]
                    destinationId = thisIntervalData[ 'destinationId' ]

                    foundObjects = [ x for x in self.__setCollection.fieldSet if x.canonicalId == destinationId ]

                    if len( foundObjects ) == 0 :
                        raise ParseError(
                            'Destination element not found in destination set, {0}'.format( destinationId ) )

                    assert len( foundObjects ) == 1

                    sourceRange = BitRange.from_yamlData( { 'range' : sourceRangeData } )
                    destinationRange = BitRange.from_yamlData( { 'range' : destinationRangeData } )

                    self.__createFieldToRegisterMapping( foundObjects[ 0 ],
                                                         list( sourceRange.value ),
                                                         list( destinationRange.value ) )

            except KeyError as e :
                raise ParseError( 'Mapping not specified in YAML' ) from e


        def acquireConstraints( thisData ) :
            nonlocal self
            self.__coreData[ 'constraints' ] = ConstraintsParameter.from_yamlData( thisData, self.__memory,
                                                                                   optional = True )
            self.__registerConstraintNotifiers()


        def acquireDescription( thisData ) :
            nonlocal self
            self.__coreData[ 'description' ] = Parameter.from_yamlData( thisData, 'description',
                                                                        optional = True )


        def acquireMode( thisData ) :
            nonlocal self
            self.__coreData[ 'mode' ] = ModeParameter.from_yamlData( thisData,
                                                                     optional = True )


        def acquireName( thisData ) :
            nonlocal self
            self.__coreData[ 'name' ] = Parameter.from_yamlData( thisData, 'name',
                                                                 optional = False )


        def acquirePublic( thisData ) :
            nonlocal self
            self.__coreData[ 'public' ] = PublicParameter.from_yamlData( thisData,
                                                                         optional = True )


        def acquireSummary( thisData ) :
            nonlocal self
            self.__coreData[ 'summary' ] = Parameter.from_yamlData( thisData, 'summary',
                                                                    optional = True )


        def acquireUserDefinedParameters( thisData ) :
            nonlocal self

            for name, value in thisData.items() :
                # Only add user defined parameters if the YAML item is not in core data and doesn't begin with '_'
                # '_' are ready only data that should always be ignored on import.
                if (name not in self.__coreData) \
                        and (not name.startswith( '_' )) :
                    self.__userData[ name ] = Parameter( name = name,
                                                         value = value )


        def getParameters( thisData ) :
            acquireConstraints( thisData )
            acquireDescription( thisData )
            acquireMode( thisData )
            acquireName( thisData )
            acquirePublic( thisData )
            acquireSummary( thisData )

            # Field acquisition must be done after the basic register data is acquired.
            acquireFields( thisData )

            # BitMap acquisition must come after the other parameters because it uses those parameters as part of the set up.
            acquireBitMap( thisData )

            acquireUserDefinedParameters( thisData )

            # Legacy artifact of not using exceptions to signal problems.
            return True


        return complexParameter( yamlData, Register.__YAML_NAME, getParameters,
                                 optional = optional )


    def __encodeCoreParameters( self ) :
        """
        Encode Register core parameters ready for use with yaml.dump.

        :return: List of encoded parameters.
        """

        encodedParameters = list()
        encodedParameters.append( parameter( '_sizeMemoryUnits', self.sizeMemoryUnits ) )

        for parameterData in self.__coreData.values() :
            parameterYamlData = parameterData.to_yamlData()
            encodedParameters.append( parameterYamlData )

        encodedParameters.append( self.__bitMap.to_yamlData() )

        return encodedParameters


    def __encodeUserParameters( self ) :
        """
        Encode Register user parameters ready for use with yaml.dump.

        :return: List of encoded parameters.
        """
        encodedParameters = list()

        for parameterData in self.__userData.values() :
            parameterYamlData = parameterData.to_yamlData()
            encodedParameters.append( parameterYamlData )

        return encodedParameters


    def to_yamlData( self ) :
        yamlData = { self.__YAML_NAME : { } }

        coreParameters = self.__encodeCoreParameters()
        userParameters = self.__encodeUserParameters()

        parameters = coreParameters + userParameters

        for thisParameter in parameters :
            yamlData[ self.__YAML_NAME ].update( thisParameter )

        return yamlData
