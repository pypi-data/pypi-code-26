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

from ..base.interface import LanguageParser

from .options import CppOptions
from .registerMap import Output


class CppArgumentParser( LanguageParser ) :

    def __init__( self, parentParser ) :
        self.parser = parentParser.add_parser( 'c++' )

        self.parser.add_argument( 'output',
                                  help = 'Directory to place the generated files. Created if not present.' )
        self.parser.add_argument( '--pack',
                                  default = None,
                                  help = 'Pragma pack alignment value. Default None.',
                                  nargs = 1,
                                  type = int )
        self.parser.add_argument( '--include-prefix',
                                  default = [ '' ],
                                  help = 'Prefix path to register map include files. Default None.',
                                  nargs = 1,
                                  type = str )


    def acquireOptions( self, parserProcessedArguments ) :
        options = CppOptions()

        options.generator = Output
        options.output = parserProcessedArguments.output
        if parserProcessedArguments.pack is not None :
            options.packAlignment = parserProcessedArguments.pack[ 0 ]
        else :
            options.packAlignment = None
        if parserProcessedArguments.include_prefix is not None :
            options.includePrefix = parserProcessedArguments.include_prefix[ 0 ]
        else :
            options.includePrefix = None

        return options
