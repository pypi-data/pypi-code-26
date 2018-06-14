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

CREATE_DIRECTORY_MODULE_PATH = 'registerMap.export.c.output.registerMap.RegisterMapTemplates.createDirectory'
OPEN_MODULE_PATH = 'registerMap.export.commonCppC.output.registerMap.open'

HEADER_MODULE_PATH = 'registerMap.export.c.output.registerMap.RegisterMapTemplatesBase' \
                     '._RegisterMapTemplatesBase__createRegisterMapHeader'
SOURCE_MODULE_PATH = 'registerMap.export.c.output.registerMap.RegisterMapTemplatesBase' \
                     '._RegisterMapTemplatesBase__createRegisterMapSource'


class TestCRegisterMapTemplates( unittest.TestCase ) :

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

        self.registerMap = RegisterMap(self.expectedName, registerMap)


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
            'include/path/registerMap.h',
            'source/path/someName.c',
        ]

        self.assertEqual( expectedFiles, outputUnderTest.createdFiles )


    def testHeader( self ) :
        expectedText = """/*
 *
 * someName
 *
 *
 */

#ifndef SOMENAME_H
#define SOMENAME_H

#include "this/prefix/macro/extern.h"
#include "this/prefix/memory/memory.h"

#include "this/prefix/modules/m1.h"


SOMENAME_OPEN_EXTERN_C

#pragma pack( 10 )

struct someName_t
{
  struct m1_t volatile* const m1;
};

#pragma pack()


// Declare the register map instance for users.
extern struct MemorySpace_t someName_memory;
extern struct someName_t someName;

SOMENAME_CLOSE_EXTERN_C

#endif
"""
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

        actualText = ''.join(actualLines)
        self.assertEqual( expectedText, actualText )


    def testSource( self ) :
        expectedText = """/*
 *
 * someName
 *
 *
 */

#include "this/prefix/macro/extern.h"
#include "this/prefix/memory/memory.h"
#include "this/prefix/registerMap.h"


SOMENAME_OPEN_EXTERN_C

#ifdef OFF_TARGET_MEMORY

struct MemorySpace_t myRegisterMap_memory = {
  .allocated_memory_span = 2,
};

#else

struct MemorySpace_t myRegisterMap_memory = {
  .allocated_memory_span = 2,
  .base = ( uint8_t volatile* const ) 0x20f0,
};

#endif

struct someName_t someName = {
  .m1 = ( m1_t volatile* const )( someName_memory.base + 0x0 ),
};

SOMENAME_CLOSE_EXTERN_C
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
