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

from registerMap.export.commonCppC.output import ModuleTemplatesBase

from ..elements import \
    Field, \
    Module, \
    Register

from .base import CPP_TEMPLATE_PACKAGE


MODULE_TEMPLATE_CONFIGURATION = {
    'module-template' : 'module_template.hpp',
    'header-suffix' : 'hpp',
    'template-package' : CPP_TEMPLATE_PACKAGE,
    'field-type' : Field,
    'module-type' : Module,
    'register-type' : Register,
}


class ModuleTemplates( ModuleTemplatesBase ) :

    def __init__( self, paths, encapsulatedRegisterMap,
                  licenseTextLines = None,
                  suffixes = list() ) :
        super().__init__( paths, MODULE_TEMPLATE_CONFIGURATION, encapsulatedRegisterMap,
                          licenseTextLines = licenseTextLines,
                          suffixes = suffixes )
