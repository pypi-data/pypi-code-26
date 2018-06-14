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

import copy
import jinja2
import os
import unittest.mock

from registerMap.export.commonCppC.output.tests.common import doTemplateTest

from ..macro import \
    MACRO_TEMPLATE_CONFIGURATION, \
    MacroTemplates

import registerMap.export.base.template


CREATE_DIRECTORY_MODULE_PATH = 'registerMap.export.cpp.output.macro.MacroTemplates.createDirectory'
OPEN_MODULE_PATH = 'registerMap.export.commonCppC.output.macro.open'


class TestMacroTemplate( unittest.TestCase ) :

    def setUp( self ) :
        self.expectedName = 'someName'
        self.includeDirectory = 'include/path'
        self.sourceDirectory = 'source/path'


    def testDefaults( self ) :
        expectedMacroDirectory = os.path.join( self.includeDirectory, 'macro' )
        expectedTemplateDirectory = os.path.join( 'templates', 'macro' )

        paths = MacroTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = MacroTemplates( paths,
                                          self.expectedName )

        self.assertEqual( self.expectedName, outputUnderTest.registerMapName )
        self.assertEqual( expectedTemplateDirectory, outputUnderTest.templateDirectory )
        self.assertEqual( expectedMacroDirectory, outputUnderTest.macroDirectory )


    def testInitialCreatedFiles( self ) :
        paths = MacroTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = MacroTemplates( paths,
                                          self.expectedName )
        mock_template = unittest.mock.create_autospec( jinja2.Template )
        with unittest.mock.patch( CREATE_DIRECTORY_MODULE_PATH,
                                  return_value = True ) as mock_createDirectory, \
                unittest.mock.patch( OPEN_MODULE_PATH ), \
                unittest.mock.patch.object( registerMap.export.base.template.jinja2.Environment,
                                            'get_template',
                                            return_value = mock_template ) :
            outputUnderTest.apply()

        expectedFiles = [
            'include/path/macro/assert.hpp',
        ]

        self.assertEqual( expectedFiles, outputUnderTest.createdFiles )

        mock_template.render.assert_has_calls( [
            unittest.mock.call( registerMapName = self.expectedName,
                                licenseText = None ),
        ] )

        mock_createDirectory.assert_has_calls( [
            unittest.mock.call( outputUnderTest.macroDirectory ),
        ] )


class TestAssertMacroTemplate( unittest.TestCase ) :

    def setUp( self ) :
        self.expectedName = 'someName'
        self.includeDirectory = 'include/path'
        self.sourceDirectory = 'source/path'

        self.templateConfig = copy.deepcopy( MACRO_TEMPLATE_CONFIGURATION )
        self.templateConfig[ 'files' ] = [ self.templateConfig[ 'files' ][ 0 ] ]


    def testAssertMacroOutput( self ) :
        paths = MacroTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = MacroTemplates( paths,
                                          self.expectedName )
        outputUnderTest.configuration = self.templateConfig

        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH )

        expectedLines = [
            '/*\n',
            ' *\n',
            ' *\n',
            ' */\n',
            '\n',
            '#ifndef SOMENAME_ASSERT_HPP\n',
            '#define SOMENAME_ASSERT_HPP\n',
            '\n',
            '\n',
            '#ifndef DISABLE_RUNTIME_ASSERT\n',
            '\n',
            '#include <cassert>\n',
            '#define RUNTIME_ASSERT(expression) \\\n',
            '  assert(expression)\n',
            '\n',
            '#else\n',
            '\n',
            '#define RUNTIME_ASSERT()\n',
            '\n', '#endif\n',
            '\n',
            '\n',
            '#ifndef DISABLE_COMPILETIME_ASSERT\n',
            '\n',
            '#define COMPILETIME_ASSERT(expression) \\\n',
            '#if !(expression) \\\n',
            '#error "ASSERTION FAILED: " #expression \\\n',
            '#endif\n',
            '\n',
            '#else\n',
            '\n',
            '#define COMPILETIME_ASSERT(expression)\n',
            '\n', '#endif\n',
            '\n',
            '\n',
            '#endif\n'
        ]

        self.assertEqual( expectedLines, actualLines )


if __name__ == '__main__' :
    unittest.main()
