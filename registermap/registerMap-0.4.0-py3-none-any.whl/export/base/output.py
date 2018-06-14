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

from .interface import OutputInterface

log = logging.getLogger( __name__ )


class OutputBase( OutputInterface ) :

    def __init__( self, outputOptions,
                  licenseTextLines = list() ) :
        self.createdDirectories = list()
        self.createdFiles = list()

        self.licenseTextLines = licenseTextLines

        self.outputOptions = outputOptions

        self.__validateOutputDirectory()


    def __validateOutputDirectory( self ) :
        if not os.path.isdir( self.outputOptions.output ) :
            raise RuntimeError( 'Output directory is not a directory, {0}'.format( self.outputOptions.output ) )


    @property
    def outputDirectory( self ) :
        return self.outputOptions.output


    def createDirectory( self, thisDir ) :
        os.makedirs( thisDir,
                     exist_ok = True )
        self.createdDirectories.append( thisDir )
        log.debug( 'Created directory, {0}'.format( self.createdDirectories[ -1 ] ) )
