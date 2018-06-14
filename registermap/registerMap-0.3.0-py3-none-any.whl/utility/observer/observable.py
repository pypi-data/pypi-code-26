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


class Observable( object ) :
    """
    Parent interface of a class that wants other classes to observe its generated events.
    """


    # http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Observer.html

    def __init__( self ) :
        self.observers = list()
        self.changed = False


    def addObserver( self, thisObserver ) :
        if thisObserver not in self.observers :
            self.observers.append( thisObserver )


    def notifyObservers( self, arguments = None ) :
        for thisObserver in self.observers :
            thisObserver.update( self, arguments )


    def removeObserver( self, thisObserver ) :
        self.observers.remove( thisObserver )


    def removeObservers( self ) :
        self.observers = list()
