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

def isOverlap( interval1, interval2 ) :
    """
    Is there any overlap of the two specified intervals?

    :param interval1:
    :param interval2:

    :return: True if the intervals overlap in any way.
    """
    if (max( interval1.value ) >= min( interval2.value )) \
            and (max( interval1.value ) <= max( interval2.value )) :
        return True
    elif (min( interval1.value ) <= max( interval2.value )) \
            and (min( interval1.value ) >= min( interval2.value )) :
        return True
    elif (min( interval2.value ) <= max( interval1.value )) \
            and (min( interval2.value ) >= min( interval1.value )) :
        return True

    return False


def isEncapsulated( interval1, interval2 ) :
    """
    Is interval1 encapsulated by interval2?

    :param interval1:
    :param interval2:

    :return: True if interval1 is encapsulated by interval2 (including that they are equal).
    """
    if (max( interval1.value ) <= max( interval2.value )) \
            and (min( interval1.value ) >= min( interval2.value )) :
        return True

    return False


def anyOverlap( intervals ) :
    """
    Detect any overlapping intervals in an iterable of intervals.

    :param intervals:

    :return: True if any intervals in the iterable overlap.
    """
    reviewedOverlap = set()

    intervalSet = set( intervals )

    while intervalSet:
        reviewingInterval = intervalSet.pop()
        reviewedOverlap.add( any( { isOverlap( reviewingInterval, x ) for x in intervalSet } ) )

    return any( reviewedOverlap )
