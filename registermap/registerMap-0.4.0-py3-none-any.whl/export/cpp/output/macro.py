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

from registerMap.export.commonCppC.output import MacroTemplatesBase

from .base import CPP_TEMPLATE_PACKAGE


MACRO_TEMPLATE_CONFIGURATION = {
    'files' : [
        {
            'file' : 'assert.hpp',
            'template' : 'assert_template.hpp',
        },
    ],
    'template-package' : CPP_TEMPLATE_PACKAGE,
}


class MacroTemplates( MacroTemplatesBase ) :

    def __init__( self, paths, registerMapName,
                  licenseTextLines = None,
                  suffixes = list() ) :
        super().__init__( paths, MACRO_TEMPLATE_CONFIGURATION, registerMapName,
                          licenseTextLines = licenseTextLines,
                          suffixes = suffixes )
