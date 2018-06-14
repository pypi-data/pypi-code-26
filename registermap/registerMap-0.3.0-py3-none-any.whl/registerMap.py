"""
Definition of RegisterMap
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

from .base.parameters import \
    ElementsParameter, \
    ModulesParameter

from .elements.base.parameter import Parameter
from .elements.module import Module

from .exceptions import \
    ConfigurationError, \
    ParseError

from .set import SetCollection

from .structure.memory.element import AddressableMemoryElement
from .structure.memory.space import MemorySpace

from .utility.observer import AddressChangeObserver


log = logging.getLogger( __name__ )


class RegisterMap :
    __yamlName = 'registerMap'


    def __init__( self ) :
        self.__addressObserver = AddressChangeObserver( self )

        self.setCollection = SetCollection()
        self.__initializeMemorySpace()
        self.__initializeElement()

        self.__data = {
            'description' : Parameter( 'description', '' ),
            'element' : ElementsParameter( self ),
            'modules' : ModulesParameter( self ),
            'summary' : Parameter( 'summary', '' )
        }
        self.__sizeObserver = self.__data[ 'modules' ].sizeObserver
        self.__memorySpace.sizeChangeNotifier.addObserver( self.__sizeObserver )


    def __initializeElement( self ) :
        self.__element = AddressableMemoryElement( self.__memorySpace )
        self.__element.startAddress = self.__memorySpace.baseAddress
        self.__element.sizeMemoryUnits = None


    def __initializeMemorySpace( self ) :
        self.__memorySpace = MemorySpace()
        self.__memorySpace.addressChangeNotifier.addObserver( self.__addressObserver )


    @property
    def assignedMemoryUnits( self ) :
        """
        :return: Total number of memory units assigned a definition via a register.
        """
        totalSize = 0
        for thisModule in self.__data[ 'modules' ].value.values() :
            totalSize += thisModule.assignedMemoryUnits

        return totalSize


    @property
    def memory( self ) :
        return self.__memorySpace


    @property
    def spanMemoryUnits( self ) :
        return self.__element.sizeMemoryUnits


    @property
    def startAddress( self ) :
        return self.__element.startAddress


    def addModule( self, name ) :
        """
        Create a module with the specified name.

        :param name: Name of the new module.

        :return: The created module.
        """
        thisModule = Module( self.__memorySpace, self.setCollection )
        self.setCollection.moduleSet.add( thisModule )
        thisModule[ 'name' ] = name
        self.__validateAddedModule( thisModule )

        self.__data[ 'modules' ].value[ thisModule[ 'name' ] ] = thisModule

        log.debug( 'Notifying on module change in register map' )
        self.reviewSizeChange()

        return thisModule


    def __validateAddedModule( self, module ) :
        foundModules = [ x[ 'name' ] for x in self.__data[ 'modules' ].value.values() if
                         x[ 'name' ] == module[ 'name' ] ]

        if len( foundModules ) != 0 :
            raise ConfigurationError(
                'Created module names must be unique within a register map, ' + repr( module[ 'name' ] ) )


    def reviewAddressChange( self ) :
        """
        Propagate a memory space base address change.
        """
        if self.__data[ 'modules' ].firstElement is not None :
            self.__data[ 'modules' ].firstElement.endAddress = self.__memorySpace.baseAddress - 1


    def reviewSizeChange( self ) :
        startAddress = self.__memorySpace.baseAddress
        endAddress = startAddress
        registersCreated = False
        for thisModule in self.__data[ 'modules' ].value.values() :
            if thisModule.endAddress > endAddress :
                endAddress = thisModule.endAddress

            if len( thisModule[ 'registers' ] ) > 0 :
                registersCreated = True

        if (endAddress == startAddress) and (not registersCreated) :
            self.__element.sizeMemoryUnits = 0
        elif (endAddress == startAddress) and registersCreated :
            self.__element.sizeMemoryUnits = 1
        else :
            self.__element.sizeMemoryUnits = endAddress - startAddress + 1


    def __getitem__( self, item ) :
        return self.__data[ item ].value


    def __setitem__( self, key, value ) :
        self.__data[ key ].value = value


    @classmethod
    def from_yamlData( cls, yamlData,
                       optional = False ) :
        def acquireMemorySpace( thisData ) :
            nonlocal thisMap
            thisMap.__memorySpace = MemorySpace.from_yamlData( thisData )
            thisMap.__memorySpace.sizeChangeNotifier.addObserver( thisMap.__sizeObserver )
            thisMap.__memorySpace.addressChangeNotifier.addObserver( thisMap.__addressObserver )


        def acquireDescription( thisData ) :
            nonlocal thisMap
            thisMap.__data[ 'description' ] = Parameter.from_yamlData( thisData, 'description',
                                                                       optional = True )


        def acquireModules( thisData ) :
            nonlocal thisMap
            thisMap.__data[ 'modules' ] = ModulesParameter.from_yamlData(
                thisData, thisMap, thisMap.__memorySpace, thisMap.setCollection,
                optional = True )


        def acquireSummary( thisData ) :
            nonlocal thisMap
            thisMap.__data[ 'summary' ] = Parameter.from_yamlData( thisData, 'summary',
                                                                   optional = True )


        thisMap = cls()
        if (not optional) and (cls.__yamlName not in yamlData.keys()) :
            raise ParseError( 'RegisterMap is not defined in yaml data' )
        elif cls.__yamlName in yamlData.keys() :
            # Memory space acquisition must occur first because it is used by module acquisition
            acquireMemorySpace( yamlData[ cls.__yamlName ] )

            acquireDescription( yamlData[ cls.__yamlName ] )
            acquireSummary( yamlData[ cls.__yamlName ] )

            acquireModules( yamlData[ cls.__yamlName ] )

            thisMap.reviewAddressChange()
            thisMap.reviewSizeChange()

        return thisMap


    def to_yamlData( self ) :
        yamlData = { self.__yamlName : { } }

        parameters = list()
        for parameterData in self.__data.values() :
            parameterYamlData = parameterData.to_yamlData()

            if parameterYamlData is not None :
                parameters.append( parameterYamlData )

        yamlData[ self.__yamlName ].update( self.__memorySpace.to_yamlData() )
        for thisParameter in parameters :
            yamlData[ self.__yamlName ].update( thisParameter )

        return yamlData


    def __len__( self ) :
        thisLength = len( self.setCollection.moduleSet ) \
                     + len( self.setCollection.registerSet ) \
                     + len( self.setCollection.fieldSet )

        return thisLength
