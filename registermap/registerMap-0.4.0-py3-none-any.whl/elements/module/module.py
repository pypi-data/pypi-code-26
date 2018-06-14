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

from registerMap.exceptions import \
    ConfigurationError, \
    ParseError
from registerMap.structure.memory.element import \
    AddressableMemoryElement, \
    Size
from registerMap.utility.io.yaml.parameters.encode import parameter
from registerMap.utility.io.yaml.parameters.parse import complexParameter
from registerMap.utility.observer import \
    AddressChangeObserver, \
    Observable, \
    SizeChangeObserver

from ..base import \
    IdentityElement, \
    AddressObservableInterface, \
    SizeObservableInterface
from ..base.parameter import \
    ConstraintsParameter, \
    Parameter
from ..register import RegisterInstance

from .interface import ModuleInterface
from .parameters import RegistersParameter


log = logging.getLogger( __name__ )


class Module( ModuleInterface,
              IdentityElement,
              AddressObservableInterface,
              SizeObservableInterface ) :
    __DEFAULT_INSTANCES = 1
    __DEFAULT_MODULE_SIZE = 0
    __YAML_NAME = 'module'


    def __init__( self, memorySpace, setCollection ) :
        super().__init__()

        self.addressChangeNotifier = Observable()
        self.sizeChangeNotifier = Observable()

        self.__addressObserver = AddressChangeObserver( self )
        self.__sizeObserver = SizeChangeObserver( self )
        self.__setCollection = setCollection

        self.__memory = memorySpace
        self.__previousModule = None

        # __element initialisation must be done before __coreData initialisation because it is needed by
        # RegistersParameter.
        self.__initialiseElements()
        self.__coreData = {
            'constraints' : ConstraintsParameter( self.__memory ),
            'description' : Parameter( 'description', '' ),
            'instances' : Parameter( 'instances', self.__DEFAULT_INSTANCES ),
            'name' : Parameter( 'name', None ),
            'registers' : RegistersParameter( self ),
            'summary' : Parameter( 'summary', '' ),
        }
        self.__coreData[ 'registers' ].addObserver( self.__sizeObserver )
        self.__coreData[ 'instances' ].addObserver( self.__sizeObserver )

        self.__userData = dict()

        self.__registerConstraintNotifiers()


    def __initialiseElements( self ) :
        # Must be the same as __coreData['instances'] but cannot reference that directly because it does not exist yet.
        # Assume the module instances are uniform size, for now.
        self.__moduleInstanceSize = Size()
        self.__moduleInstanceSize.value = self.__DEFAULT_MODULE_SIZE

        self.__element = { x : AddressableMemoryElement( self.__memory, sizeObject = self.__moduleInstanceSize )
                           for x in range( self.__DEFAULT_INSTANCES ) }


    def __registerConstraintNotifiers( self ) :
        self.__memory.addressChangeNotifier.addObserver( self.__addressObserver )

        self.__coreData[ 'constraints' ].value.addressChangeNotifier.addObserver( self.__addressObserver )
        self.__coreData[ 'constraints' ].value.sizeChangeNotifier.addObserver( self.__sizeObserver )


    @property
    def assignedMemoryUnits( self ) :
        """
        :return: The number of memory units currently consumed by registers.
        """
        totalSize = 0
        for register in self.__coreData[ 'registers' ].value.values() :
            totalSize += register.sizeMemoryUnits

        return totalSize


    @property
    def baseAddress( self ) :
        """
        Address of the first register of the module (the "base" address of the module), or the fixed address if a
        'fixedAddress' constraint is applied.
        """
        return self.__element[ 0 ].startAddress


    @property
    def canonicalId( self ) :
        canonicalName = self.__coreData[ 'name' ].value

        return canonicalName


    @property
    def endAddress( self ) :
        """
        The last address of the last module instance.
        """
        maxIndex = max( self.__element.keys() )
        return self.__element[ maxIndex ].endAddress


    @property
    def memory( self ) :
        """
        :return: Module local alias of for the memory space definitions of the register map.
        """
        return self.__memory


    @property
    def offset( self ) :
        """
        :return: The offset of the module relative to the base address of the register map.
        """
        return self.baseAddress - self.__memory.baseAddress


    @property
    def previousElement( self ) :
        """
        :return: The module preceding this module in memory.
        """
        return self.__previousModule


    @previousElement.setter
    def previousElement( self, value ) :
        self.__previousModule = value
        # If the previous module changes address or size, then these events could both impact the address of the
        # current register.
        self.__previousModule.sizeChangeNotifier.addObserver( self.__addressObserver )
        self.__previousModule.addressChangeNotifier.addObserver( self.__addressObserver )

        self.reviewAddressChange()


    @property
    def spanMemoryUnits( self ) :
        """
        :return: The current number of memory units spanned by the registers in the module.
        """
        return self.__calculateTotalSpan()


    def addRegister( self, name ) :
        """
        Create a new register of the specified name to be added to the module.

        :param name: Name of the register.
        :return: The added register.
        """
        register = RegisterInstance( self.__memory,
                                     parent = self,
                                     setCollection = self.__setCollection )
        register[ 'name' ] = name
        self.__validateAddedRegister( register )

        # Don't add the register until all the checks have passed
        self.__setCollection.registerSet.add( register )
        self.__coreData[ 'registers' ].value[ register[ 'name' ] ] = register

        log.debug( 'Notifying on register change in module' )
        self.reviewSizeChange()

        return register


    def __validateAddedRegister( self, register ) :
        def checkSpan() :
            currentSpan = self.__calculateRegisterOnlySingleModuleSpan()
            if currentSpan is not None :
                newSpan = currentSpan + register.sizeMemoryUnits
                constrainedSize = self.__coreData[ 'constraints' ].value.applySizeConstraints( newSpan )

                if constrainedSize < newSpan :
                    raise ConfigurationError(
                        'Adding new register breaks fixed size constraint, {0}'.format( register.canonicalId ) )


        def checkUniqueName() :
            foundRegisters = [ x[ 'name' ] for x in self.__coreData[ 'registers' ].value.values()
                               if x[ 'name' ] == register[ 'name' ] ]

            if len( foundRegisters ) != 0 :
                raise ConfigurationError(
                    'Created register names must be unique within a module, {0}'.format( register[ 'name' ] ) )


        checkUniqueName()
        checkSpan()


    def reviewSizeChange( self ) :
        numberInstances = self.__coreData[ 'instances' ].value
        if len( self.__element ) != numberInstances :
            # Number of instances has changed.
            # Can only increase the size, for now.
            assert self.__coreData[ 'instances' ].value > len( self.__element )

            for x in range( len( self.__element ), numberInstances ) :
                self.__element[ x ] = AddressableMemoryElement( self.__memory,
                                                                sizeObject = self.__moduleInstanceSize )

        newSpan = self.__calculateSingleModuleSpan()
        if newSpan != self.__moduleInstanceSize :
            self.__moduleInstanceSize.value = newSpan
            self.sizeChangeNotifier.notifyObservers()


    def reviewAddressChange( self ) :
        def updateFirstRegister() :
            nonlocal self

            if self.__coreData[ 'registers' ].firstElement is not None :
                self.__coreData[ 'registers' ].firstElement.endAddress = newStartAddress - 1


        newStartAddress = self.__calculateStartAddress()
        if (newStartAddress is not None) \
                and (newStartAddress != self.__element[ 0 ].startAddress) :
            self.__element[ 0 ].startAddress = newStartAddress
            updateFirstRegister()
            self.reviewSizeChange()

            self.addressChangeNotifier.notifyObservers()


    def __recalculateInstanceStartAddresses( self, singleInstanceSize ) :
        assert (len( self.__element ) == self.__coreData[ 'instances' ].value), \
            'Number of instances defined and instances realized is not the same'

        for index in range( 0, (len( self.__element ) - 1) ) :
            nextInstanceStartAddress = self.__coreData[ 'constraints' ].value.applyAddressConstraints(
                self.__element[ index ].startAddress + singleInstanceSize )

            self.__element[ index + 1 ].startAddress = nextInstanceStartAddress


    def __calculateStartAddress( self ) :
        if (self.__previousModule is not None) and (self.__previousModule.endAddress is not None) :
            # Page register impact is calculate before application of constraints. This means that constraints could
            # still affect the address. eg. if address alignment modified the affect of page register on the address.
            proposedAddress = self.__previousModule.endAddress + 1
            initialAddress = self.__memory.calculatePageRegisterImpact( proposedAddress )
        else :
            initialAddress = None

        newAddress = self.__coreData[ 'constraints' ].value.applyAddressConstraints( initialAddress )
        return newAddress


    def __calculateTotalSpan( self ) :
        singleModuleSpan = self.__calculateSingleModuleSpan()

        if (singleModuleSpan is not None) \
                and (singleModuleSpan > self.__DEFAULT_MODULE_SIZE) :
            self.__recalculateInstanceStartAddresses( singleModuleSpan )

            maxIndex = max( self.__element.keys() )
            finalSize = self.__element[ maxIndex ].endAddress - self.__element[ 0 ].startAddress + 1
        else :
            finalSize = self.__DEFAULT_MODULE_SIZE

        return finalSize


    def __calculateSingleModuleSpan( self ) :
        """
        Calculate the span of a single module including size constraints.
        """
        singleInstanceSize = self.__calculateRegisterOnlySingleModuleSpan()
        singleModuleSpan = self.__coreData[ 'constraints' ].value.applySizeConstraints( singleInstanceSize )

        return singleModuleSpan


    def __calculateRegisterOnlySingleModuleSpan( self ) :
        """
        Calculate the span of a single module for registers only (no size constraints).

        Assume all module are identical and do the calculation on the first module only.

        :return: number of memory units spanned.
        """


        def sizeCalculationWithAddresses() :
            nonlocal self

            # Module size is the difference between the address of the first memory unit and the last memory unit
            # consumed by the last register
            startAddress = self.__element[ 0 ].startAddress
            endAddress = startAddress

            if len( self.__coreData[ 'registers' ].value ) == 0 :
                totalRegisterSpan = 0
            else :
                for register in self.__coreData[ 'registers' ].value.values() :
                    if (register.endAddress is not None) and (register.endAddress > endAddress) :
                        endAddress = register.endAddress
                    elif register.endAddress is None :
                        log.debug(
                            'Register has None end address during span calculation, ' + repr( register[ 'name' ] ) )

                totalRegisterSpan = endAddress - startAddress + 1

            return totalRegisterSpan


        if self.__element[ 0 ].startAddress is not None :
            moduleRegisterSpan = sizeCalculationWithAddresses()
        else :
            moduleRegisterSpan = None

        return moduleRegisterSpan


    def __getitem__( self, item ) :
        if item in self.__coreData :
            value = self.__coreData[ item ].value
        elif item in self.__userData :
            value = self.__userData[ item ].value
        else :
            raise KeyError( 'Module parameter not in core or user data, {0} ({1})'.format( item, self.canonicalId ) )
        return value


    def __setitem__( self, key, value ) :
        if key in self.__coreData :
            self.__coreData[ key ].value = value
        else :
            assert not key.startswith( '_' )

            log.info( 'Creating user defined module parameter, {0}={1} ({2})'.format( key, value, self.canonicalId ) )
            self.__userData[ key ] = Parameter( name = key, value = value )

        # Assume that any change events in registers or constraints will be taken care of using registered observers of
        # the relevant objects.


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace, setCollection,
                       optional = False ) :

        module = cls( memorySpace, setCollection )
        setCollection.moduleSet.add( module )

        goodResult = module.__decodeModule( yamlData, optional )

        if (not optional) \
                and (not goodResult) :
            raise ParseError( 'Error parsing Module YAML data' )

        return module


    def __decodeModule( self, yamlData, optional ) :

        def acquireConstraints( thisData ) :
            nonlocal self
            self.__coreData[ 'constraints' ] = ConstraintsParameter.from_yamlData( thisData, self.__memory,
                                                                                   optional = True )
            self.__registerConstraintNotifiers()


        def acquireDescription( thisData ) :
            nonlocal self
            self.__coreData[ 'description' ] = Parameter.from_yamlData( thisData, 'description',
                                                                        optional = True )


        def acquireName( thisData ) :
            nonlocal self
            self.__coreData[ 'name' ] = Parameter.from_yamlData( thisData, 'name',
                                                                 optional = False )


        def acquireRegisters( thisData ) :
            nonlocal self
            self.__coreData[ 'registers' ] = RegistersParameter.from_yamlData(
                thisData, self, self.__memory, self.__setCollection,
                optional = True,
                parent = self )


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
            acquireName( thisData )
            acquireRegisters( thisData )
            acquireSummary( thisData )

            acquireUserDefinedParameters( thisData )

            # Legacy artifact of not using exceptions to signal problems.
            return True


        return complexParameter( yamlData, Module.__YAML_NAME, getParameters,
                                 optional = optional )


    def __encodeCoreParameters( self ) :
        """
        Encode Module core parameters ready for use with yaml.dump.

        :return: List of encoded parameters.
        """
        encodedParameters = list()
        encodedParameters.append( parameter( '_address', self.baseAddress ) )
        encodedParameters.append( parameter( '_spanMemoryUnits', self.spanMemoryUnits ) )

        for parameterData in self.__coreData.values() :
            parameterYamlData = parameterData.to_yamlData()
            encodedParameters.append( parameterYamlData )

        return encodedParameters


    def __encodeUserParameters( self ) :
        """
        Encode Module user parameters ready for use with yaml.dump.

        :return: List of encoded parameters.
        """
        encodedParameters = list()
        for parameterData in self.__userData.values() :
            parameterYamlData = parameterData.to_yamlData()
            encodedParameters.append( parameterYamlData )

        return encodedParameters


    def to_yamlData( self ) :
        """
        Encode Module ready for use with yaml.dump.

        :return: Encoded YAML data structure
        """
        yamlData = { self.__YAML_NAME : { } }

        coreParameters = self.__encodeCoreParameters()
        userParameters = self.__encodeUserParameters()

        parameters = coreParameters + userParameters

        for thisParameter in parameters :
            yamlData[ self.__YAML_NAME ].update( thisParameter )

        return yamlData
