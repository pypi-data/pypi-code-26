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

from registerMap.elements.field.parameters import GlobalParameter


class MockElement :
    def __init__( self, parent ) :
        self.__parent = parent


    @property
    def parent( self ) :
        return self.__parent


class TestGlobalParameter( unittest.TestCase ) :
    def testIsGlobal( self ) :
        mockElement = MockElement( None )

        testParameter = GlobalParameter( mockElement )

        self.assertTrue( testParameter.value )


    def testIsNotGlobal( self ) :
        mockElement = MockElement( 'someName' )

        testParameter = GlobalParameter( mockElement )

        self.assertFalse( testParameter.value )
