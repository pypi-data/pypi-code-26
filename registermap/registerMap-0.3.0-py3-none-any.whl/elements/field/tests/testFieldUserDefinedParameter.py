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

from ..field import Field


class TestFieldUserDefinedParameter( unittest.TestCase ) :
    def setUp( self ) :
        self.fieldUnderTest = Field()


    def testAssignParameterOk( self ) :
        expectedValue = 'some value'
        self.fieldUnderTest[ 'my-parameter' ] = expectedValue

        self.assertEqual( expectedValue, self.fieldUnderTest[ 'my-parameter' ] )


    def testBadParameterRaises( self ) :
        with self.assertRaisesRegex( KeyError, 'Field parameter not in core or user data' ) :
            self.fieldUnderTest[ 'bad-parameter' ]


    def testUnderscorePrefixAsserts( self ) :
        with self.assertRaises( AssertionError ) :
            self.fieldUnderTest[ '_my-parameter' ] = 2


if __name__ == '__main__' :
    unittest.main()
