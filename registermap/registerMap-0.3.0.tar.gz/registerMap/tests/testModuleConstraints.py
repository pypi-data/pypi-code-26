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


class TestModuleFixedAddressConstraint( unittest.TestCase ) :
    def setUp( self ) :
        self.registerMap = RegisterMap()

        self.moduleUnderTest = self.registerMap.addModule( 'm1' )


    def testFixedAddressOk( self ) :
        self.assertEqual( 0x0, self.registerMap.memory.baseAddress )
        self.assertEqual( self.registerMap.memory.baseAddress, self.moduleUnderTest.baseAddress )

        expectedValue = 0x20f0

        self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = expectedValue

        # The register map base address is unchanged.
        self.assertEqual( 0x0, self.registerMap.memory.baseAddress )
        # The module has the specified base address.
        self.assertEqual( expectedValue, self.moduleUnderTest.baseAddress )


class TestModuleFixedSizeConstraint( unittest.TestCase ) :
    def setUp( self ) :
        self.registerMap = RegisterMap()

        self.moduleUnderTest = self.registerMap.addModule( 'm1' )


    def testFixedSizeOk( self ) :
        self.assertEqual( 0, self.moduleUnderTest.spanMemoryUnits )

        expectedValue = 10

        self.moduleUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = expectedValue

        self.assertEqual( expectedValue, self.moduleUnderTest.spanMemoryUnits )


    def testExceededSizeRegisterAddRaises( self ) :
        moduleSize = 3
        self.moduleUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = moduleSize

        for i in range( 0, moduleSize ) :
            self.moduleUnderTest.addRegister( 'r{0}'.format( i ) )

        # Attempting to add a fourth register to a module constrained to size 3 raises an exception.
        with self.assertRaisesRegex( ConstraintError, '^Fixed size exceeded' ) :
            self.moduleUnderTest.addRegister( 'r3' )


    def testExceededSizeConstraintTooSmallRaises( self ) :
        moduleSize = 3

        for i in range( 0, moduleSize ) :
            self.moduleUnderTest.addRegister( 'r{0}'.format( i ) )

        self.assertEqual( moduleSize, self.moduleUnderTest.spanMemoryUnits )

        # Attempting to constrain the size smaller than the allocated registers raises
        with self.assertRaisesRegex( ConstraintError, '^Fixed size exceeded' ) :
            self.moduleUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = moduleSize - 1


class TestModuleMemoryAlignmentConstraint( unittest.TestCase ) :
    def setUp( self ) :
        self.registerMap = RegisterMap()
        # Assign an unaligned base address to the map.
        self.registerMap.memory.baseAddress = 0x1

        self.moduleUnderTest = self.registerMap.addModule( 'm1' )


    def testWordAlignedAddress( self ) :
        self.assertEqual( 8, self.registerMap.memory.memoryUnitBits )
        self.assertEqual( self.registerMap.memory.baseAddress, self.moduleUnderTest.baseAddress )

        # Align the module start address to 32 bit (8 bits * 4 memory units).
        self.moduleUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4

        self.assertEqual( 0x4, self.moduleUnderTest.baseAddress )


class TestModuleConstraintCombinations( unittest.TestCase ) :
    def setUp( self ) :
        self.registerMap = RegisterMap()

        self.moduleUnderTest = self.registerMap.addModule( 'm1' )


    def testFixedAddressAndAlignmentOk( self ) :
        # Applying memory alignment to a fixed address that is memory aligned is fine (implicitly, if in future
        # the fixed address is changed to an unaligned address then an exception will be raised)
        self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x4
        self.moduleUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4


    def testFixedAddressAndAlignmentRaises( self ) :
        self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x1

        with self.assertRaisesRegex( ConstraintError, '^Address constraints conflict' ) :
            self.moduleUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4


    def testFixedAddressAndAlignmentWithAddressChangeRaises( self ) :
        self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x4
        self.moduleUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4

        with self.assertRaisesRegex( ConstraintError, '^Address constraints conflict' ) :
            self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x5


    def testFixedAddressAndSizeOk( self ) :
        self.moduleUnderTest[ 'constraints' ][ 'fixedAddress' ] = 0x4
        self.moduleUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = 4


    def testAlignmentAndSizeOk( self ) :
        self.moduleUnderTest[ 'constraints' ][ 'alignmentMemoryUnits' ] = 4
        self.moduleUnderTest[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = 4


if __name__ == '__main__' :
    unittest.main()
