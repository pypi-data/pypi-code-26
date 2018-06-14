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

import argparse
import unittest

from ..arguments import CArgumentParser


class TestCppArgumentParser( unittest.TestCase ) :

    def setUp( self ) :
        self.argumentParser = argparse.ArgumentParser()

        self.languageParsers = self.argumentParser.add_subparsers( dest = 'language',
                                                                   title = 'language' )
        self.parserUnderTest = CArgumentParser( self.languageParsers )


    def testOutputSpecified( self ) :
        inputValue = [
            'c',
            'some/path',
        ]
        args = self.argumentParser.parse_args( inputValue )

        actualValue = self.parserUnderTest.acquireOptions( args )

        self.assertEqual( inputValue[ 1 ], actualValue.output )


    def testMissingOutputRaises( self ) :
        inputValue = [
            'c',
        ]
        with self.assertRaises( SystemExit ) :
            self.argumentParser.parse_args( inputValue )


    def testPack( self ) :
        inputValue = [
            'c',
            'some/path',
            '--pack',
            '2'
        ]
        args = self.argumentParser.parse_args( inputValue )

        actualValue = self.parserUnderTest.acquireOptions( args )

        self.assertEqual( int( inputValue[ 3 ] ), actualValue.packAlignment )


    def testDefaultIncludePath( self ) :
        inputValue = [
            'c',
            'some/path',
        ]
        args = self.argumentParser.parse_args( inputValue )

        actualValue = self.parserUnderTest.acquireOptions( args )

        self.assertEqual( '', actualValue.includePrefix )


    def testIncludePath( self ) :
        inputValue = [
            'c',
            'some/path',
            '--include-prefix',
            'some/include/path',
        ]
        args = self.argumentParser.parse_args( inputValue )

        actualValue = self.parserUnderTest.acquireOptions( args )

        self.assertEqual( inputValue[ 3 ], actualValue.includePrefix )


if __name__ == '__main__' :
    unittest.main()
