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

from registerMap.export.cpp.elements.memory import Memory
from registerMap.export.cpp.elements.registerMap import RegisterMap

from registerMap.export.commonCppC.output.tests.common import doTemplateTest

from ..module import ModuleTemplates

import registerMap.export.base.template


CREATE_DIRECTORY_MODULE_PATH = 'registerMap.export.cpp.output.module.ModuleTemplates.createDirectory'
OPEN_MODULE_PATH = 'registerMap.export.commonCppC.output.module.open'


class TestModuleTemplates( unittest.TestCase ) :

    def setUp( self ) :
        self.expectedName = 'someName'
        self.includeDirectory = 'include/path'
        self.sourceDirectory = 'source/path'

        self.__setupRegisterMap()

        self.memory = Memory( self.registerMap.memory, self.registerMap.spanMemoryUnits )


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
        paths = ModuleTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.includeDirectory

        outputUnderTest = ModuleTemplates( paths, self.registerMap )
        mock_template = unittest.mock.create_autospec( jinja2.Template )
        with unittest.mock.patch( CREATE_DIRECTORY_MODULE_PATH,
                                  return_value = True ) as mock_createDirectory, \
                unittest.mock.patch( OPEN_MODULE_PATH ), \
                unittest.mock.patch.object( registerMap.export.base.template.jinja2.Environment,
                                            'get_template',
                                            return_value = mock_template ) :
            outputUnderTest.apply()

        expectedFiles = [
            'include/path/modules/m1.hpp'
        ]

        self.assertEqual( expectedFiles, outputUnderTest.createdFiles )

        mock_template.render.assert_called_once()

        mock_createDirectory.assert_has_calls( [
            unittest.mock.call( outputUnderTest.moduleDirectory ),
        ] )


    def testContiguousFieldsRegisterData( self ) :
        expectedText = \
            """/*
 *
 * Module: m1
 *
 *
 */

#ifndef SOMENAME_M1_HPP
#define SOMENAME_M1_HPP

#include <cstdint>

#include "this/prefix/memory/memory.hpp"


namespace someName
{

  namespace m1
  {

    class r1_t
    {
      public:
        std::uint8_t volatile f1:3;
        std::uint8_t volatile f2:2;
        std::uint16_t volatile f3:11;
    };

  }


#pragma pack(  )

  class m1_t
  {
    public:

      m1::r1_t volatile r1;
  };


#pragma pack()

}


#endif
"""
        paths = ModuleTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.includeDirectory

        outputUnderTest = ModuleTemplates( paths, self.registerMap )
        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH )

        actualText = '{}'.format( ''.join( actualLines ) )
        self.assertEqual( expectedText, actualText )


class TestNoncontiguousRegisterOutput( unittest.TestCase ) :

    def setUp( self ) :
        self.expectedName = 'someName'
        self.includeDirectory = 'include/path'
        self.sourceDirectory = 'source/path'

        registerMap = ImportedRegisterMap()
        registerMap.memory.baseAddress = 0x20f0

        self.m1 = registerMap.addModule( 'm1' )

        self.registerMap = RegisterMap( self.expectedName, registerMap )
        self.memory = Memory( self.registerMap.memory, self.registerMap.spanMemoryUnits )


    def testNoncontiguousFieldsSingleByteRegisterData( self ) :
        r1 = self.m1.addRegister( 'r1' )

        r1.addField( 'f1', (0, 1) )
        r1.addField( 'f2', (4, 5) )
        r1.addField( 'f3', (7, 7) )

        expectedText = \
            """/*
 *
 * Module: m1
 *
 *
 */

#ifndef SOMENAME_M1_HPP
#define SOMENAME_M1_HPP

#include <cstdint>

#include "this/prefix/memory/memory.hpp"


namespace someName
{

  namespace m1
  {

    class r1_t
    {
      public:
        std::uint8_t volatile f1:2;
        std::uint8_t volatile :2;
        std::uint8_t volatile f2:2;
        std::uint8_t volatile :1;
        std::uint8_t volatile f3:1;
    };

  }


#pragma pack(  )

  class m1_t
  {
    public:

      m1::r1_t volatile r1;
  };


#pragma pack()

}


#endif
"""
        paths = ModuleTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.includeDirectory

        outputUnderTest = ModuleTemplates( paths, self.registerMap )
        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH )

        self.assertEqual( expectedText.splitlines( keepends = True ), actualLines )


    def testNoncontiguousFieldsStartsRegisterData( self ) :
        r1 = self.m1.addRegister( 'r1' )

        r1.addField( 'f1', (2, 4) )
        r1.addField( 'f2', (5, 5) )
        r1.addField( 'f3', (7, 7) )

        expectedText = \
            """/*
 *
 * Module: m1
 *
 *
 */

#ifndef SOMENAME_M1_HPP
#define SOMENAME_M1_HPP

#include <cstdint>

#include "this/prefix/memory/memory.hpp"


namespace someName
{

  namespace m1
  {

    class r1_t
    {
      public:
        std::uint8_t volatile :2;
        std::uint8_t volatile f1:3;
        std::uint8_t volatile f2:1;
        std::uint8_t volatile :1;
        std::uint8_t volatile f3:1;
    };

  }


#pragma pack(  )

  class m1_t
  {
    public:

      m1::r1_t volatile r1;
  };


#pragma pack()

}


#endif
"""
        paths = ModuleTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.includeDirectory

        outputUnderTest = ModuleTemplates( paths, self.registerMap )
        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH )

        self.assertEqual( expectedText.splitlines( keepends = True ), actualLines )


    def testNoncontiguousFieldsMultiByteRegisterData( self ) :
        r1 = self.m1.addRegister( 'r1' )

        r1.addField( 'f1', (0, 1) )
        r1.addField( 'f2', (4, 5) )
        r1.addField( 'f3', (7, 9) )

        expectedText = \
            """/*
 *
 * Module: m1
 *
 *
 */

#ifndef SOMENAME_M1_HPP
#define SOMENAME_M1_HPP

#include <cstdint>

#include "this/prefix/memory/memory.hpp"


namespace someName
{

  namespace m1
  {

    class r1_t
    {
      public:
        std::uint8_t volatile f1:2;
        std::uint8_t volatile :2;
        std::uint8_t volatile f2:2;
        std::uint8_t volatile :1;
        std::uint8_t volatile f3:3;
        std::uint8_t volatile :6;
    };

  }


#pragma pack(  )

  class m1_t
  {
    public:

      m1::r1_t volatile r1;
  };


#pragma pack()

}


#endif
"""
        paths = ModuleTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.includeDirectory

        outputUnderTest = ModuleTemplates( paths, self.registerMap )
        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH )

        actualText = ''.join( actualLines )
        self.assertEqual( expectedText, actualText )


class TestEmptyModuleOutput( unittest.TestCase ) :

    def setUp( self ) :
        self.expectedName = 'someName'
        self.includeDirectory = 'include/path'
        self.sourceDirectory = 'source/path'

        registerMap = ImportedRegisterMap()
        registerMap.memory.baseAddress = 0x20f0

        m1 = registerMap.addModule( 'm1' )

        self.moduleUnderTest = m1

        self.registerMap = RegisterMap( self.expectedName, registerMap )


    def testNoRegistersEmptyFile( self ) :
        expectedText = \
            """/*
 *
 * Module: m1
 *
 *
 */

#ifndef SOMENAME_M1_HPP
#define SOMENAME_M1_HPP

#include <cstdint>

#include "this/prefix/memory/memory.hpp"


// someName::m1 is an empty module

#endif
"""
        paths = ModuleTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.includeDirectory

        outputUnderTest = ModuleTemplates( paths, self.registerMap )
        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH )

        actualText = ''.join( actualLines )
        self.assertEqual( expectedText, actualText )


    def testLicenseLines( self ) :
        expectedText = \
            """/*
 *
 * Module: m1
 *
 * This is a license text.
 * There could be some copyright applied.
 * Or any other distribution limitations.
 *
 */

#ifndef SOMENAME_M1_HPP
#define SOMENAME_M1_HPP

#include <cstdint>

#include "this/prefix/memory/memory.hpp"


// someName::m1 is an empty module

#endif
"""

        inputLicense = [
            'This is a license text.',
            'There could be some copyright applied.',
            'Or any other distribution limitations.',
        ]

        paths = ModuleTemplates.Paths()
        paths.includeDirectory = self.includeDirectory
        paths.includePrefix = 'this/prefix'
        paths.sourceDirectory = self.includeDirectory

        outputUnderTest = ModuleTemplates( paths, self.registerMap,
                                           licenseTextLines = inputLicense )
        actualLines = doTemplateTest( outputUnderTest,
                                      OPEN_MODULE_PATH,
                                      CREATE_DIRECTORY_MODULE_PATH )

        actualText = ''.join( actualLines )
        self.assertEqual( expectedText, actualText )


if __name__ == '__main__' :
    unittest.main()
