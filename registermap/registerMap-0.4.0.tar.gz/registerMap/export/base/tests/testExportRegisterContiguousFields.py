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

from registerMap import RegisterMap

from registerMap.structure.interval import sortIntervals

from ..field import FieldBase
from ..register import RegisterContiguousFieldIntervals as Register


class MockField( FieldBase ) :
    def __init__( self, element ) :
        super().__init__( element )


    @property
    def type( self ) :
        return 'unsigned'


class TestCppRegisterFieldOrdering( unittest.TestCase ) :
    def setUp( self ) :
        self.registerMap = RegisterMap()

        m1 = self.registerMap.addModule( 'm1' )

        self.r1 = m1.addRegister( 'r1' )

        self.cppRegisterUnderTest = Register( self.r1, MockField )


    def testContiguousLocalFields( self ) :
        expectedFields = [
            self.r1.addField( 'f1', (0, 3) ),
            self.r1.addField( 'f2', (4, 6) ),
            self.r1.addField( 'f3', (7, 7) ),
        ]
        self.assertEqual( 8, self.r1.sizeBits )

        registerIntervals = sortIntervals( self.r1.bitMap.sourceIntervals )
        fieldsUnderTest = self.cppRegisterUnderTest.fields

        self.assertEqual( len( registerIntervals ), len( fieldsUnderTest ) )

        self.assertEqual( len( expectedFields ), len( registerIntervals ) )

        for index in range( 0, len( registerIntervals ) ) :
            expectedInterval = registerIntervals[ index ].value
            fieldIntervals = sortIntervals( fieldsUnderTest[ index ]._element.bitMap.destinationIntervals.values() )

            self.assertEqual( 1, len( fieldIntervals ) )
            self.assertEqual( expectedInterval, fieldIntervals[ 0 ].value )


    def testNoncontiguousLocalFields8BitRegister( self ) :
        self.r1.addField( 'f1', (0, 1) )
        # Unassigned interval (2, 3)
        self.r1.addField( 'f2', (4, 5) )
        # Unassigned interval (6, 6)
        self.r1.addField( 'f3', (7, 7) )

        self.assertEqual( 8, self.r1.sizeBits )

        expectedNumberFields = 5

        fieldsUnderTest = self.cppRegisterUnderTest.fields

        self.assertEqual( expectedNumberFields, len( fieldsUnderTest ) )

        # Can only check names and sizes for inserted gaps
        expectedSizes = [
            2, 2, 2, 1, 1,
        ]
        actualSizes = [ x._element[ 'size' ] for x in fieldsUnderTest ]
        self.assertEqual( expectedSizes, actualSizes )

        expectedNames = [
            'f1',
            '',
            'f2',
            '',
            'f3',
        ]
        actualNames = [ x._element[ 'name' ] for x in fieldsUnderTest ]
        self.assertEqual( expectedNames, actualNames )


    def testNoncontiguousLocalFields8BitRegisterStartsWithUnassignedf( self ) :
        # Unassigned interval (0, 0)
        self.r1.addField( 'f1', (1, 1) )
        # Unassigned interval (2, 3)
        self.r1.addField( 'f2', (4, 5) )
        # Unassigned interval (6, 6)
        self.r1.addField( 'f3', (7, 7) )

        self.assertEqual( 8, self.r1.sizeBits )

        expectedNumberFields = 6

        fieldsUnderTest = self.cppRegisterUnderTest.fields

        self.assertEqual( expectedNumberFields, len( fieldsUnderTest ) )

        # Can only check names and sizes for inserted gaps
        expectedSizes = [
            1, 1, 2, 2, 1, 1,
        ]
        actualSizes = [ x._element[ 'size' ] for x in fieldsUnderTest ]
        self.assertEqual( expectedSizes, actualSizes )

        expectedNames = [
            '',
            'f1',
            '',
            'f2',
            '',
            'f3',
        ]
        actualNames = [ x._element[ 'name' ] for x in fieldsUnderTest ]
        self.assertEqual( expectedNames, actualNames )


    def testNoncontiguousLocalFields16BitRegister( self ) :
        self.r1.addField( 'f1', (0, 1) )
        # Unassigned interval (2, 3)
        self.r1.addField( 'f2', (4, 5) )
        # Unassigned interval (6, 6)
        self.r1.addField( 'f3', (7, 9) )
        # Unassigned interval (10, 15)

        expectedNumberFields = 6

        fieldsUnderTest = self.cppRegisterUnderTest.fields

        self.assertEqual( expectedNumberFields, len( fieldsUnderTest ) )

        # Can only check names and sizes for inserted gaps
        expectedSizes = [
            2, 2, 2, 1, 3, 6,
        ]
        actualSizes = [ x._element[ 'size' ] for x in fieldsUnderTest ]
        self.assertEqual( expectedSizes, actualSizes )

        expectedNames = [
            'f1',
            '',
            'f2',
            '',
            'f3',
            '',
        ]
        actualNames = [ x._element[ 'name' ] for x in fieldsUnderTest ]
        self.assertEqual( expectedNames, actualNames )


if __name__ == '__main__' :
    unittest.main()
