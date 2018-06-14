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


def parameter( parameterName, value ) :
    """
    Encode a simple parameter for yaml data.

    :param parameterName: Name of yaml parameter.
    :param value: Parameter value in a format suitable for output to yaml.
    :return: Yaml data structure.
    """
    return { parameterName : value }

# From http://stackoverflow.com/questions/18666816/using-python-to-dump-hexidecimals-into-yaml
class HexInt( int ) :
    pass


def hexIntRepresenter( dumper, data ) :
    return yaml.ScalarNode( 'tag:yaml.org,2002:int', hex( data ) )


yaml.add_representer( HexInt, hexIntRepresenter )
