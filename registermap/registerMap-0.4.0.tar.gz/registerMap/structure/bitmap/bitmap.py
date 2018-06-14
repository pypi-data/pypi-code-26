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

import registerMap.utility.io.yaml.parameters.encode as rye

from registerMap.exceptions import \
    ConfigurationError

from registerMap.structure.bitrange import BitRange
from registerMap.structure.interval.overlap import isOverlap
from registerMap.utility.io import yaml


class SourceIntervalError( ConfigurationError ) :
    pass


class DestinationIntervalError( ConfigurationError ) :
    pass


class BitMap( yaml.Export ) :
    """
    Map bits from a source to a destination.

    Assumes a single destination with multiple sources.
    eg. A register (source) maps its bits to multiple bit fields (destinations).
        A bit field (source) maps its bits to multiple registers (destinations).
    """

    __yamlName = 'bitmap'


    def __init__( self, source ) :
        """
        :param source: The source element.
        """
        self.__source = source
        self.__destinations = set()

        # Indexed by source bit ranges.
        # Each source bit range entry contains the destination object and destination bit range it is mapped to.
        self.__map = collections.OrderedDict()


    @property
    def destinations( self ) :
        return self.__destinations


    @property
    def destinationIntervals( self ) :
        """
        Map source intervals to destination intervals, one-to-one.

        :return: dict mapping
        """
        intervals = dict()
        for sourceRange, destinationData in self.__map.items() :
            intervals[ sourceRange ] = destinationData[ 'interval' ]

        return intervals


    @property
    def intervalMap( self ) :
        return self.__map


    @property
    def source( self ) :
        return self.__source


    @property
    def sourceIntervals( self ) :
        """
        :return: set of source intervals.
        """
        intervals = set()
        for sourceRange, destinationData in self.__map.items() :
            intervals.add( sourceRange )

        return intervals


    def addReciprocalMap( self, sourceBitRange, destinationBitRange, destination ) :
        """
        When creating a reciprocal mapping between elements (eg register <-> field) this method is used to apply the map
        to the destination element.

        The parameter names are defined with respect to the other side of the mapping. So if the register is where the
        reciprocal map is being applied from, then the parameters of this method are as seen by the field (the
        destination object is the register).

        :param sourceBitRange:
        :param destinationBitRange:
        :param destination:
        :return:
        """

        # Notation has reversed here, but keep in mind that we are talking about the other (remote/destination) end of
        # the reciprocal map.
        self.__validateBitRange( sourceBitRange, self.__source, 'destination' )
        self.__validateBitRange( destinationBitRange, destination, 'source' )

        try :
            self.__validateSourceOverlaps( sourceBitRange )
        except SourceIntervalError as e :
            raise DestinationIntervalError(
                'Specifed destination interval overlaps existing destination intervals, {0}: {1}'.format(
                    self.__source.canonicalId,
                    sourceBitRange.value ) ) from e

        # Assume that length checking of source & destination ranges has been done by mapBits.

        # Passed all the validation so preserve the mapping
        self.__addElements( sourceBitRange, destinationBitRange, destination )


    def mapBits( self, sourceBitRange, destinationBitRange, destination ) :
        self.__validateBitRange( sourceBitRange, self.__source, 'source' )
        self.__validateBitRange( destinationBitRange, destination, 'destination' )

        self.__validateSourceOverlaps( sourceBitRange )

        if sourceBitRange.numberBits != destinationBitRange.numberBits :
            raise ConfigurationError(
                'Mismatched bit range sizes, {0} (source), {1} (destination)'.format( sourceBitRange.numberBits,
                                                                                      destinationBitRange.numberBits ) )
        # The destination is assumed to do it's own validation of the destination interval.
        destination.bitMap.addReciprocalMap( destinationBitRange, sourceBitRange, self.__source )

        # Passed all the validation so preserve the mapping
        self.__addElements( sourceBitRange, destinationBitRange, destination )


    def __addElements( self, sourceBitRange, destinationBitRange, destination ) :
        self.__map[ sourceBitRange ] = { 'interval' : destinationBitRange,
                                         'destination' : destination }
        self.__destinations.add( destination )


    @staticmethod
    def __validateBitRange( bitRange, element, rangeText ) :
        """
        Check if the specified range has the appropriate properties against the specified element.

        :param bitRange:
        :param element:
        :param rangeText: 'source' | 'destination'
        :return:
        """
        assert rangeText in [ 'source', 'destination' ]

        if not isinstance( bitRange, BitRange ) :
            raise RuntimeError( 'Incorrect bits type for {1}, {0}'.format( type( bitRange ), rangeText ) )

        expectedSize = element.sizeBits
        if bitRange.numberBits > expectedSize :
            raise RuntimeError(
                'Range {2} cannot exceed size, {0} (range), {1} (size)'.format(
                    bitRange.numberBits,
                    expectedSize,
                    rangeText ) )


    def __validateSourceOverlaps( self, sourceBitRange ) :
        """
        Check if a specified range overlaps any existing ranges in the mapping.

        :param sourceBitRange:
        :return:
        """
        anyOverlaps = False
        overlapsIntervals = list()
        for thisSourceRange, destinationData in self.__map.items() :
            # Do not fail on identical intevals because this implies an over-write, not an error.
            if sourceBitRange != thisSourceRange :
                thisOverlap = isOverlap( sourceBitRange, thisSourceRange )
                anyOverlaps |= thisOverlap

                if thisOverlap :
                    overlapsIntervals.append( '{0}'.format( thisSourceRange.value ) )

        if anyOverlaps :
            raise SourceIntervalError(
                'Specifed source interval overlaps existing source intervals, {0}: {1}, {2}'.format(
                    self.__source.canonicalId,
                    sourceBitRange.value,
                    overlapsIntervals ) )


    def removeDestination( self,
                           destination = None,
                           interval = None ) :
        """
        Remove a mapping related to a destination.

        :param destination: (optional) Destination object to be removed. All interval mappings to the destination object
        will be removed.
        :param interval: (optional) Interval to be removed.

        :return:
        """
        assert not ((destination is None)
                    and (interval is None))

        if interval is None :
            self.__removeDestinationObject( destination )

            # The source is a destination on the other side of the mapping so make sure the other end is cleaned up.
            destination.bitMap._removeReciprocalMap( self.__source )
        else :
            assert (destination is not None) \
                   and (interval is not None)

            sourceInterval = self.__removeDestinationInterval( destination, interval )

            # The source is a destination on the other side of the mapping so make sure the other end is cleaned up.
            destination.bitMap._removeReciprocalMap( self.__source, sourceInterval )


    def __removeDestinationObject( self, destination ) :
        # destination is not None
        assert destination is not None

        try :
            self.__destinations.remove( destination )

            # find every source interval mapped to destination and remove it from the mapping.
            mappedSourceIntervals = [ k for k, v in self.__map.items() if v[ 'destination' ] == destination ]
            for sourceBitRange in mappedSourceIntervals :
                del self.__map[ sourceBitRange ]
        except KeyError as e :
            raise ConfigurationError(
                'Specified destination does not exist in bit map and cannot be removed, {0}'.format(
                    destination.id ) ) from e


    def __removeDestinationInterval( self, destination, interval ) :
        if destination not in self.__destinations :
            raise ConfigurationError(
                'Specified destination does not exist in bit map so cannot remove interval, {0}'.format(
                    destination.id ) )

        mappedSourceIntervals = [ k for k, v in self.__map.items()
                                  if (v[ 'destination' ] == destination) and (v[ 'interval' ] == interval) ]

        if len( mappedSourceIntervals ) != 0 :
            assert len( mappedSourceIntervals ) == 1

            for sourceBitRange in mappedSourceIntervals :
                del self.__map[ sourceBitRange ]
        else :
            raise ConfigurationError(
                'Specified destination interval does not exist in bit map and cannot be removed, {0}, {1}'.format(
                    destination.id,
                    interval ) )

        return mappedSourceIntervals[ 0 ]


    def _removeReciprocalMap( self,
                              destination = None,
                              interval = None ) :
        """
        Remove the specified object or range from the reciprocal mapping.

        Should only be used BitMap to BitMap, not publicly by users.

        :param destination:
        :param interval:
        :return:
        """
        assert not ((destination is None)
                    and (interval is None))

        if interval is None :
            self.__removeDestinationObject( destination )
        else :
            assert (destination is not None) \
                   and (interval is not None)

            self.__removeDestinationInterval( destination, interval )


    def removeSource( self, interval ) :
        assert interval is not None

        if interval == self.__source :
            raise ConfigurationError( 'Cannot remove source from bit map, {0}'.format( self.__source.canonicalId ) )

        destination = self.__removeSourceInterval( interval )

        # The source is a destination on the other side of the mapping so make sure the other end is cleaned up.
        destination.bitMap._removeReciprocalMap( self.__source, interval )


    def __removeSourceInterval( self, interval ) :
        range = BitRange( interval )
        destinationObject = self.__map[ range ][ 'destination' ]

        del self.__map[ range ]

        return destinationObject


    def to_yamlData( self ) :

        def constructDestinationIntervalsMapping() :
            nonlocal self, yamlData

            mappingData = list()
            for sourceRange, destinationData in self.__map.items() :
                sourceRangeData = sourceRange.to_yamlData()
                destinationRangeData = destinationData[ 'interval' ].to_yamlData()
                intervalData = {
                    'source' : sourceRangeData[ 'range' ],
                    'destination' : destinationRangeData[ 'range' ],
                    'destinationId' : destinationData[ 'destination' ].canonicalId,
                }
                mappingData.append( intervalData )

            yamlData[ self.__yamlName ] = mappingData


        yamlData = rye.parameter( 'bitmap', dict() )

        constructDestinationIntervalsMapping()

        return yamlData
