"""
Definition of constraints on register map artifacts.
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

import abc
import logging
import math

import registerMap.utility.io.yaml.parameters.parse as ryp

from registerMap.utility.io import yaml

from registerMap.exceptions import ConstraintError, ParseError


log = logging.getLogger( __name__ )


class AbstractConstraint( metaclass = abc.ABCMeta ) :
    constraintTypes = { 'size' : 0,
                        'address' : 1 }


    @property
    @abc.abstractmethod
    def value( self ) :
        pass


    @value.setter
    @abc.abstractmethod
    def value( self, v ) :
        pass


    @abc.abstractmethod
    def calculate( self, value ) :
        pass


    @abc.abstractmethod
    def validate( self, value ) :
        pass


class ConstraintObserver :
    def __init__( self, owner ) :
        self.__owner = owner


    def update( self, notifier, arguments ) :
        currentConstraint = self.__owner.value
        # The constraint can initially be None until it is set by the users and while this is true, validation should
        # not be done.
        if currentConstraint is not None :
            # Redundantly setting the value to its current value will still trigger the validation method.
            self.__owner.value = currentConstraint


class AlignmentMemoryUnits( AbstractConstraint,
                            yaml.Import,
                            yaml.Export ) :
    """
    Alignment memory units means that the address will be aligned to the next highest multiple of the specified number
    of memory units.
    """
    name = 'alignmentMemoryUnits'
    type = AbstractConstraint.constraintTypes[ 'address' ]

    __yamlName = 'alignment'


    def __init__( self, memorySpace, constraintValue = None ) :
        super().__init__()

        self.__observer = ConstraintObserver( self )

        self.__memory = memorySpace
        self.__memory.addressChangeNotifier.addObserver( self.__observer )

        if constraintValue is not None :
            self.__validateConstraint( constraintValue )
        self.__alignmentConstraint = constraintValue


    @property
    def value( self ) :
        return self.__alignmentConstraint


    @value.setter
    def value( self, v ) :
        self.__validateConstraint( v )

        self.__alignmentConstraint = v


    @staticmethod
    def __validateConstraint( value ) :
        assert isinstance( value, int )

        validatePositiveNonZero( value, 'Alignment' )


    def calculate( self, value ) :
        self.validate( value )
        assert isinstance( self.__alignmentConstraint, int )

        if value is not None :
            modifiedValue = int( math.ceil( float( value ) / self.__alignmentConstraint ) * self.__alignmentConstraint )
        else :
            modifiedValue = None

        return modifiedValue


    def validate( self, value ) :
        if value is not None :
            assert isinstance( value, int )

            validatePositive( value, 'Address' )


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace,
                       optional = False ) :
        def recordValue( yamlValue ) :
            nonlocal constraint

            constraint.__alignmentConstraint = yamlValue


        constraint = cls( memorySpace )

        goodResult = False
        if cls.__yamlName in yamlData :
            goodResult = ryp.integerParameter( yamlData, cls.__yamlName, recordValue,
                                               optional = optional )
        else :
            constraint = None

        if (not optional) and (not goodResult) :
            raise ParseError( 'Yaml data does not contain alignment constraint' )

        return constraint


    def to_yamlData( self ) :
        yamlData = { self.__yamlName : self.__alignmentConstraint }

        return yamlData


class FixedAddress( AbstractConstraint ) :
    """
    Fixed address means that the address will never change from the specified value.
    """
    name = 'fixedAddress'
    type = AbstractConstraint.constraintTypes[ 'address' ]

    __yamlName = 'fixedAddress'


    def __init__( self, memorySpace,
                  constraintValue = None ) :
        super().__init__()

        self.__observer = ConstraintObserver( self )

        self.__memory = memorySpace
        self.__memory.addressChangeNotifier.addObserver( self.__observer )

        if constraintValue is not None :
            self.__validateConstraint( constraintValue )
        self.__addressConstraint = constraintValue


    @property
    def value( self ) :
        return self.__addressConstraint


    @value.setter
    def value( self, v ) :
        self.__validateConstraint( v )

        self.__addressConstraint = v


    def __validateConstraint( self, value ) :
        assert isinstance( value, int )
        validatePositive( value, 'Fixed address constraint' )

        if self.__memory.pageSize is not None :
            if self.__memory.isPageRegister( value ) :
                raise ConstraintError( 'Cannot constrain address to page register' )


    def calculate( self, value ) :
        self.validate( value )
        assert isinstance( self.__addressConstraint, int )

        fixedAddress = self.__addressConstraint
        currentAddress = value
        if (currentAddress is not None) and (currentAddress > fixedAddress) :
            raise ConstraintError( 'Fixed address exceeded, '
                                   + hex( currentAddress ) + ' (current), '
                                   + hex( fixedAddress ) + ' (constraint)' )
        return fixedAddress


    def validate( self, value ) :
        if value is not None :
            validatePositive( value, 'Fixed address' )


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace,
                       optional = False ) :
        def recordValue( yamlValue ) :
            nonlocal constraint

            constraint.__addressConstraint = yamlValue


        constraint = cls( memorySpace )

        goodResult = False
        if cls.__yamlName in yamlData :
            goodResult = ryp.integerParameter( yamlData, cls.__yamlName, recordValue,
                                               optional = optional )
        else :
            constraint = None

        if (not optional) and (not goodResult) :
            raise ParseError( 'Yaml data does not contain fixed address constraint' )

        return constraint


    def to_yamlData( self ) :
        yamlData = { self.__yamlName : self.__addressConstraint }

        return yamlData


class FixedSizeMemoryUnits( AbstractConstraint ) :
    """
    Fixed size constraint means that the size will never change from the specified value. The size is defined as the
    number of memory units.

    eg. In a memory space with 32 bit memory units, a fixed size of 2 memory units means a size of 8 bytes.
    """
    name = 'fixedSizeMemoryUnits'
    type = AbstractConstraint.constraintTypes[ 'size' ]

    __yamlName = 'fixedSize'


    def __init__( self, memorySpace, constraintValue = None ) :
        super().__init__()

        self.__observer = ConstraintObserver( self )

        self.__memory = memorySpace
        self.__memory.sizeChangeNotifier.addObserver( self.__observer )

        if constraintValue is not None :
            self.validate( constraintValue )
        self.__sizeConstraint = constraintValue


    @property
    def value( self ) :
        return self.__sizeConstraint


    @value.setter
    def value( self, v ) :
        self.validate( v )

        self.__sizeConstraint = v


    def calculate( self, value ) :
        self.validate( value )
        assert isinstance( self.__sizeConstraint, int )

        fixedSize = self.__sizeConstraint
        currentSize = value
        if currentSize > fixedSize :
            raise ConstraintError( 'Fixed size exceeded, '
                                   + repr( currentSize ) + ' (current), '
                                   + repr( fixedSize ) + ' (constraint)' )

        modifiedValue = self.__sizeConstraint
        return modifiedValue


    def validate( self, value ) :
        # Unlike an address, a size value can never be None.
        assert isinstance( value, int )

        validatePositive( value, 'Fixed size' )


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace,
                       optional = False ) :
        def recordValue( yamlValue ) :
            nonlocal constraint

            constraint.__sizeConstraint = yamlValue


        constraint = cls( memorySpace )

        goodResult = False
        if cls.__yamlName in yamlData :
            goodResult = ryp.integerParameter( yamlData, cls.__yamlName, recordValue,
                                               optional = optional )
        else :
            constraint = None

        if (not optional) and (not goodResult) :
            raise ParseError( 'Yaml data does not contain fixed size constraint' )

        return constraint


    def to_yamlData( self ) :
        yamlData = { self.__yamlName : self.__sizeConstraint }

        return yamlData


def validatePositive( value, idText ) :
    """
    Test a value for positive integer, raising an exception if false.

    :param value: The value to be tested
    :param idText: Short text identifying the class of value for the exception
    """
    if (not isinstance( value, int )) \
            or (value < 0) :
        raise ConstraintError( idText + ' must be a positive integer' )


def validatePositiveNonZero( value, idText ) :
    """
    Test a value for positive, non-zero integer, raising an exception if false.

    :param value: The value to be tested
    :param idText: Short text identifying the class of value for the exception
    """
    if (not isinstance( value, int )) \
            or (value < 1) :
        raise ConstraintError( idText + ' must be a positive non-zero integer' )
