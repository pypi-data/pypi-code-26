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

from ..arguments import parseArguments


class TestExporterArgumentParser( unittest.TestCase ) :
    def testRegisterMapFilePath( self ) :
        inputValue = [
            'path/registerMapFile',
            'c++',
            'output/path',
        ]

        optionsUnderTest = parseArguments( inputValue )

        self.assertEqual( inputValue[ 0 ], optionsUnderTest.registerMapFile )


    def testDefaultRegisterMapName( self ) :
        inputValue = [
            'path/registerMapFile',
            'c++',
            'output/path',
        ]

        optionsUnderTest = parseArguments( inputValue )

        self.assertEqual( 'registerMap', optionsUnderTest.registerMapName )


    def testMissingLanguageRaises( self ) :
        inputValue = [
            'path/registerMapFile',
        ]

        with self.assertRaisesRegex( RuntimeError, '^Language must be specified' ) :
            parseArguments( inputValue )


    def testLongLicenseFileOption( self ) :
        inputValue = [
            'path/registerMapFile',
            '--license-file',
            'license/path',
            'c++',
            'output/path',
        ]

        optionsUnderTest = parseArguments( inputValue )

        self.assertEqual( inputValue[ 2 ], optionsUnderTest.licenseFile )


    def testShortLicenseFileOption( self ) :
        inputValue = [
            'path/registerMapFile',
            '-l',
            'license/path',
            'c++',
            'output/path',
        ]

        optionsUnderTest = parseArguments( inputValue )

        self.assertEqual( inputValue[ 2 ], optionsUnderTest.licenseFile )


    def testLongRegisterMapNameOption( self ) :
        inputValue = [
            'path/registerMapFile',
            '--registermap-name',
            'someName',
            'c++',
            'output/path',
        ]

        optionsUnderTest = parseArguments( inputValue )

        self.assertEqual( inputValue[ 2 ], optionsUnderTest.registerMapName )


    def testShortRegisterMapNameOption( self ) :
        inputValue = [
            'path/registerMapFile',
            '-n',
            'someName',
            'c++',
            'output/path',
        ]

        optionsUnderTest = parseArguments( inputValue )

        self.assertEqual( inputValue[ 2 ], optionsUnderTest.registerMapName )


if __name__ == '__main__' :
    unittest.main()
