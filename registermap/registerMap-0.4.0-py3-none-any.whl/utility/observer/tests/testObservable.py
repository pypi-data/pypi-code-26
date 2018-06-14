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

import unittest

from ..observable import Observable
from ..interface import Observer


class TestObservable( unittest.TestCase ) :
    def testConstruct( self ) :
        thisObservable = Observable()

        self.assertEqual( thisObservable.observers, [ ] )


class TestAddRemoveObservers( unittest.TestCase ) :
    class MockObserver( Observer ) :
        def update( self, observable, arguments ) :
            pass


    def setUp( self ) :
        self.testObservable = Observable()


    def testAddObserver( self ) :
        expectedObserver = TestAddRemoveObservers.MockObserver()

        self.testObservable.addObserver( expectedObserver )

        self.assertEqual( len( self.testObservable.observers ), 1 )
        self.assertEqual( self.testObservable.observers[ 0 ], expectedObserver )


    def testRemoveObserver( self ) :
        expectedObserver = TestAddRemoveObservers.MockObserver()

        self.testObservable.addObserver( expectedObserver )

        self.assertEqual( len( self.testObservable.observers ), 1 )
        self.assertEqual( self.testObservable.observers[ 0 ], expectedObserver )

        self.testObservable.removeObserver( expectedObserver )

        self.assertEqual( len( self.testObservable.observers ), 0 )


    def testRemoveObservers( self ) :
        expectedNumberObservers = 4
        for i in range( 0, expectedNumberObservers ) :
            self.testObservable.addObserver( TestAddRemoveObservers.MockObserver() )

        self.assertEqual( len( self.testObservable.observers ), expectedNumberObservers )

        self.testObservable.removeObservers()

        self.assertEqual( len( self.testObservable.observers ), 0 )


class TestNotifyObservers( unittest.TestCase ) :
    class MockObserver( Observer ) :
        def __init__( self ) :
            self.updateCount = 0


        def update( self, source, arguments ) :
            self.updateCount += 1


        @property
        def updated( self ) :
            returnValue = False
            if self.updateCount != 0 :
                returnValue = True

            return returnValue


    def setUp( self ) :
        self.testObservable = Observable()


    def testSingleNotification( self ) :
        expectedObserver = TestNotifyObservers.MockObserver()

        self.testObservable.addObserver( expectedObserver )

        self.assertEqual( len( self.testObservable.observers ), 1 )
        self.assertEqual( self.testObservable.observers[ 0 ], expectedObserver )

        self.testObservable.notifyObservers()

        self.assertTrue( expectedObserver.updated )


if __name__ == '__main__' :
    unittest.main()
