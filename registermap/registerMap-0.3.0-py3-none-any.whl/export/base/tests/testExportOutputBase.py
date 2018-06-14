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

from ..output import OutputBase


class MockOptions :

    def __init__( self ) :
        self.output = None
        self.packAlignment = None


class MockOutput( OutputBase ) :

    def __init__( self, outputOptions,
                  licenseTextLines = list() ) :
        super().__init__( outputOptions,
                          licenseTextLines = licenseTextLines )


    def generate( self, registerMap, registerMapName ) :
        pass


class TestOutputBase( unittest.TestCase ) :

    def setUp( self ) :
        self.filePath = 'some/path'
        self.registerMap = RegisterMap()

        self.registerMap.addModule( 'm1' )
        self.registerMap.addModule( 'm2' )


    def testOutputDirectoryProperty( self ) :
        mockOptions = MockOptions()
        mockOptions.output = self.filePath

        with unittest.mock.patch(
                'registerMap.export.base.output.OutputBase._OutputBase__validateOutputDirectory' ) :
            outputUnderTest = MockOutput( mockOptions )

            self.assertEqual( self.filePath, outputUnderTest.outputDirectory )


    def testPackAlignmentOption( self ) :
        mockOptions = MockOptions()
        mockOptions.packAlignment = 10

        with unittest.mock.patch(
                'registerMap.export.base.output.OutputBase._OutputBase__validateOutputDirectory' ) :
            outputUnderTest = MockOutput( mockOptions )

            self.assertEqual( mockOptions.packAlignment, outputUnderTest.outputOptions.packAlignment )


if __name__ == '__main__' :
    unittest.main()
