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

from .interface import Observer


class SizeChangeObserver( Observer ) :
    """
    Narrow the generic Observer to a specific type of event relating to element size.
    """


    def __init__( self, owner ) :
        self.__owner = owner


    def update( self, observable, arguments ) :
        self.__owner.reviewSizeChange()
