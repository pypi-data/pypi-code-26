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
import unittest.mock

from registerMap import RegisterMap as ImportedRegisterMap

from registerMap.export.c.elements.memory import Memory
from registerMap.export.c.elements.registerMap import RegisterMap

from registerMap.export.commonCppC.output.tests.common import doTemplateTest

from ..registerMap import RegisterMapTemplates

import registerMap.export.base.template


CREATE_DIRECTORY_MODULE_PATH = 'registerMap.export.cpp.output.registerMap.RegisterMapTemplates.createDirectory'
OPEN_MODULE_PATH = 'registerMap.export.commonCppC.output.registerMap.open'

HEADER_MODULE_PATH = 'registerMap.export.cpp.output.registerMap.RegisterMapTemplatesBase' \
                     '._RegisterMapTemplatesBase__createRegisterMapHeader'
SOURCE_MODULE_PATH = 'registerMap.export.cpp.output.registerMap.RegisterMapTemplatesBase' \
                     '._RegisterMapTemplatesBase__createRegisterMapSource'


class TestRegisterMapTemplates( unittest.TestCase ) :

    def setUp( self ) :
        self.expectedName = 'someName'
        self.includeDirectory = 'include/path'
        self.sourceDirectory = 'source/path'

        self.__setupRegisterMap()


    def __setupRegisterMap( self ) :
        registerMap = ImportedRegisterMap()

        registerMap.memory.baseAddress = 0x20f0

        self.m1 = registerMap.addModule( 'm1' )

        r1 = self.m1.addRegister( 'r1' )

        r1.addField( 'f1', (0, 2) )
        r1.addField( 'f2', (3, 4) )
        r1.addField( 'f3', (5, 15) )

        self.registerMap = RegisterMap( self.expectedName, registerMap )


    def testInitialCreatedFiles( self ) :
        paths = RegisterMapTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = RegisterMapTemplates( paths,
                                                self.registerMap )
        mock_template = unittest.mock.create_autospec( jinja2.Template )
        with unittest.mock.patch( CREATE_DIRECTORY_MODULE_PATH,
                                  return_value = True ), \
             unittest.mock.patch( OPEN_MODULE_PATH ), \
             unittest.mock.patch.object( registerMap.export.base.template.jinja2.Environment,
                                         'get_template',
                                         return_value = mock_template ) :
            outputUnderTest.apply()

        expectedFiles = [
            'include/path/registerMap.hpp',
            'source/path/someName.cpp',
        ]

        self.assertEqual( expectedFiles, outputUnderTest.createdFiles )


    def testHeader( self ) :
        expectedLines = [
            '/*\n',
            ' *\n',
            ' * someName\n',
            ' *\n',
            ' *\n',
            ' */\n',
            '\n',
            '#ifndef SOMENAME_HPP\n',
            '#define SOMENAME_HPP\n',
            '\n',
            '#include "this/prefix/modules/m1.hpp"\n',
            '\n',
            '\n',
            'namespace someName\n',
            '{\n',
            '\n',
            '#pragma pack( 10 )\n',
            '\n',
            '  class someName_t\n',
            '  {\n',
            '    public:\n',
            '      MemorySpace memory;\n',
            '\n',
            '      someName_t() :\n',
            '          m1( reinterpret_cast<m1_t volatile* const>( memory.base + 0x0 ) )\n',
            '        {};\n',
            '\n',
            '      m1_t volatile* const m1;\n',
            '  };\n',
            '\n',
            '#pragma pack()\n',
            '\n',
            '\n',
            '  // Declare the register map instance for users.\n',
            '  extern someName_t someName;\n',
            '\n',
            '}\n',
            '\n',
            '#endif'
            '\n',
        ]

        paths = RegisterMapTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.sourceDirectory

        self.registerMap.memory.alignment = 10

        outputUnderTest = RegisterMapTemplates( paths,
                                                self.registerMap )
        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH,
                                      suppressModulePath = SOURCE_MODULE_PATH )
        expectedText = ''.join( expectedLines )
        actualText = ''.join( actualLines )
        self.assertEqual( expectedText, actualText )


    def testSource( self ) :
        expectedText = """/*
 *
 * someName
 *
 *
 */

#include "this/prefix/registerMap.hpp"


namespace someName
{

  someName_t someName;

}
"""
        paths = RegisterMapTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.sourceDirectory

        outputUnderTest = RegisterMapTemplates( paths,
                                                self.registerMap )
        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH,
                                      suppressModulePath = HEADER_MODULE_PATH )

        actualText = ''.join( actualLines )
        self.assertEqual( expectedText, actualText )


if __name__ == '__main__' :
    unittest.main()
