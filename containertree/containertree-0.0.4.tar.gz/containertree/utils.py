#
# Copyright (C) 2018 Vanessa Sochat.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import os

def get_installdir():
    return os.path.abspath(os.path.dirname(__file__))

def get_template(name):
    '''return an html template based on name.
    '''
    here = get_installdir()
    template_folder = os.path.join(here, 'templates')
    template_file = "%s/%s.html" %(template_folder, name)
    if os.path.exists(template_file):
        return template_file
