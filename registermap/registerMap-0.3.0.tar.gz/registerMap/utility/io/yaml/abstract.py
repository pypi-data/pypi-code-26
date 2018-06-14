#
# Copyright 2017 Russell Smiley
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

import abc


class Import( metaclass = abc.ABCMeta ) :
    @classmethod
    @abc.abstractmethod
    def from_yamlData( cls, yamlData ) :
        '''
        Use yamlData to initialize the object.

        :param yamlData: YAML data loaded using yaml.load
        :return: Created instance of class.
        '''
        return


class Export( metaclass = abc.ABCMeta ) :
    @abc.abstractmethod
    def to_yamlData( self ) :
        '''
        Create the YAML data structure to be used by yaml.dump for YAML export.

        :return: YAML data structure
        '''
        return
