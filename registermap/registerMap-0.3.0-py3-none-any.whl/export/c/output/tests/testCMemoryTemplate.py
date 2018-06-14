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

import jinja2
import os
import unittest.mock

from registerMap.export.c.elements import Memory

from registerMap.export.commonCppC.output.tests.common import doTemplateTest

from ..memory import MemoryTemplates

import registerMap.export.base.template


CREATE_DIRECTORY_MODULE_PATH = 'registerMap.export.c.output.memory.MemoryTemplates.createDirectory'
OPEN_MODULE_PATH = 'registerMap.export.commonCppC.output.memory.open'


class TestCMemoryTemplates( unittest.TestCase ) :

    def setUp( self ) :
        self.expectedName = 'someName'
        self.includeDirectory = 'include/this/path'
        self.sourceDirectory = 'source/path'

        self.mock_Memory = unittest.mock.create_autospec( Memory )
        self.mock_Memory.size = 345
        self.mock_Memory.sizeType = 'uint_least8_t'


    def testDefaults( self ) :
        expectedMemoryDirectory = os.path.join( self.includeDirectory, 'memory' )
        expectedTemplateDirectory = os.path.join( 'templates', 'idiomatic' )

        paths = MemoryTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/path'
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
        paths.includePrefix = 'this/path'
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = MemoryTemplates( paths, self.expectedName, self.mock_Memory )
        mock_template = unittest.mock.create_autospec( jinja2.Template )
        with unittest.mock.patch( CREATE_DIRECTORY_MODULE_PATH,
                                  return_value = True ) as mock_createDirectory, \
                unittest.mock.patch( OPEN_MODULE_PATH ), \
                unittest.mock.patch.object( registerMap.export.base.template.jinja2.Environment,
                                            'get_template',
                                            return_value = mock_template ) :
            outputUnderTest.apply()

        expectedFiles = [
            'include/this/path/memory/memory.h'
        ]

        self.assertEqual( expectedFiles, outputUnderTest.createdFiles )

        mock_template.render.assert_called_once()

        mock_createDirectory.assert_has_calls( [
            unittest.mock.call( outputUnderTest.memoryDirectory ),
        ] )


    def testMemoryOutput( self ) :
        paths = MemoryTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = MemoryTemplates( paths,
                                           self.expectedName,
                                           self.mock_Memory )
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
            '#ifndef SOMENAME_MEMORY_H\n',
            '#define SOMENAME_MEMORY_H\n',
            '\n',
            '#include <stdint.h>\n',
            '\n',
            '#include "this/prefix/macro/extern.h"\n',
            '\n',
            '\n',
            'SOMENAME_OPEN_EXTERN_C\n',
            '\n',
            'struct MemorySpace_t\n',
            '{\n',
            '#ifdef OFF_TARGET_MEMORY\n',
            '\n',
            '  uint_least32_t const allocated_memory_span;\n',
            '\n',
            "  uint_least8_t volatile base[ 345 ];\n",
            '\n',
            '#else\n',
            '\n',
            "  uint_least8_t volatile* const base;\n",
            '\n',
            '#endif\n',
            '};\n',
            '\n',
            'SOMENAME_CLOSE_EXTERN_C\n',
            '\n',
            '#endif\n',
        ]

        self.assertEqual( expectedLines, actualLines )


if __name__ == '__main__' :
    unittest.main()
