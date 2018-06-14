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

from registerMap.structure.memory.element import AddressableMemoryElement
from registerMap.utility.observer import \
    AddressChangeObserver, \
    SizeChangeObserver

from ..base.parameter import \
    ConstraintsParameter

from .interface import ModuleInterface


class ModuleInstance( ModuleInterface ) :
    """
    Maintainer of RegisterInstances within a module. In a series module - a Module with multiple instances - there is a
    one to one correspondence between instances and ModuleInstance.
    """
    __VALID_PARAMETERS = {
        'constraints',
    }

    __VALID_CONSTRAINTS = {
        'fixedAddress',
        'alignmentMemoryUnits',
    }


    def __init__( self, parent, memorySpace ) :
        super().__init__()

        self.__element = AddressableMemoryElement( parent.memory )
        self.__memory = memorySpace
        self.__parent = parent
        self.__previousElement = None

        self.__coreData = {
            'constraints' : ConstraintsParameter( self.__memory,
                                                  validConstraints = self.__VALID_CONSTRAINTS ),
        }


    @property
    def assignedMemoryUnits( self ) :
        return self.__parent.assignedMemoryUnits


    @property
    def baseAddress( self ) :
        if self.__previousElement.endAddress is not None :
            proposedValue = self.__previousElement.endAddress + 1
        else :
            proposedValue = None

        value = self.__coreData[ 'constraints' ].value.applyAddressConstraints( proposedValue )

        return value


    @property
    def canonicalId( self ) :
        # Append the instance base address to the parent module canonical id.
        value = '{0}[{1}]'.format( self.__parent.canonicalId, hex( self.baseAddress ) )
        return value


    @property
    def endAddress( self ) :
        pass


    @property
    def memory( self ) :
        return self.__memory


    @property
    def offset( self ) :
        value = self.baseAddress - self.memory.baseAddress

        return value


    @property
    def previousElement( self ) :
        return self.__previousElement


    @previousElement.setter
    def previousElement( self, value ) :
        self.__previousElement = value


    @property
    def spanMemoryUnits( self ) :
        pass


    def __getitem__( self, item ) :
        if item in self.__VALID_PARAMETERS :
            value = self.__coreData[ item ].value
        else :
            value = self.__parent[ item ]

        return value


    def __setitem__( self, key, value ) :
        if key in self.__VALID_PARAMETERS :
            self.__coreData[ key ].value = value
        else :
            self.__parent[ key ] = value
