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
from registerMap.utility.observer import Observable, SizeChangeObserver

from .interface import AddressableElementInterface


class Size( Observable ) :
    """
    Express the size of a memory element. Notify observers when the size changes.
    """


    def __init__( self ) :
        super().__init__()

        self._value = None


    @property
    def value( self ) :
        return self._value


    @value.setter
    def value( self, v ) :
        self._value = v
        self.notifyObservers()


class AddressableMemoryElement( AddressableElementInterface ) :
    """
    Basic address and size properties of a memory element.
    """
    __DEFAULT_SIZE = 1


    def __init__( self, memory,
                  startAddress = None,
                  endAddress = None,
                  sizeMemoryUnits = None,
                  sizeObject = None ) :
        self.__memory = memory

        if (endAddress is not None) and (sizeMemoryUnits is not None) :
            raise ConfigurationError(
                'Cannot specify both endAddress and sizeMemoryUnits, {0}, {1}'.format(
                    endAddress, sizeMemoryUnits ) )

        self.__sizeObserver = SizeChangeObserver( self )

        if sizeObject is not None :
            self.__sizeMemoryUnits = sizeObject
        else :
            self.__sizeMemoryUnits = Size()

        self.__sizeMemoryUnits.addObserver( self.__sizeObserver )

        self.__startAddress = startAddress
        if startAddress is None :
            self.__endAddress = None
            if sizeObject is None :
                self.__sizeMemoryUnits.value = self.__DEFAULT_SIZE
        else :
            # Assume the start address is numerical
            # If a sizeObject is specified, assume that it's size is valid.
            if endAddress is not None :
                self.__evaluateSizeFromEndAddressChange( endAddress )
            elif sizeMemoryUnits is not None :
                self.__evaluateEndAddressFromSizeChange( sizeMemoryUnits )
            elif sizeObject is None :
                # both endAddress and sizeMemoryUnits must be None
                self.__endAddress = self.__startAddress
                self.__sizeMemoryUnits.value = self.__DEFAULT_SIZE


    def __evaluateEndAddressFromSizeChange( self, newSize ) :
        """
        Adjust end address assuming the start address is constant.

        :param newSize:
        """
        if newSize is None :
            self.__endAddress = None
        elif self.__startAddress is not None :
            self.__endAddress = self.__startAddress + newSize - 1

        self.__updateProtectedSizeValue( newSize )


    def __evaluateEndAddressFromStartAddressChange( self, newAddress ) :
        """
        Adjust end address assuming the size is constant.

        :param newAddress:
        """
        if newAddress is None :
            self.__endAddress = None
        elif self.__sizeMemoryUnits.value is not None :
            self.__endAddress = newAddress + self.__sizeMemoryUnits.value - 1

        self.__startAddress = newAddress


    def __updateProtectedSizeValue( self, newSize ) :
        # Use the protected member instead of the .value property in order to avoid recursion loops via size change
        # notification.
        self.__sizeMemoryUnits._value = newSize


    def __evaluateStartAddressFromSizeChange( self, newSize ) :
        """
        Adjust start address assuming the end address is constant.

        :param newSize:
        """
        if newSize is None :
            self.__startAddress = None
        elif self.__endAddress is not None :
            self.__startAddress = self.__endAddress - newSize + 1

        self.__updateProtectedSizeValue( newSize )


    def __evaluateStartAddressFromEndAddressChange( self, newAddress ) :
        """
        Adjust start address assuming the size is constant.

        :param newAddress:
        """
        if newAddress is None :
            self.__endAddress = None
        elif self.__sizeMemoryUnits.value is not None :
            self.__startAddress = newAddress - self.__sizeMemoryUnits.value + 1

        self.__endAddress = newAddress


    def __evaluateSizeFromStartAddressChange( self, newAddress ) :
        """
        Adjust size assuming the end address is constant.

        :param newAddress:
        """
        if newAddress is None :
            self.__startAddress = None
        elif self.__endAddress is not None :
            self.__sizeMemoryUnits.value = self.__endAddress - newAddress + 1

        self.__startAddress = newAddress


    def __evaluateSizeFromEndAddressChange( self, newAddress ) :
        """
        Adjust size assuming the start address is constant.

        :param newAddress:
        """
        if newAddress is None :
            self.__startAddress = None
        elif self.__startAddress is not None :
            self.__sizeMemoryUnits.value = newAddress - self.__startAddress + 1

        self.__endAddress = newAddress


    @property
    def offset( self ) :
        """
        Address offset relative to the memory space base address.
        """
        if self.__startAddress is None :
            offset = None
        else :
            offset = self.__startAddress - self.__memory.baseAddress

        return offset


    @property
    def startAddress( self ) :
        """
        The start address of the element, corresponding to the lowest numerical value of the addresses spanned by the element.
        """
        return self.__startAddress


    @startAddress.setter
    def startAddress( self, value ) :
        # Assume the size is fixed and adjust the end address.
        self.__evaluateEndAddressFromStartAddressChange( value )


    @property
    def endAddress( self ) :
        """
        The end address of the element, corresponding to the highest numerical value of the addresses spanned by the element.
        """
        return self.__endAddress


    @endAddress.setter
    def endAddress( self, value ) :
        if self.__startAddress is None :
            raise ConfigurationError( 'Must define start address before attempting to define end address' )
        else :
            # Assume the start address is fixed and adjust the size.
            self.__evaluateSizeFromEndAddressChange( value )


    @property
    def size( self ) :
        """
        Access the Size object stored in the memory element.
        """
        return self.__sizeMemoryUnits


    @property
    def sizeMemoryUnits( self ) :
        """
        Number of memory units spanned by the element.
        """
        return self.__sizeMemoryUnits.value


    @sizeMemoryUnits.setter
    def sizeMemoryUnits( self, value ) :
        # Assume the start address is fixed and adjust the end address.
        self.__evaluateEndAddressFromSizeChange( value )


    def reviewSizeChange( self ) :
        self.__evaluateEndAddressFromSizeChange( self.__sizeMemoryUnits.value )
