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
import logging
import os


log = logging.getLogger( __name__ )


class TemplateBase :
    """
    Base functionality for management of templates.
    """


    class Paths :

        def __init__( self ) :
            self.includeDirectory = None
            self.includePrefix = None
            self.sourceDirectory = None
            self.templatePackagePath = None


    def __init__( self, paths,
                  licenseTextLines = None,
                  subdir = None,
                  suffixes = list() ) :
        self.__constructTemplateDirectoryPath( subdir )

        self.createdDirectories = list()
        self.createdFiles = list()

        self.licenseTextLines = licenseTextLines
        self.paths = paths

        self.environment = jinja2.Environment( autoescape = jinja2.select_autoescape( suffixes ),
                                               keep_trailing_newline = True,
                                               loader = jinja2.PackageLoader( self.paths.templatePackagePath,
                                                                              self.templateDirectory ) )


    def __constructTemplateDirectoryPath( self, subdir ) :
        if subdir is None :
            self.templateDirectory = 'templates'
        else :
            self.templateDirectory = os.path.join( 'templates', subdir )

        log.debug( 'Template directory, {0}'.format( self.templateDirectory ) )


    def createDirectory( self, thisDir ) :
        os.makedirs( thisDir,
                     exist_ok = True )
        self.createdDirectories.append( thisDir )
        log.debug( 'Created directory, {0}'.format( self.createdDirectories[ -1 ] ) )
