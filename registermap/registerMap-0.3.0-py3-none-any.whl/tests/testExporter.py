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

import io
import unittest.mock
import yaml

from ..exporter import \
    acquireRegisterMap, \
    main
from ..registerMap import RegisterMap
from ..export.arguments import parseArguments
from ..export.cpp.registerMap import Output


class ParseArgumentsSideEffect :
    def __init__( self ) :
        self.mock_generator = None
        self.options = None


    def __call__( self, commandLineArguments ) :
        self.options = parseArguments( commandLineArguments )

        self.mock_generator = unittest.mock.create_autospec( Output )
        self.options.languageOptions.generator = self.mock_generator

        return self.options


class TestAcquireRegisterMap( unittest.TestCase ) :
    def testEmptyRegisterMap( self ) :
        mock_yamlContent = io.StringIO( '' )
        with unittest.mock.patch( 'registerMap.exporter.open',
                                  return_value = mock_yamlContent ) :
            actualValue = acquireRegisterMap( 'some/path' )

            self.assertIsNone( actualValue )


class TestExporter( unittest.TestCase ) :
    def setUp( self ) :
        self.parserSideEffect = ParseArgumentsSideEffect()
        self.registerMap = RegisterMap()

        m1 = self.registerMap.addModule( 'm1' )
        r1 = m1.addRegister( 'r1' )
        r1.addField( 'f1', (0, 10) )

        r2 = m1.addRegister( 'r2' )
        r2.addField( 'f1', (0, 2) )
        r2.addField( 'f2', (5, 7) )


    def testExporterSequence( self ) :
        inputValue = [
            'registerMap/path',
            '--license-file',
            'licenseFile/text',
            'c++',
            'output/path'
        ]
        expectedLicenseLines = [
            'a small\n',
            'license text\n',
        ]
        inputLicenseText = ''.join( expectedLicenseLines )

        with unittest.mock.patch( 'registerMap.exporter.parseArguments',
                                  side_effect = self.parserSideEffect ), \
             unittest.mock.patch( 'registerMap.exporter.open',
                                  return_value = io.StringIO( inputLicenseText ) ), \
             unittest.mock.patch( 'registerMap.exporter.acquireRegisterMap',
                                  return_value = self.registerMap ) as mock_acquireRegisterMap :
            main( inputValue )

            mock_acquireRegisterMap.assert_called_once_with( self.parserSideEffect.options.registerMapFile )

            # Check that the generator was instantiated correctly.
            self.parserSideEffect.mock_generator.assert_called_once_with(
                self.parserSideEffect.options.languageOptions,
                licenseTextLines = expectedLicenseLines )

            # Check that the generate method was called correctly.
            generatorInstance = self.parserSideEffect.mock_generator.return_value
            generatorInstance.generate.assert_called_once_with( self.registerMap,
                                                                self.parserSideEffect.options.registerMapName )


    def testLicenseFileNone( self ) :
        inputValue = [
            'registerMap/path',
            'c++',
            'output/path'
        ]

        with unittest.mock.patch( 'registerMap.exporter.parseArguments',
                                  side_effect = self.parserSideEffect ), \
             unittest.mock.patch( 'registerMap.exporter.acquireRegisterMap',
                                  return_value = self.registerMap ) as mock_acquireRegisterMap :
            main( inputValue )

            mock_acquireRegisterMap.assert_called_once_with( self.parserSideEffect.options.registerMapFile )

            mock_generatorInstance = self.parserSideEffect.mock_generator.return_value
            mock_generatorInstance.generate.assert_called_once_with( self.registerMap,
                                                                     self.parserSideEffect.options.registerMapName )

            # Check for the default register map name since no license file specified.
            self.assertEqual( 'registerMap', self.parserSideEffect.options.registerMapName )


if __name__ == '__main__' :
    unittest.main()
