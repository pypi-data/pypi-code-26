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

from registerMap.export.commonCppC.output import RegisterMapTemplatesBase

from ..elements import RegisterMap

from .base import CPP_TEMPLATE_PACKAGE


REGISTERMAP_TEMPLATE_CONFIGURATION = {
    'registermap' : 'registerMap.hpp',
    'header-template' : 'registerMap_template.hpp',
    'source-template' : 'registerMap_template.cpp',
    'source-suffix' : 'cpp',
    'registermap-type' : RegisterMap,
    'template-package' : CPP_TEMPLATE_PACKAGE,
}


class RegisterMapTemplates( RegisterMapTemplatesBase ) :

    def __init__( self, paths, encapsulatedRegisterMap,
                  licenseTextLines = None,
                  suffixes = list() ) :
        paths.templatePackagePath = REGISTERMAP_TEMPLATE_CONFIGURATION[ 'template-package' ]

        super().__init__( paths, REGISTERMAP_TEMPLATE_CONFIGURATION, encapsulatedRegisterMap,
                          licenseTextLines = licenseTextLines,
                          suffixes = suffixes )
