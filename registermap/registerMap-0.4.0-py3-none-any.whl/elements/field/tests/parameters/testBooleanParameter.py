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

import registerMap.elements.field.parameters as rmbp


class TestBooleanParameter( unittest.TestCase ) :
    def setUp( self ) :
        self.p = rmbp.BooleanParameter( 'booleanParameter' )
        self.assertTrue( self.p.value )


    def testDataAssignment( self ) :
        self.p.value = False

        self.assertFalse( self.p.value )


    def testNonBoolRaises( self ) :
        with self.assertRaisesRegex( rmbp.ConfigurationError, '^Must be specified as boolean' ) :
            self.p.value = 'true'


if __name__ == '__main__' :
    unittest.main()
