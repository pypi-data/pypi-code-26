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

from ..instance import ModuleInstance
from ..module import Module

from .commonModuleInterfaceTests import CommonModuleInterfaceTests


class TestModuleInstance( unittest.TestCase ) :

    def setUp( self ) :
        self.mock_memory = unittest.mock.MagicMock()

        self.mock_moduleParent = unittest.mock.create_autospec( Module )
        self.mock_moduleParent.canonicalId = 'one.two'

        self.elementUnderTest = ModuleInstance( self.mock_moduleParent, self.mock_memory )
        self.elementUnderTest[ 'name' ] = 'm1'


    def testAssignedMemoryUnitsProperty( self ) :
        self.mock_moduleParent.assignedMemoryUnits = 5

        self.assertEqual( self.mock_moduleParent.assignedMemoryUnits, self.elementUnderTest.assignedMemoryUnits )


    def testCanonicalIdProperty( self ) :
        self.mock_previousElement = unittest.mock.MagicMock()
        self.mock_previousElement.endAddress = 0x100

        self.elementUnderTest.previousElement = self.mock_previousElement

        self.assertEqual( 0x101, self.elementUnderTest.baseAddress )

        self.assertEqual( 'one.two[0x101]', self.elementUnderTest.canonicalId )


    def testMemoryProperty( self ) :
        self.assertEqual( self.mock_memory, self.elementUnderTest.memory )


class TestModuleInstanceBaseAddressProperty( unittest.TestCase ) :

    def setUp( self ) :
        self.mock_memory = unittest.mock.MagicMock()

        self.mock_previousElement = unittest.mock.MagicMock()
        self.mock_previousElement.endAddress = None

        self.mock_moduleParent = unittest.mock.create_autospec( Module )
        self.mock_moduleParent.canonicalId = 'one.two'

        self.elementUnderTest = ModuleInstance( self.mock_moduleParent, self.mock_memory )
        self.elementUnderTest[ 'name' ] = 'm1'
        self.elementUnderTest.previousElement = self.mock_previousElement


    def testDefault( self ) :
        """
        With no constraints and no previous element specified, the base address can only be `None`.
        """
        self.assertIsNone( self.elementUnderTest.baseAddress )


    def testNoConstraintsNonePreviousEndAddress( self ) :
        """
        With no constraints applied and a previous element with undefined end address, the base address can only be
        `None`.
        """
        self.mock_previousElement.endAddress = None
        self.elementUnderTest.previousElement = self.mock_previousElement

        self.assertIsNone( self.elementUnderTest.baseAddress )


    def testNoConstraintsPreviousEndAddressDefined( self ) :
        """
        With no constraints applied and a previous element with defined end address, the base address can only be the
        next address.
        """
        self.mock_previousElement.endAddress = 0x100

        expectedValue = self.mock_previousElement.endAddress + 1

        self.assertEqual( expectedValue, self.elementUnderTest.baseAddress )


class TestModuleInstanceConstraints( CommonModuleInterfaceTests.TestModuleConstraints ) :

    def constructInstanceUnderTest( self ) :
        self.mock_moduleParent = unittest.mock.create_autospec( Module )
        self.mock_moduleParent.canonicalId = 'one.two'

        elementUnderTest = ModuleInstance( self.mock_moduleParent, self.mock_memory )
        elementUnderTest[ 'name' ] = 'm1'

        return elementUnderTest


class TestModuleInstanceOffsetProperty( CommonModuleInterfaceTests.TestModuleOffsetProperty ) :

    def constructInstanceUnderTest( self ) :
        self.mock_moduleParent = unittest.mock.create_autospec( Module )
        self.mock_moduleParent.canonicalId = 'one.two'

        moduleUnderTest = ModuleInstance( self.mock_moduleParent, self.testSpace )
        moduleUnderTest[ 'name' ] = 'm1'

        return moduleUnderTest


class TestModuleInstancePreviousElementProperty( CommonModuleInterfaceTests.TestModulePreviousElementProperty ) :

    def constructInstanceUnderTest( self ) :
        self.mock_moduleParent = unittest.mock.create_autospec( Module )

        elementUnderTest = ModuleInstance( self.mock_moduleParent, self.mock_memory )
        elementUnderTest[ 'name' ] = 'm1'

        return elementUnderTest


class TestModuleNameParameter( CommonModuleInterfaceTests.TestModuleNameParameter ) :

    def constructInstanceUnderTest( self ) :
        self.mock_moduleParent = Module( self.mock_memory, self.setCollection )

        elementUnderTest = ModuleInstance( self.mock_moduleParent, self.mock_memory )

        return elementUnderTest


    def testParentNameAssignment( self ) :
        """
        A name assigned to a module instance assigns the name to the parent module.
        """
        expectedValue = 'some-name'

        self.moduleUnderTest[ 'name' ] = expectedValue

        self.assertEqual( expectedValue, self.moduleUnderTest[ 'name' ] )
        self.assertEqual( expectedValue, self.mock_moduleParent[ 'name' ] )


if __name__ == '__main__' :
    unittest.main()
