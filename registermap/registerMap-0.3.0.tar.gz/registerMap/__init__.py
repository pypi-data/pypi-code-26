#
# Copyright 2016 Russell Smiley
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

"""
A Python 3 framework for creating and maintaining register maps for integrated circuit design and embedded
software development.
"""

import os.path


here = os.path.abspath( os.path.dirname( __file__ ) )
versionFilePath = os.path.abspath( os.path.join( here, 'VERSION' ) )

with open( versionFilePath ) as version_file :
    version = version_file.read().strip()

__version__ = version

from .exceptions import \
    ConfigurationError, \
    ParseError

from .registerMap import RegisterMap
