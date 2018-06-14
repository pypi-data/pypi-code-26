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

from ..registerMap import RegisterMap
from ..exceptions import ConstraintError


class TestRegisterFixedAddressConstraint( unittest.TestCase ) :

    def setUp( self ) :
        self.registerMap = RegisterMap()
        self.module = self.registerMap.addModule( 'm1' )

        self.r1 = self.module.addRegister( 'r1' )


    def testFixedAddressOk( self ) :
        """
        Applying a fixed address constraint changes the address.
        """
        self.assertEqual( 0x0, self.registerMap.memory.baseAddress )
        self.assertEqual( self.registerMap.memory.baseAddress, self.module.baseAddress )
        self.assertEqual( self.module.baseAddress, self.r1.address )

        expectedValue = 0x2000

        self.r1[ 'constraints' ][ 'fixedAddress' ] = expectedValue

        self.assertEqual( expectedValue, self.r1.address )


    def testFixedAddressAdjustsOtherRegisters( self ) :
        """
        Applying a fixed address shuffles other registers appropriately.
        """

        r2 = self.module.addRegister( 'r2' )

        self.assertEqual( 0x0, self.registerMap.memory.baseAddress )
        self.assertEqual( self.registerMap.memory.baseAddress, self.module.baseAddress )
        self.assertEqual( self.module.baseAddress, self.r1.address )

        self.assertEqual( 1, self.r1.sizeMemoryUnits )
        self.assertEqual( 1, r2.address )

        expectedValue = 0x2000

        self.r1[ 'constraints' ][ 'fixedAddress' ] = expectedValue

        self.assertEqual( expectedValue, self.r1.address )
        self.assertEqual( (expectedValue + 1), r2.address )


class TestRegisterFixedSizeConstraint( unittest.TestCase ) :

    def setUp( self ) :
        self.registerMap = RegisterMap()
        self.module = self.registerMap.addModule( 'm1' )
        self.register1 = self.module.addRegister( 'r1' )

        self.registerUnderTest = self.module.addRegister( 'r2' )


    def testFixedSizeOk( self ) :
        """
        Show that when a fixed size constraint is applied, that the next register address is shifted appropriately.
        """
        self.assertEqual( self.module.baseAddress, self.register1.address )
        self.assertEqual( (self.register1.address + 1), self.registerUnderTest.address )

        expectedSize = 5

        self.register1[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = expectedSize

        expectedAddress = self.register1.address + expectedSize

        self.assertEqual( expectedAddress, self.registerUnderTest.address )


class TestRegisterMemoryAlignmentConstraint( unittest.TestCase ) :

    def setUp( self ) :
        self.registerMap = RegisterMap()
        self.registerMap.memory.baseAddress = 0x1
        self.module = self.registerMap.addModule( 'm1' )

        self.registerUnderTest = self.module.addRegister( 'r1' )


    def testMemoryAlignmentOk( self ) :
        """
        Show that address alignment shuffles a register address appropriately.
        """
        self.assertEqual( 0x1, self.registerMap.memory.baseAddress )
        self.assertEqual( self.registerMap.memory.baseAddress, self.module.baseAddress )
        self.assertEqual( self.registerMap.memory.baseAddress, self.registerUnderTest.address )

        self.registerUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4

        expectedValue = 0x4

        self.assertEqual( expectedValue, self.registerUnderTest.address )


class TestRegisterConstraintCombinations( unittest.TestCase ) :

    def setUp( self ) :
        self.registerMap = RegisterMap()
        self.module = self.registerMap.addModule( 'm1' )

        self.registerUnderTest = self.module.addRegister( 'r1' )


    def testFixedAddressAndAlignmentOk( self ) :
        """
        Applying memory alignment to a fixed address that is memory aligned is fine (implicitly, if in future
        the fixed address is changed to an unaligned address then an exception will be raised)
        """
        self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x4
        self.registerUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4


    def testFixedAddressAndAlignmentRaises( self ) :
        """
        Show that an exception is raised when alignment conflicts with a fixed address.
        """
        self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x1

        with self.assertRaisesRegex( ConstraintError, '^Address constraints conflict' ) :
            self.registerUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4


    def testFixedAddressAndAlignmentWithAddressChangeRaises( self ) :
        """
        Show that an exception is raised when a fixed address is changed that conflicts with existing constraints.
        """
        self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x4
        self.registerUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4

        with self.assertRaisesRegex( ConstraintError, '^Address constraints conflict' ) :
            self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x5


    def testFixedAddressAndSizeOk( self ) :
        """
        Show that non conflicting fixed address and fixed size constraints are okay.
        """
        self.registerUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x4
        self.registerUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = 4


    def testAlignmentAndSizeOk( self ) :
        """
        Show that non conflicting alignment and fixed size constraints are okay.
        """
        self.registerUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4
        self.registerUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = 4


if __name__ == '__main__' :
    unittest.main()
