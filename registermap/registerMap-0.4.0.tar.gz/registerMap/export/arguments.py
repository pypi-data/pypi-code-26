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

import argparse

from .options import ExporterOptions
from .exporters import exporters


languages = [
    'c++',
    'c',
]


class MainParser :
    def __init__( self ) :
        self.parser = argparse.ArgumentParser(
            description = 'Export a register map to a language implementation',
            usage = '''export-map <register map YAML file> [<export options>] <language> [<language options>]

Supported languages include:
    {0}
'''.format( '\n    '.join( languages ) )
        )

        self.__applyTopLevelArguments()

        languageParsers = self.parser.add_subparsers(
            dest = 'language',
            help = 'Output language selection.',
            title = 'language'
        )

        # All the language parser instances need to be instantiated at this point because the command line parsing
        # hasn't occured yet so we don't know what language is being selected.
        self.languageParserInstances = {
            x : y( languageParsers ) for x, y in exporters.items()
        }


    def __applyTopLevelArguments( self ) :
        self.parser.add_argument(
            'registerMapFile',
            help = 'Append to an existing distribution package, if it exists. Created otherwise. (default disabled)'
        )

        self.parser.add_argument(
            '-n', '--registermap-name',
            default = 'registerMap',
            help = 'Register map name. (default "registerMap")'
        )

        self.parser.add_argument(
            '-l', '--license-file',
            default = None,
            help = 'License text file. Text must be line formatted to be incorporated into exporter generated output boilerplate.'
        )


    def parse_args( self, commandLineArguments ) :
        args = self.parser.parse_args( commandLineArguments )

        return args


def parseArguments( arguments ) :
    thisParser = MainParser()

    parsedArguments = thisParser.parse_args( arguments )

    options = ExporterOptions()
    options.language = parsedArguments.language
    options.licenseFile = parsedArguments.license_file
    options.registerMapFile = parsedArguments.registerMapFile
    options.registerMapName = parsedArguments.registermap_name

    if options.language is None :
        raise RuntimeError( 'Language must be specified' )

    # Acquire language specific options
    options.languageOptions = thisParser.languageParserInstances[ options.language ].acquireOptions( parsedArguments )

    options.output = parsedArguments.output

    return options
