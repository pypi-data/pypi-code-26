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


class ModuleTemplatesBase( TemplateInterface, TemplateBase ) :

    def __init__( self, paths, configuration, encapsulatedRegisterMap,
                  licenseTextLines = None,
                  suffixes = list() ) :
        paths.templatePackagePath = configuration[ 'template-package' ]

        self.configuration = configuration
        super().__init__( paths,
                          licenseTextLines = licenseTextLines,
                          subdir = 'idiomatic',
                          suffixes = suffixes )

        self.moduleDirectory = None
        self.encapsulatedRegisterMap = encapsulatedRegisterMap


    def apply( self ) :
        self.moduleDirectory = os.path.join( self.paths.includeDirectory, 'modules' )
        self.createDirectory( self.moduleDirectory )

        moduleElements = self.encapsulatedRegisterMap.modules
        self.__createModuleFiles( self.encapsulatedRegisterMap.name, self.encapsulatedRegisterMap.memory,
                                  moduleElements )


    def __createModuleFiles( self, registerMapName, memory, moduleElements ) :
        template = self.environment.get_template( self.configuration[ 'module-template' ] )
        for thisModule in moduleElements :
            thisModuleFile = os.path.join( self.moduleDirectory,
                                           '{0}.{1}'.format( thisModule.name,
                                                             self.configuration[ 'header-suffix' ]
                                                             )
                                           )

            with open( thisModuleFile, 'w' ) as sourceFile :
                text = template.render( licenseText = self.licenseTextLines,
                                        memory = memory,
                                        module = thisModule,
                                        prefixPath = self.paths.includePrefix,
                                        registerMapMemoryAlignment = self.encapsulatedRegisterMap.memory.alignment,
                                        registerMapName = registerMapName )
                sourceFile.write( text )

            self.createdFiles.append( thisModuleFile )
