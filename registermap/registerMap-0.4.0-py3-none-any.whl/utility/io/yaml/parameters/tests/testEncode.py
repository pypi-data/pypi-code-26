#
# Copyright 2017 Russell Smiley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import unittest

import registerMap.utility.io.yaml.parameters.encode as rmyce
import registerMap.utility.io.yaml.stream as rmycs


class TestEncodeParameter( unittest.TestCase ) :
    @classmethod
    def setUpClass( cls ) :
        thisDir = os.path.dirname( os.path.realpath( __file__ ) )
        cls.__dataDir = os.path.join( thisDir, 'data' )


    def testSaveLoad( self ) :
        filePathName = os.path.join( self.__dataDir, (self.testSaveLoad.__name__ + '.yml') )
        yamlData = rmyce.parameter( 'someParameter', 10 )

        _testSaveLoad( self, filePathName, yamlData )


def _testSaveLoad( instance, filePathName, yamlData ) :
    try :
        rmycs.save( filePathName, yamlData )

        recoveredData = rmycs.load( filePathName )

        instance.assertEqual( yamlData, recoveredData )
    finally :
        if os.path.exists( filePathName ) :
            os.remove( filePathName )


if __name__ == '__main__' :
    unittest.main( )
