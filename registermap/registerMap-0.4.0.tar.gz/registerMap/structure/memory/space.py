"""
Define register map memory space parameters. These parameters typically relate to physical properties of underlying hardware.
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

import math

import registerMap.utility.io.yaml.parameters.encode as rye
import registerMap.utility.io.yaml.parameters.parse as ryp
import registerMap.utility.observer as rmo

from registerMap.utility.io import yaml

from registerMap.exceptions import ConfigurationError, ParseError


class MemorySpace( yaml.Export, yaml.Import ) :
    def __init__( self ) :
        super().__init__()

        self.addressChangeNotifier = rmo.Observable()
        self.sizeChangeNotifier = rmo.Observable()

        self.__baseAddress = 0
        self.__addressBits = 32
        self.__memoryUnitBits = 8
        self.__pageSize = None

        self.__maximumMemoryAddress = pow( 2, self.__addressBits )


    @property
    def addressBits( self ) :
        """
        :return: The maximum number of bits for register map addresses.
        :default: 32
        """
        return self.__addressBits


    @addressBits.setter
    def addressBits( self, value ) :
        if (not isinstance( value, int )) or (value < 1) :
            raise ConfigurationError( 'Memory address bits must be specified as positive non-zero integer' )

        maximumMemoryAddress = pow( 2, value )
        if maximumMemoryAddress < self.__baseAddress :
            raise ConfigurationError( 'Addressable memory must be greater than the base address, '
                                      + hex( maximumMemoryAddress ) + ' < '
                                      + hex( self.__baseAddress ) )

        self.__addressBits = value
        self.__maximumMemoryAddress = maximumMemoryAddress

        if self.__pageSize is not None :
            self.addressChangeNotifier.notifyObservers( arguments = 'addressBits' )


    @property
    def baseAddress( self ) :
        """
        :return: The address of offset zero in the register map; the first address location.
        :default: 0x0
        """
        return self.__baseAddress


    @baseAddress.setter
    def baseAddress( self, value ) :
        if (not isinstance( value, int )) \
                or (value < 0) :
            raise ConfigurationError( 'Base address must be specified as non-negative integer' )

        if value > self.__maximumMemoryAddress :
            raise ConfigurationError( 'Base address must be less than maximum addressable memory, '
                                      + hex( value ) + ' < ' + hex( self.__maximumMemoryAddress ) )

        self.__baseAddress = value

        self.addressChangeNotifier.notifyObservers( arguments = 'baseAddress' )


    @property
    def maximumMemoryAddress( self ) :
        return self.__maximumMemoryAddress


    @property
    def memoryUnitBits( self ) :
        """
        :return: The maximum number of bits for a register map location.
        :default: 8
        """
        return self.__memoryUnitBits


    @memoryUnitBits.setter
    def memoryUnitBits( self, value ) :
        if (not isinstance( value, int )) or (value < 1) :
            raise ConfigurationError( 'Memory unit bits must be specified as positive non-zero integer' )

        self.__memoryUnitBits = value

        if self.__pageSize is not None :
            self.addressChangeNotifier.notifyObservers( arguments = 'memoryUnitBits' )


    @property
    def pageSize( self ) :
        """
        By default, paging is disabled and pageSize is None.

        If paging is enabled, then the last N bits of the page are reserved for page addressing, where N is equal to
        memoryAddressBits.

        :return: The maximum number of memory units in a page.
        :default: None
        """
        return self.__pageSize


    @pageSize.setter
    def pageSize( self, newPageSize ) :
        if (newPageSize is not None) and (not isinstance( newPageSize, int )) :
            raise ConfigurationError( 'Page size must be specified as integer' )
        elif newPageSize is None :
            self.__pageSize = None
        else :
            # Must be an integer
            pageRegisterReservedUnits = self.__calculateNumberPageRegisters()
            if (newPageSize - pageRegisterReservedUnits) < 0 :
                raise ConfigurationError( 'Bad page size, ' + repr( newPageSize ) )

            self.__pageSize = newPageSize

        self.addressChangeNotifier.notifyObservers( arguments = 'pageSize' )


    def __calculateNumberPageRegisters( self ) :
        pageRegisterReservedUnits = math.ceil( float( self.__addressBits ) / self.__memoryUnitBits )
        return pageRegisterReservedUnits


    def __calculatePageRegisterOffsets( self ) :
        pageRegisterOffsets = None
        if self.__pageSize is not None :
            numberPageRegisters = self.__calculateNumberPageRegisters()
            pageRegisterOffsets = list()
            for offset in range( numberPageRegisters, 0, -1 ) :
                pageRegisterOffsets.append( self.__pageSize - offset )
        return pageRegisterOffsets


    def calculatePageRegisterImpact( self, proposedAddress ) :
        if self.__pageSize is not None :
            if self.isPageRegister( proposedAddress ) :
                # Propose the first address of the next page.
                proposedAddress = self.pageBaseAddress( proposedAddress ) + self.__pageSize

        return proposedAddress


    def isPageRegister( self, address ) :
        """
        Determine if specified address is a page register.

        Always returns False if page size is not specified.

        :param address: Address to be evaluated
        :return: True if address is a page register.
        """
        result = False
        if self.__pageSize is not None :
            pageRegisterOffsets = self.__calculatePageRegisterOffsets()

            if (address % self.__pageSize) in pageRegisterOffsets :
                result = True

        return result


    def pageBaseAddress( self, address ) :
        """
        Determine base address of page for specfied address.

        :param address:
        :return: Page base address, or None if page size is not specified.
        """
        thisPageBaseAddress = None
        if self.__pageSize is not None :
            thisPageBaseAddress = math.floor( float( address ) / self.__pageSize ) * self.__pageSize
        return thisPageBaseAddress


    @classmethod
    def from_yamlData( cls, yamlData ) :
        memorySpace = cls()
        goodResult = memorySpace.__decodeMemorySpace( yamlData )

        if not goodResult :
            raise ParseError( 'Processing memory space data failed. Check log for details. ' + repr( yamlData ) )

        return memorySpace


    def __decodeMemorySpace( self, yamlData ) :
        def recordBaseAddress( value ) :
            nonlocal self
            self.__baseAddress = value


        def recordAddressBits( value ) :
            nonlocal self
            self.__addressBits = value


        def recordMemoryUnitBits( value ) :
            nonlocal self
            self.__memoryUnitBits = value


        def recordPageSizeMemoryUnits( value ) :
            nonlocal self
            self.__pageSize = value


        def getParameters( thisData ) :
            thisGoodResult = ryp.integerParameter( thisData, 'baseAddress', recordBaseAddress,
                                                   optional = True )
            thisGoodResult &= ryp.integerParameter( thisData, 'addressBits', recordAddressBits,
                                                    optional = True )
            thisGoodResult &= ryp.integerParameter( thisData, 'memoryUnitBits', recordMemoryUnitBits,
                                                    optional = True )
            thisGoodResult &= ryp.integerParameter( thisData, 'pageSizeMemoryUnits', recordPageSizeMemoryUnits,
                                                    optional = True,
                                                    noneValid = True )

            return thisGoodResult


        keyName = 'memorySpace'

        return ryp.complexParameter( yamlData, keyName, getParameters )


    def to_yamlData( self ) :
        parameters = [ rye.parameter( 'baseAddress', rye.HexInt( self.__baseAddress ) ),
                       rye.parameter( 'addressBits', self.__addressBits ),
                       rye.parameter( 'memoryUnitBits', self.__memoryUnitBits ),
                       rye.parameter( 'pageSizeMemoryUnits', self.__pageSize ) ]

        keyName = 'memorySpace'
        yamlData = { keyName : { } }

        for thisParameter in parameters :
            yamlData[ keyName ].update( thisParameter )

        return yamlData
