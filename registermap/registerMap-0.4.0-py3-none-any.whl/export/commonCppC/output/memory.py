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


class MemoryTemplatesBase( TemplateInterface, TemplateBase ) :

    def __init__( self, paths, configuration, registerMapName, encapsulatedMemory,
                  licenseTextLines = None,
                  suffixes = list() ) :
        paths.templatePackagePath = configuration[ 'template-package' ]

        super().__init__( paths,
                          licenseTextLines = licenseTextLines,
                          subdir = 'idiomatic',
                          suffixes = suffixes )

        self.configuration = configuration
        self.encapsulatedMemory = encapsulatedMemory
        self.memoryDirectory = os.path.join( self.paths.includeDirectory, 'memory' )
        self.registerMapName = registerMapName

        self.__TEMPLATE_GENERATORS = {
            'header' : self.__createHeader,
            'source' : self.__createSource,
        }


    def apply( self ) :
        assert self.memoryDirectory is not None

        self.createDirectory( self.memoryDirectory )

        for id, createFileMethod in self.__TEMPLATE_GENERATORS.items() :
            for thisTemplate in self.configuration[ id ] :
                createFileMethod( thisTemplate[ 'file' ], thisTemplate[ 'template' ] )


    def __createHeader( self, file, template ) :
        targetSource = os.path.join( self.memoryDirectory, file )

        template = self.environment.get_template( template )
        with open( targetSource, 'w' ) as sourceFile :
            text = template.render( licenseText = self.licenseTextLines,
                                    memory = self.encapsulatedMemory,
                                    prefixPath = self.paths.includePrefix,
                                    registerMapName = self.registerMapName )
            sourceFile.write( text )

            self.createdFiles.append( targetSource )


    def __createSource( self, file, template ) :
        targetSource = os.path.join( self.paths.sourceDirectory, file )

        template = self.environment.get_template( template )
        with open( targetSource, 'w' ) as sourceFile :
            text = template.render( licenseText = self.licenseTextLines,
                                    memory = self.encapsulatedMemory,
                                    prefixPath = self.paths.includePrefix,
                                    registerMapName = self.registerMapName )
            sourceFile.write( text )

            self.createdFiles.append( targetSource )
