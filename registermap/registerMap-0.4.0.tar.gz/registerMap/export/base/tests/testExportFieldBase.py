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

from registerMap.elements.field import Field as FieldElement

from .mocks import MockField


class TestExportFieldBase( unittest.TestCase ) :
    def setUp( self ) :
        self.field = FieldElement()
        self.field[ 'name' ] = 'f1'
        self.field[ 'size' ] = 4

        self.mockField = MockField( self.field )


    def testName( self ) :
        self.assertEqual( self.field[ 'name' ], self.mockField.name )


    def testSize( self ) :
        self.assertEqual( self.field[ 'size' ], self.mockField.size )


    def testType( self ) :
        self.assertEqual( self.mockField.expectedType, self.mockField.type )


if __name__ == '__main__' :
    unittest.main()
