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
import sys
import yaml

from .registerMap import RegisterMap
from .export import parseArguments


log = logging.getLogger( __name__ )


def acquireLicenseText( licenseTextFile ) :
    if licenseTextFile is not None :
        with open( licenseTextFile, 'r' ) as fileObject :
            licenseTextLines = fileObject.readlines()
    else :
        licenseTextLines = list()

    return licenseTextLines


def acquireRegisterMap( registerMapFile ) :
    with open( registerMapFile, 'r' ) as fileObject :
        yamlData = yaml.safe_load( fileObject )

    if yamlData is None :
        # Register map file was empty
        registerMap = None
    else :
        registerMap = RegisterMap.from_yamlData( yamlData )

    return registerMap


def main( commandLineArguments ) :
    exporterOptions = parseArguments( commandLineArguments )

    licenseText = acquireLicenseText( exporterOptions.licenseFile )
    registerMap = acquireRegisterMap( exporterOptions.registerMapFile )

    if registerMap is None :
        log.warning( 'Empty register map exports no code, {0}'.format( exporterOptions.registerMapFile ) )
    else :
        thisGenerator = exporterOptions.languageOptions.generator( exporterOptions.languageOptions,
                                                                   licenseTextLines = licenseText )

        thisGenerator.generate( registerMap, exporterOptions.registerMapName )


def entry() :
    main( sys.argv[ 1 : ] )


if __name__ == '__main__' :
    main( sys.argv[ 1 : ] )
