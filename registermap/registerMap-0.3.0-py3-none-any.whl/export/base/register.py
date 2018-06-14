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

import abc

from registerMap.structure.interval import makeContiguous


class RegisterFieldsIndirection :

    def __init__( self, fieldElements, FieldType ) :
        self.__elements = fieldElements
        self.__FieldType = FieldType


    def __getitem__( self, item ) :
        return self.__FieldType( self.__elements[ item ] )


    def __len__( self ) :
        return len( self.__elements )


class RegisterBase( metaclass = abc.ABCMeta ) :
    """
    Representation of a Register for output using jinja2.

    `RegisterBase` just represents the assigned fields in the export. See `RegisterContiguousFieldIntervals` for a
    representation including unassigned and reserved bit intervals.
    """


    def __init__( self, element, FieldType ) :
        super().__init__()

        self._element = element
        self._FieldType = FieldType


    @property
    def name( self ) :
        return self._element[ 'name' ]


    @property
    def fields( self ) :
        return RegisterFieldsIndirection( list( self._element[ 'fields' ].values() ), self._FieldType )


    @property
    def address( self ) :
        """
        The absolute address of the register in the register map, formatted for text output in hexadecimal.
        """
        return hex( self._element.address )


    @property
    def offset( self ) :
        """
        The offset of the register in the register map, relative to the base address of the register map,
        formatted for text output in hexadecimal.
        """
        return hex( self._element.offset )


    @property
    def moduleOffset( self ) :
        """
        The offset of the register in the register map, relative to its parent module, formatted for text output in
        hexadecimal.
        """
        return hex( self._element.moduleOffset )


    @property
    def precedingGapBytes( self ) :
        """
        The size of any gap between the end address of the preceding register and the start address of this register.

        For sequential registers the start address would be one more than the end address of the preceding register,
        resulting in a gap of zero.
        """
        memoryUnitBytes = int( self._element.memory.memoryUnitBits / 8 )
        return (self._element.address - self._element.previousElement.endAddress - 1) * memoryUnitBytes


class RegisterContiguousFieldIntervals( RegisterBase ) :
    """
    Represent the register with a field for every bit interval, including unassigned or reserved ranges. For C and
    C++ idiomatic export,.
    """


    def __init__( self, element, FieldType ) :
        super().__init__( element, FieldType )

        self.__fieldItems = element[ 'fields' ].items()


    @property
    def fields( self ) :
        registerIntervals = makeContiguous( self._element.bitMap.sourceIntervals, (self._element.sizeBits - 1) )

        contiguousFields = list()
        for thisInterval in registerIntervals :
            try :
                thisField = self.__findFieldFromInterval( thisInterval )

                contiguousFields.append( thisField )
            except RuntimeError :
                # The interval must be an "unassigned" insertion so create a dummy field to capture the necessary size.
                # Duck typing at work...
                contiguousFields.append( {
                    'name' : '',
                    'size' : thisInterval.size,
                } )

        return RegisterFieldsIndirection( contiguousFields, self._FieldType )


    def __findFieldFromInterval( self, interval ) :
        fieldOwnsInterval = list()
        for name, field in self.__fieldItems :

            fieldIntervalValues = list()
            for sourceInterval, fieldDestinationInterval in field.bitMap.destinationIntervals.items() :
                fieldIntervalValues.append( fieldDestinationInterval.value )

            assert len( fieldIntervalValues ) == 1

            if interval.value == fieldIntervalValues[ 0 ] :
                fieldOwnsInterval.append( field )

        if len( fieldOwnsInterval ) != 1 :
            raise RuntimeError( 'Interval not found in field destinations' )

        return fieldOwnsInterval[ 0 ]
