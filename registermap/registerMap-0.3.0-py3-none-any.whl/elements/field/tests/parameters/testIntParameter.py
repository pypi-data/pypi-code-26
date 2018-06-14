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

from registerMap.elements.field.parameters import \
    ConfigurationError, \
    IntParameter, \
    PositiveIntParameter


class TestIntParameter( unittest.TestCase ) :
    def typeUnderTest( self,
                       value = 0 ) :
        """
        Children must implement this method to define the parameter type to apply testing to.

        :return: Type of parameter for testing.
        """
        return IntParameter( 'intParameter',
                             value = value )


    def testDefaultConstructorOk( self ) :
        self.typeUnderTest()


    def testConstructorNoneRaises( self ) :
        with self.assertRaisesRegex( ConfigurationError, '^Must be an int' ) :
            self.typeUnderTest( value = None )


    def testConstructorNonIntRaises( self ) :
        with self.assertRaisesRegex( ConfigurationError, '^Must be an int' ) :
            self.typeUnderTest( value = '30' )


    def testValueNonIntRaises( self ) :
        p = self.typeUnderTest()
        with self.assertRaisesRegex( ConfigurationError, '^Must be an int' ) :
            p.value = list()


class TestPositiveIntParameter( TestIntParameter ) :
    def typeUnderTest( self,
                       value = 0 ) :
        return PositiveIntParameter( 'positiveIntParameter',
                                     value = value )


    def testNegativeValueRaises( self ) :
        p = self.typeUnderTest()
        with self.assertRaisesRegex( ConfigurationError, '^Must be a positive int' ) :
            p.value = -1


if __name__ == '__main__' :
    unittest.main()
