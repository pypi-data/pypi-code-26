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

from ..options import CppOptions
from ..registerMap import Output as CppOutput


BASE_MODULE_PATH = 'registerMap.export.cpp.registerMap'


class TestCRegisterMapHeaderSource( unittest.TestCase ) :

    def setUp( self ) :
        self.outputDir = 'some/path'

        self.__setupRegisterMap()

        self.mock_options = CppOptions()
        self.mock_options.includePrefix = 'this/prefix'
        self.mock_options.output = self.outputDir
        self.mock_options.packAlignment = 10


    def __setupRegisterMap( self ) :
        self.registerMap = RegisterMap()

        self.registerMap.memory.baseAddress = 0x20f0

        m1 = self.registerMap.addModule( 'm1' )
        r1 = m1.addRegister( 'r1' )
        r1.addField( 'f1', (0, 11) )

        m2 = self.registerMap.addModule( 'm2' )
        r2 = m2.addRegister( 'r2' )
        r2.addField( 'f2', (0, 4) )

        m3 = self.registerMap.addModule( 'm3' )
        r3 = m3.addRegister( 'r3' )
        r3.addField( 'f3', (4, 6) )


    def testExecution( self ) :
        with unittest.mock.patch(
                '{0}.OutputBase._OutputBase__validateOutputDirectory'.format( BASE_MODULE_PATH ) ), \
             unittest.mock.patch(
                 'registerMap.export.cpp.registerMap.MacroTemplates'.format( BASE_MODULE_PATH ) ) as \
                mock_MacroTemplate, \
                unittest.mock.patch(
                    '{0}.MemoryTemplates'.format( BASE_MODULE_PATH ) ) as mock_MemoryTemplate, \
                unittest.mock.patch(
                    '{0}.ModuleTemplates'.format( BASE_MODULE_PATH ) ) as mock_ModuleTemplate, \
                unittest.mock.patch( '{0}.RegisterMapTemplates'.format( BASE_MODULE_PATH ) ) as \
                        mock_RegisterMapTemplate, \
                unittest.mock.patch( '{0}.Output._Output__createDirectories'.format( BASE_MODULE_PATH ) ) :
            outputUnderTest = CppOutput( self.mock_options )

            # Mock created directory paths
            outputUnderTest.includePath = 'some/include'
            outputUnderTest.sourceDirectory = 'some/source'

            outputUnderTest.generate( self.registerMap, 'myRegisterMap' )

            mock_macroTemplateInstance = mock_MacroTemplate.return_value
            mock_macroTemplateInstance.apply.assert_called_once()

            mock_memoryTemplateInstance = mock_MemoryTemplate.return_value
            mock_memoryTemplateInstance.apply.assert_called_once()

            mock_moduleTemplateInstance = mock_ModuleTemplate.return_value
            mock_moduleTemplateInstance.apply.assert_called_once()

            mock_registerMapTemplateInstance = mock_RegisterMapTemplate.return_value
            mock_registerMapTemplateInstance.apply.assert_called_once()


if __name__ == '__main__' :
    unittest.main()
