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

import unittest.mock

from registerMap.elements.tests.mockObserver import MockObserver
from registerMap.elements.base.element import ElementList
from registerMap.elements.module import Module
from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace

from registerMap.elements.register.tests.mocks import MockPreviousRegister

from ..instance import RegisterInstance


class TestRegisterInstanceYamlAddress( unittest.TestCase ) :

    def setUp( self ) :
        self.setCollection = SetCollection()
        self.testSpace = MemorySpace()
        self.testRegister = RegisterInstance( self.testSpace,
                                              setCollection = self.setCollection )

        self.previousRegister = MockPreviousRegister( endAddress = 0x3e7,
                                                      sizeMemoryUnits = 4 )
        self.testRegister.previousElement = self.previousRegister

        self.observer = MockObserver()
        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testYamlDataAddressSingleRegister( self ) :
        # The address data is automatically generated so it is prefixed by '_'.
        self.assertEqual( self.previousRegister.endAddress, 0x3e7 )

        expectedName = '_address'
        expectedValue = 0x3e8

        self.assertEqual( expectedValue, self.testRegister.address )

        yamlData = self.testRegister.to_yamlData()
        self.assertEqual( expectedValue, yamlData[ 'register' ][ expectedName ] )


if __name__ == '__main__' :
    unittest.main()
