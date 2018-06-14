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

import os
import unittest.mock

from registerMap.export.base.template import TemplateBase


class TestExportTemplateBase( unittest.TestCase ) :

    def setUp( self ) :
        self.includeDirectory = 'include/path'
        self.sourceDirectory = 'source/path'


    def testDefaults( self ) :
        here = os.path.abspath( os.path.dirname( __file__ ) )
        expectedTemplateDir = 'templates'

        paths = TemplateBase.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory
        paths.templatePackagePath = 'registerMap.export.c.output'

        outputUnderTest = TemplateBase( paths )

        self.assertEqual( expectedTemplateDir, outputUnderTest.templateDirectory )
        self.assertEqual( self.includeDirectory, outputUnderTest.paths.includeDirectory )
        self.assertEqual( self.sourceDirectory, outputUnderTest.paths.sourceDirectory )
        self.assertEqual( list(), outputUnderTest.createdDirectories )
        self.assertEqual( list(), outputUnderTest.createdFiles )


    def testTemplateLicenseTextLines( self ) :
        lines = [
            'this line',
            'another line',
        ]

        paths = TemplateBase.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory
        paths.templatePackagePath = 'registerMap.export.c.output'

        outputUnderTest = TemplateBase( paths,
                                        licenseTextLines = lines )

        self.assertEqual( lines, outputUnderTest.licenseTextLines )


    def testTemplateSubDir( self ) :
        subdir = 'thisSubdir'

        expectedValue = os.path.join( 'templates', subdir )

        paths = TemplateBase.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory
        paths.templatePackagePath = 'registerMap.export.c.output'

        outputUnderTest = TemplateBase( paths,
                                        subdir = subdir )

        actualValue = outputUnderTest.templateDirectory

        self.assertEqual( expectedValue, actualValue )


    def testCreateDirectorry( self ) :
        paths = TemplateBase.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory
        paths.templatePackagePath = 'registerMap.export.c.output'

        outputUnderTest = TemplateBase( paths )

        expectedValue = 'some/path'

        with unittest.mock.patch( 'registerMap.export.base.template.os.makedirs' ) as mock_makedirs :
            outputUnderTest.createDirectory( expectedValue )

            mock_makedirs.assert_called_once_with( expectedValue,
                                                   exist_ok = True )

        self.assertEqual( 1, len( outputUnderTest.createdDirectories ) )
        self.assertIn( expectedValue, outputUnderTest.createdDirectories )


if __name__ == '__main__' :
    unittest.main()
