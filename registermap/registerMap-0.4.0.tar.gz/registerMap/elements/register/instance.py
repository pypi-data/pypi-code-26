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
from registerMap.utility.io import yaml
from registerMap.utility.io.yaml.parameters.encode import parameter
from registerMap.utility.observer import \
    AddressChangeObserver, \
    Observable, \
    SizeChangeObserver

from ..base import \
    AddressObservableInterface, \
    IdentityElement

from .interface import RegisterInterface
from .register import Register


class RegisterInstance( IdentityElement,
                        RegisterInterface,
                        AddressObservableInterface,
                        yaml.Export,
                        yaml.Import ) :
    """
    An instantiation of a register, which means assigning an address.

    Multiple RegisterInstance objects may refer to the same Register object.
    """


    def __init__( self, memorySpace,
                  parent = None,
                  register = None,
                  setCollection = None ) :
        super().__init__()

        self.addressChangeNotifier = Observable()

        self.__addressObserver = AddressChangeObserver( self )
        self.__memory = memorySpace
        self.__sizeObserver = SizeChangeObserver( self )
        if register is None :
            # parent is still optional.
            assert setCollection is not None

            self.__register = Register( memorySpace, setCollection,
                                        parent = parent )
        else :
            self.__register = register
        self.__register.sizeChangeNotifier.addObserver( self.__sizeObserver )
        self.__element = AddressableMemoryElement( memorySpace,
                                                   sizeObject = self.__register.size )
        self.__previousRegister = None

        self.__registerConstraintNotifiers()


    def __registerConstraintNotifiers( self ) :
        self.__register.memory.addressChangeNotifier.addObserver( self.__addressObserver )

        # RegisterInstance only cares about address constraints. Size constraints are managed by the Register object.
        self.__register[ 'constraints' ].addressChangeNotifier.addObserver( self.__addressObserver )


    def reviewAddressChange( self ) :
        newStartAddress = self.__calculateStartAddress()
        if newStartAddress != self.__element.startAddress :
            self.__element.startAddress = newStartAddress
            self.addressChangeNotifier.notifyObservers()


    def __calculateStartAddress( self ) :
        if (self.__previousRegister is not None) and (self.__previousRegister.endAddress is not None) :
            # Page register impact is calculate before application of constraints. This means that constraints could
            # still affect the address. eg. if address alignment modified the affect of page register on the address.
            proposedAddress = self.__previousRegister.endAddress + 1
            initialAddress = self.__register.memory.calculatePageRegisterImpact( proposedAddress )
        else :
            initialAddress = None

        newAddress = self.__register[ 'constraints' ].applyAddressConstraints( initialAddress )

        return newAddress


    def reviewSizeChange( self ) :
        pass


    @property
    def address( self ) :
        """
        The first memory unit (the smallest numerical address value) used by the register.
        """
        return self.__element.startAddress


    @property
    def endAddress( self ) :
        """
        The last memory unit (the largest numerical address value) used by the register.
        """
        return self.__element.endAddress


    @property
    def memory( self ) :
        """
        The memory space defining the register map memory.
        """
        return self.__register.memory


    @property
    def moduleOffset( self ) :
        """
        The offset of the register instance relative to its parent module.
        """
        if (self.__register.parent is not None) \
                and (self.__element.startAddress is not None) :
            value = self.__element.startAddress - self.__register.parent.baseAddress
        else :
            value = None

        return value


    @property
    def offset( self ) :
        """
        Offset address relative to the memory space base address.
        """
        return self.__element.offset


    @property
    def bitMap( self ) :
        return self.__register.bitMap


    @property
    def canonicalId( self ) :
        return self.__register.canonicalId


    @property
    def previousElement( self ) :
        """
        The previous register from which to derive the address of the current register.
        """
        return self.__previousRegister


    @previousElement.setter
    def previousElement( self, previousRegister ) :
        """
        When a Register is added to a Module it is added to the modules ElementList. ElementList uses this property
        to link this Register with the previous Register in the list. This property is where the address and size
        notification relationships between adjacent registers are assigned.

        :param previousRegister:
        """
        self.__previousRegister = previousRegister
        self.__previousRegister.sizeChangeNotifier.addObserver( self.__addressObserver )
        self.__previousRegister.addressChangeNotifier.addObserver( self.__addressObserver )

        # An address or size change in the previous register can affect the address of the current register, but the
        # previous register should have no effect on the size of the current register which is determined by
        # constraints and bit fields.
        self.reviewAddressChange()


    @property
    def sizeBits( self ) :
        return self.__register.sizeBits


    @property
    def sizeMemoryUnits( self ) :
        return self.__register.sizeMemoryUnits


    @property
    def sizeChangeNotifier( self ) :
        return self.__register.sizeChangeNotifier


    def addField( self, name, registerBitInterval,
                  fieldBitInterval = None,
                  isGlobal = False ) :
        newRegister = self.__register.addField( name, registerBitInterval,
                                                fieldBitInterval = fieldBitInterval,
                                                isGlobal = isGlobal )
        return newRegister


    def __getitem__( self, item ) :
        return self.__register[ item ]


    def __setitem__( self, key, value ) :
        self.__register[ key ] = value


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace, setCollection,
                       optional = False,
                       parent = None ) :
        thisRegister = Register.from_yamlData( yamlData, memorySpace, setCollection,
                                               optional = optional,
                                               parent = parent )
        thisObject = cls( memorySpace,
                          parent = parent,
                          register = thisRegister,
                          setCollection = setCollection )
        setCollection.registerSet.add( thisObject )

        return thisObject


    def to_yamlData( self ) :
        registerYaml = self.__register.to_yamlData()

        registerYaml[ 'register' ].update( parameter( '_address', self.address ) )

        return registerYaml
