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
from registerMap.utility.observer import Observable


class MockPreviousRegister :
    def __init__( self,
                  startAddress = None,
                  endAddress = None,
                  sizeMemoryUnits = None ) :
        self.sizeChangeNotifier = Observable()
        self.addressChangeNotifier = Observable()

        self.__address = startAddress
        if (endAddress is not None) and (startAddress is not None) :
            self.__endAddress = endAddress
            self.__sizeMemoryUnits = self.__endAddress - self.__address + 1
        elif (sizeMemoryUnits is not None) and (startAddress is not None) :
            self.__sizeMemoryUnits = sizeMemoryUnits
            self.__endAddress = self.__address + self.__sizeMemoryUnits - 1
        elif (sizeMemoryUnits is not None) and (endAddress is not None) :
            self.__endAddress = endAddress
            self.__sizeMemoryUnits = sizeMemoryUnits
            self.__address = self.__endAddress - self.__sizeMemoryUnits + 1
        elif (startAddress is None) and (sizeMemoryUnits is not None or endAddress is not None) :
            raise RuntimeError( 'Must specify address if specifying end address or size' )
        else :
            self.__sizeMemoryUnits = None
            self.__endAddress = None


    @property
    def address( self ) :
        return self.__address


    @address.setter
    def address( self, value ) :
        if self.__address is not None :
            addressChange = value - self.__address
            self.__address = value
            self.__endAddress += addressChange
        else :
            self.__address = value
            self.__endAddress = self.__address + self.__sizeMemoryUnits - 1

        self.addressChangeNotifier.notifyObservers()


    @property
    def endAddress( self ) :
        return self.__endAddress


    @endAddress.setter
    def endAddress( self, value ) :
        self.__endAddress = value
        # For the purpose of testing, assume that a change in end address always signals a size change.
        self.__sizeMemoryUnits = self.__endAddress - self.__address + 1
        self.sizeChangeNotifier.notifyObservers()


    @property
    def sizeMemoryUnits( self ) :
        return self.__sizeMemoryUnits


    @sizeMemoryUnits.setter
    def sizeMemoryUnits( self, value ) :
        self.__sizeMemoryUnits = value
        self.__endAddress = self.__address + self.__sizeMemoryUnits - 1
        self.sizeChangeNotifier.notifyObservers()