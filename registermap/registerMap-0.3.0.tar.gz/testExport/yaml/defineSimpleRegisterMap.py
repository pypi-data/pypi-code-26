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
import os
import sys
import yaml

from registerMap import RegisterMap


def parseArguments( commandLineArguments ) :
    parser = argparse.ArgumentParser( description = 'Generate test-export.yml' )
    parser.add_argument( 'output',
                         help = 'Path to directory location of test-export.yml' )

    arguments = parser.parse_args( commandLineArguments )

    return arguments.output


def main() :
    outputDir = parseArguments( sys.argv[ 1 : ] )
    rm = RegisterMap()

    m1 = rm.addModule( 'm1' )

    # Define a 2 byte register
    r1 = m1.addRegister( 'r1' )
    f1 = r1.addField( 'f1', (0, 10) )

    m2 = rm.addModule( 'm2' )

    # Define a multi field single byte register
    m2r2 = m2.addRegister( 'r2' )
    f2 = m2r2.addField( 'f2', (0, 3) )
    f3 = m2r2.addField( 'f3', (4, 6) )

    # Define a multi field register with non contiguous fields
    r3 = m2.addRegister( 'r3' )
    f4 = r3.addField( 'f4', (2, 3) )
    f5 = r3.addField( 'f5', (5, 7) )

    m3 = rm.addModule( 'm3' )

    # Define a register with the same name as a register in another module
    m3r2 = m3.addRegister( 'r2' )
    # Define the field as the same size as m2.r2.f2 for convenience of comparing in a test.
    f6 = m3r2.addField( 'f6', (0, 3) )

    # Define a register at a fixed address such that there is a gap between it and the previous register.
    # Make sure the fixed address is not on a word boundary.
    r4 = m3.addRegister( 'r4' )
    r4[ 'constraints' ][ 'fixedAddress' ] = 0x21

    f7 = r4.addField( 'f7', (0, 31) )

    yamlData = rm.to_yamlData()
    with open( os.path.join( outputDir, 'test-export.yml' ), 'w' ) as fileObject :
        yaml.dump( yamlData, fileObject )


if __name__ == '__main__' :
    main()
