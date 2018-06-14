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

import logging
import os

from ..base import \
    OutputBase

from .elements import \
    Memory, \
    RegisterMap
from .output import \
    MacroTemplates, \
    MemoryTemplates, \
    ModuleTemplates, \
    RegisterMapTemplates


log = logging.getLogger( __name__ )


class Output( OutputBase ) :
    """
    Export a C source code representation of the register map.
    """


    def __init__( self, outputOptions,
                  licenseTextLines = list() ) :
        super().__init__( outputOptions,
                          licenseTextLines = licenseTextLines )

        self.includePath = None
        self.sourceDirectory = None

        self.suffixes = [ '.hpp', '.cpp' ]


    def __createDirectories( self, registerMapName ) :
        self.includePath = os.path.join( self.outputDirectory,
                                         'include',
                                         self.outputOptions.includePrefix,
                                         registerMapName )
        self.createDirectory( self.includePath )

        self.sourceDirectory = os.path.join( self.outputDirectory, 'source', registerMapName )
        self.createDirectory( self.sourceDirectory )


    def generate( self, registerMap, registerMapName ) :
        """
        Export the register map representation.

        :param registerMap: A RegisterMap instance for export.
        :param registerMapName: A public name for the register map used in source code file structure and object names.
        """
        self.__createDirectories( registerMapName )

        encapsulatedRegisterMap = RegisterMap( registerMapName, registerMap )
        encapsulatedRegisterMap.memory.alignment = self.outputOptions.packAlignment

        paths = MacroTemplates.Paths()
        paths.includeDirectory = self.includePath
        paths.includePrefix = os.path.join( self.outputOptions.includePrefix, registerMapName )
        paths.sourceDirectory = self.sourceDirectory

        buildOrder = [
            MacroTemplates( paths,
                            registerMapName,
                            licenseTextLines = self.licenseTextLines,
                            suffixes = self.suffixes ),
            MemoryTemplates( paths,
                             registerMapName, encapsulatedRegisterMap.memory,
                             licenseTextLines = self.licenseTextLines,
                             suffixes = self.suffixes ),
            ModuleTemplates( paths,
                             encapsulatedRegisterMap,
                             licenseTextLines = self.licenseTextLines,
                             suffixes = self.suffixes ),
            RegisterMapTemplates( paths,
                                  encapsulatedRegisterMap,
                                  licenseTextLines = self.licenseTextLines,
                                  suffixes = self.suffixes ),
        ]

        for build in buildOrder :
            build.apply()
