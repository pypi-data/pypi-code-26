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

from registerMap.export.commonCppC.output import MemoryTemplatesBase

from .base import C_TEMPLATE_PACKAGE


MEMORY_TEMPLATE_CONFIGURATION = {
    'header' : [
        {
            'file' : 'memory.h',
            'template' : 'memory_template.h',
        },
    ],
    'source' : [
        # There are no source files for the C memory implementation.
    ],
    'template-package' : C_TEMPLATE_PACKAGE,
}


class MemoryTemplates( MemoryTemplatesBase ) :

    def __init__( self, paths, registerMapName, encapsulatedMemory,
                  licenseTextLines = None,
                  suffixes = list() ) :
        super().__init__( paths, MEMORY_TEMPLATE_CONFIGURATION, registerMapName, encapsulatedMemory,
                          licenseTextLines = licenseTextLines,
                          suffixes = suffixes )
