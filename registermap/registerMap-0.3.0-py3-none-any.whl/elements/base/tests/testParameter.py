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

import unittest

from registerMap.utility.observer.interface import Observer

from ..parameter import Parameter


class MockObserver( Observer ) :
    def __init__( self ) :
        super().__init__()

        self.value = None


    def update( self, subject, arguments ) :
        self.value = subject.value


class TestObserveParameter( unittest.TestCase ) :
    def setUp( self ) :
        self.parameterUnderTest = Parameter( value = 6.6626 )

        self.observer = MockObserver()

        self.parameterUnderTest.addObserver( self.observer )


    def testValueChangeNotifies( self ) :
        self.assertNotEqual( self.parameterUnderTest.value, self.observer.value )

        self.parameterUnderTest.value = 3.14

        self.assertEqual( self.parameterUnderTest.value, self.observer.value )


if __name__ == '__main__' :
    unittest.main()
