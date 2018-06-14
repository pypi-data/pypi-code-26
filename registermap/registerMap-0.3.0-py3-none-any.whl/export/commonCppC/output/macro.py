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

import os

from registerMap.export.base import \
    TemplateBase, \
    TemplateInterface


class MacroTemplatesBase( TemplateInterface, TemplateBase ) :

    def __init__( self, paths, configuration, registerMapName,
                  licenseTextLines = None,
                  suffixes = list() ) :
        paths.templatePackagePath = configuration[ 'template-package' ]

        super().__init__( paths,
                          licenseTextLines = licenseTextLines,
                          subdir = 'macro',
                          suffixes = suffixes )

        self.configuration = configuration
        self.macroDirectory = os.path.join( self.paths.includeDirectory, 'macro' )
        self.registerMapName = registerMapName


    def apply( self ) :
        self.createDirectory( self.macroDirectory )

        for thisTemplate in self.configuration[ 'files' ] :
            self.__createHeader( thisTemplate[ 'file' ], thisTemplate[ 'template' ] )


    def __createHeader( self, file, template ) :
        assertHeader = os.path.join( self.macroDirectory, file )

        template = self.environment.get_template( template )
        with open( assertHeader, 'w' ) as headerFile :
            text = template.render( registerMapName = self.registerMapName,
                                    licenseText = self.licenseTextLines )
            headerFile.write( text )

            self.createdFiles.append( assertHeader )
