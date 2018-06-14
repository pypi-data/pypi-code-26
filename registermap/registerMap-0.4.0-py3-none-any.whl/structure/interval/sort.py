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

from .overlap import anyOverlap


def intervalSortKey( interval ) :
    return min( interval.value )


def sortIntervals( intervals ) :
    """
    Sort a list or set of integer intervals `ClosedIntegerInterval` into a list of increasing order.

    eg.

      { (3, 4), (0, 2), (5, 7) } becomes [ (0, 2), (3, 4), (5, 7) ]

    :param intervals:

    :return: list of sorted intervals.
    """
    assert not anyOverlap( intervals )

    sortedIntervals = sorted( list( intervals ), key = intervalSortKey )

    return sortedIntervals
