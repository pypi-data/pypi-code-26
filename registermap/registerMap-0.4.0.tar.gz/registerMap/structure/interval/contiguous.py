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

from .element import ClosedIntegerInterval
from .sort import sortIntervals


def makeContiguous( intervals, maxIndex ) :
    """
    Make the list or set of intervals contiguous by inserting intervals in any necessary gaps.

    :param intervals:
    :param maxIndex: The maximum index in the intervals. Enables inserting an interval at the end if necessary.

    :return: list of revised intervals
    """
    sortedIntervals = sortIntervals( intervals )

    contiguousIntervals = list()

    # Check for gap at the start
    if min( sortedIntervals[ 0 ].value ) != 0 :
        maxThisInterval = min( sortedIntervals[ 0 ].value ) - 1
        contiguousIntervals.append( ClosedIntegerInterval( (0, maxThisInterval) ) )

    for index in range( 0, (len( sortedIntervals ) - 1) ) :
        contiguousIntervals.append( sortedIntervals[ index ] )

        minNextInterval = min( sortedIntervals[ index + 1 ].value )
        expectedMinNextInterval = max( sortedIntervals[ index ].value ) + 1
        if minNextInterval != expectedMinNextInterval :
            contiguousIntervals.append( ClosedIntegerInterval( (expectedMinNextInterval, (minNextInterval - 1)) ) )

    # Always append the last interval
    contiguousIntervals.append( sortedIntervals[ -1 ] )

    maxLastInterval = max( sortedIntervals[ -1 ].value )
    if maxLastInterval != maxIndex :
        # Add an interval at the end to fill the gap to maxIndex.
        contiguousIntervals.append( ClosedIntegerInterval( ((maxLastInterval + 1), maxIndex) ) )

    return contiguousIntervals
