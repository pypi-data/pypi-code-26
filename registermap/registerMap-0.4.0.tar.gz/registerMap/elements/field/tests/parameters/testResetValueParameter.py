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
    ResetValueParameter

from registerMap.elements.field.tests.parameters.testIntParameter import TestPositiveIntParameter


class TestResetValueParameter( TestPositiveIntParameter ) :
    def typeUnderTest( self, value = 0 ) :
        return ResetValueParameter( value = value )


    def setUp( self ) :
        self.parameter = self.typeUnderTest()


    def testDefaultMaxValue( self ) :
        expectedValue = 0

        actualValue = self.parameter.maxValue
        self.assertEqual( actualValue, expectedValue )


class TestResetValueParameterSize( unittest.TestCase ) :
    def testDefaultSize( self ) :
        p = ResetValueParameter()

        expectedValue = 0
        actualValue = p.size

        self.assertEqual( actualValue, expectedValue )


    def testConstructSize( self ) :
        expectedSize = 2

        p = ResetValueParameter( size = expectedSize )

        actualSize = p.size

        self.assertEqual( actualSize, expectedSize )


    def testSetSize( self ) :
        expectedSize = 2

        p = ResetValueParameter()

        self.assertNotEqual( p.size, expectedSize )

        p.size = expectedSize

        self.assertEqual( p.size, expectedSize )


    def testNegativeSetSizeRaises( self ) :
        p = ResetValueParameter()
        with self.assertRaisesRegex( ConfigurationError, '^Size must be positive int' ) :
            p.size = -1


    def testNegativeConstructSizeRaises( self ) :
        with self.assertRaisesRegex( ConfigurationError, '^Size must be positive int' ) :
            ResetValueParameter( size = -1 )


class TestResetValueParameterMaxValue( unittest.TestCase ) :
    def testMaxValue( self ) :
        p = ResetValueParameter( size = 2 )

        self.assertEqual( p.maxValue, 3 )


if __name__ == '__main__' :
    unittest.main()
