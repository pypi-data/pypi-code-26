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

import io
import unittest.mock


class KeepString( io.StringIO ) :
    """
    Retain the lines written to io.StringIO before it is closed (at which point they are discarded).
    """


    def __init__( self, *args, **kwargs ) :
        super().__init__( *args, **kwargs )

        self.outputLines = None


    def close( self ) :
        self.seek( 0 )
        self.outputLines = self.readlines()

        super().close()


def doTemplateTest( outputUnderTest, openModulePath, createDirectoryModulePath,
                    suppressModulePath = None ) :
    """
    Acquire the output
    :param outputUnderTest:
    :param openModulePath:
    :param createDirectoryModulePath:
    :param suppressModulePath:
    """
    mock_fileObject = KeepString()
    with unittest.mock.patch( createDirectoryModulePath,
                              return_value = True ), \
         unittest.mock.patch( openModulePath,
                              unittest.mock.mock_open() ) as mock_memoryOpen :
        mock_memoryOpen.return_value = mock_fileObject

        if suppressModulePath is None :
            # apply the output for testing
            outputUnderTest.apply()
        else :
            # mock the module path to be suppresed.
            with unittest.mock.patch( suppressModulePath ) :
                outputUnderTest.apply()

    return mock_fileObject.outputLines
