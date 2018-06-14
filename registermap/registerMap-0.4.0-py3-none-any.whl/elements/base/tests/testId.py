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

import unittest

from ..identity import IdentityElement


class MockIdentityElement( IdentityElement ) :
    """
    Implement abstract methods to enable testing.
    """


    @property
    def canonicalId( self ) :
        return None


class TestIdentityElement( unittest.TestCase ) :
    def setUp( self ) :
        self.firstId = MockIdentityElement()
        self.secondId = MockIdentityElement()


    def testInitialId( self ) :
        firstId = self.firstId.id
        secondId = self.secondId.id

        self.assertNotEqual( firstId, secondId )


    def testIdConsistency( self ) :
        firstIdRead = self.firstId.id

        newId = MockIdentityElement()

        secondIdRead = self.firstId.id

        self.assertEqual( firstIdRead, secondIdRead )


if __name__ == '__main__' :
    unittest.main()
