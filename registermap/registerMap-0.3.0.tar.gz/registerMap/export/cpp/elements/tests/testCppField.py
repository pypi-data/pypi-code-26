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

from ..field import Field


class TestCppExportField( unittest.TestCase ) :
    def setUp( self ) :
        self.mockFieldElement = {
            'size' : 0,
        }

        self.fieldUnderTest = Field( self.mockFieldElement )


    def testValidTypes( self ) :
        expectedValues = [
            {
                'size' : 8,
                'type' : 'std::uint8_t',
            },
            {
                'size' : 9,
                'type' : 'std::uint16_t',
            },
            {
                'size' : 16,
                'type' : 'std::uint16_t',
            },
            {
                'size' : 17,
                'type' : 'std::uint32_t',
            },
            {
                'size' : 32,
                'type' : 'std::uint32_t',
            },
            {
                'size' : 33,
                'type' : 'std::uint64_t',
            },
            {
                'size' : 64,
                'type' : 'std::uint64_t',
            },
        ]
        for thisValue in expectedValues :
            self.mockFieldElement[ 'size' ] = thisValue[ 'size' ]

            self.assertEqual( thisValue[ 'type' ], self.fieldUnderTest.type )


    def testTypeGreaterThan64Asserts( self ) :
        # Assume that 64 bit is the maximum field size type allowed.
        self.mockFieldElement[ 'size' ] = 65

        with self.assertRaises( AssertionError ) :
            self.fieldUnderTest.type


if __name__ == '__main__' :
    unittest.main()
