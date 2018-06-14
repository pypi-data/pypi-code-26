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

import yaml


def load( filename ) :
    data = None
    with open( filename, 'r' ) as yamlFile :
        data = yaml.load( yamlFile )

    assert (data is not None)

    return data


def save( filename, data ) :
    with open( filename, 'w' ) as yamlFile :
        yaml.dump( data, yamlFile )
