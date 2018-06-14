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


class RegisterMapTemplatesBase( TemplateInterface, TemplateBase ) :

    def __init__( self, paths, configuration, encapsulatedRegisterMap,
                  licenseTextLines = None,
                  suffixes = list() ) :
        super().__init__( paths,
                          licenseTextLines = licenseTextLines,
                          subdir = 'idiomatic',
                          suffixes = suffixes )

        self.configuration = configuration
        self.encapsulatedRegisterMap = encapsulatedRegisterMap


    def apply( self ) :
        self.__createRegisterMapHeader( self.encapsulatedRegisterMap )
        self.__createRegisterMapSource( self.encapsulatedRegisterMap, self.encapsulatedRegisterMap.memory )


    def __createRegisterMapHeader( self, registerMap ) :
        registerMapHeader = os.path.join( self.paths.includeDirectory, self.configuration[ 'registermap' ] )

        template = self.environment.get_template( self.configuration[ 'header-template' ] )
        with open( registerMapHeader, 'w' ) as headerFile :
            text = template.render( licenseText = self.licenseTextLines,
                                    prefixPath = self.paths.includePrefix,
                                    registerMap = registerMap )
            headerFile.write( text )

            self.createdFiles.append( registerMapHeader )


    def __createRegisterMapSource( self, registerMap, memory ) :
        registerMapSource = os.path.join( self.paths.sourceDirectory,
                                          '{0}.{1}'.format(
                                              registerMap.name,
                                              self.configuration[ 'source-suffix' ] ) )

        template = self.environment.get_template( self.configuration[ 'source-template' ] )
        with open( registerMapSource, 'w' ) as sourceFile :
            text = template.render( licenseText = self.licenseTextLines,
                                    memory = memory,
                                    prefixPath = self.paths.includePrefix,
                                    registerMap = registerMap )
            sourceFile.write( text )
            self.createdFiles.append( registerMapSource )
