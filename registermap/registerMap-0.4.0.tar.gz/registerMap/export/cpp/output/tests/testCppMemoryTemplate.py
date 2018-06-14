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

from registerMap.export.cpp.elements import Memory

from registerMap.export.commonCppC.output.tests.common import doTemplateTest

from ..memory import \
    MEMORY_TEMPLATE_CONFIGURATION, \
    MemoryTemplates

import registerMap.export.base.template


CREATE_DIRECTORY_MODULE_PATH = 'registerMap.export.cpp.output.memory.MemoryTemplates.createDirectory'
OPEN_MODULE_PATH = 'registerMap.export.commonCppC.output.memory.open'


class TestMemoryTemplates( unittest.TestCase ) :

    def setUp( self ) :
        self.expectedName = 'someName'
        self.includeDirectory = 'include/path'
        self.sourceDirectory = 'source/path'

        self.mock_Memory = unittest.mock.create_autospec( Memory )
        self.mock_Memory.baseAddress = 1234
        self.mock_Memory.size = 345
        self.mock_Memory.sizeType = 'uint_least8_t'

        self.templateConfig = copy.deepcopy( MEMORY_TEMPLATE_CONFIGURATION )


    def testDefaults( self ) :
        expectedMemoryDirectory = os.path.join( self.includeDirectory, 'memory' )
        expectedTemplateDirectory = os.path.join( 'templates', 'idiomatic' )

        paths = MemoryTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = MemoryTemplates( paths,
                                           self.expectedName,
                                           self.mock_Memory )

        self.assertEqual( self.expectedName, outputUnderTest.registerMapName )
        self.assertEqual( expectedTemplateDirectory, outputUnderTest.templateDirectory )
        self.assertEqual( expectedMemoryDirectory, outputUnderTest.memoryDirectory )
        self.assertEqual( self.mock_Memory, outputUnderTest.encapsulatedMemory )


    def testInitialCreatedFiles( self ) :
        paths = MemoryTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = MemoryTemplates( paths,
                                           self.expectedName,
                                           self.mock_Memory )
        mock_template = unittest.mock.create_autospec( jinja2.Template )
        with unittest.mock.patch( CREATE_DIRECTORY_MODULE_PATH,
                                  return_value = True ) as mock_createDirectory, \
                unittest.mock.patch( OPEN_MODULE_PATH ), \
                unittest.mock.patch.object( registerMap.export.base.template.jinja2.Environment,
                                            'get_template',
                                            return_value = mock_template ) :
            outputUnderTest.apply()

        expectedFiles = [
            'include/path/memory/memory.hpp',
            'source/path/memory.cpp',
        ]

        self.assertEqual( expectedFiles, outputUnderTest.createdFiles )

        self.assertEqual( 2, len( mock_template.render.mock_calls ) )

        mock_createDirectory.assert_has_calls( [
            unittest.mock.call( outputUnderTest.memoryDirectory ),
        ] )


    def testMemoryHeader( self ) :
        paths = MemoryTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = MemoryTemplates( paths,
                                           self.expectedName,
                                           self.mock_Memory )
        # Select the header to test
        self.templateConfig[ 'header' ] = [ self.templateConfig[ 'header' ][ 0 ] ]
        self.templateConfig[ 'source' ] = list()
        outputUnderTest.configuration = self.templateConfig

        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH )
        expectedLines = [
            '/*\n',
            ' *\n',
            ' * someName\n',
            ' *\n',
            ' *\n',
            ' */\n',
            '\n',
            '#ifndef SOMENAME_MEMORY_HPP\n',
            '#define SOMENAME_MEMORY_HPP\n',
            '\n',
            '#include <cstdint>\n',
            '\n',
            '\n',
            'namespace someName\n',
            '{\n',
            '\n',
            'class MemorySpace\n',
            '  {\n',
            '  public:\n',
            '\n',
            '    static uint_least8_t volatile* const\n',
            '      base;\n',
            '\n',
            '#ifdef OFF_TARGET_MEMORY\n',
            '\n',
            '    static constexpr std::uint_least32_t\n',
            '      allocated_memory_span = 345;\n',
            '\n',
            '    static uint_least8_t volatile\n',
            '      off_target_memory[ allocated_memory_span ];\n',
            '\n',
            '#endif\n',
            '\n',
            '  };\n',
            '\n',
            '}\n', '\n', '#endif\n'
        ]

        self.assertEqual( expectedLines, actualLines )


    def testMemorySource( self ) :
        paths = MemoryTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = MemoryTemplates( paths,
                                           self.expectedName,
                                           self.mock_Memory )
        # Select the source to test
        self.templateConfig[ 'header' ] = list()
        self.templateConfig[ 'source' ] = [ self.templateConfig[ 'source' ][ 0 ] ]
        outputUnderTest.configuration = self.templateConfig

        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH )
        expectedLines = [
            '/*\n',
            ' *\n',
            ' * someName\n',
            ' *\n',
            ' *\n',
            ' */\n',
            '\n',
            '#include <cstdint>\n',
            '\n',
            '#include "this/prefix/memory/memory.hpp"\n',
            '\n',
            '\n',
            'namespace someName\n',
            '{\n',
            '\n',
            '#ifndef OFF_TARGET_MEMORY\n',
            '\n',
            '  uint_least8_t volatile* const\n',
            "    MemorySpace::base = reinterpret_cast<uint_least8_t volatile* const>( 1234 );\n",
            '\n',
            '#else\n',
            '\n',
            '  constexpr std::uint_least32_t\n',
            '    MemorySpace::allocated_memory_span;\n',
            '\n',
            '  uint_least8_t volatile\n',
            '    MemorySpace::off_target_memory[];\n',
            '\n',
            '  uint_least8_t volatile* const\n',
            '    MemorySpace::base = MemorySpace::off_target_memory;\n',
            '\n',
            '#endif\n',
            '\n',
            '}\n' ]

        expectedText = ''.join( expectedLines )
        actualText = ''.join( actualLines )

        self.assertEqual( expectedText, actualText )


if __name__ == '__main__' :
    unittest.main()
