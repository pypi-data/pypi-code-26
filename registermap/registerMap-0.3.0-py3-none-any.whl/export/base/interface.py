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

import abc


class LanguageParser( metaclass = abc.ABCMeta ) :
    """
    Interface of output language command line argument parsing for the `export-map` tool.
    """


    @abc.abstractmethod
    def acquireOptions( self, parserProcessedArguments ) :
        pass


class OutputInterface( metaclass = abc.ABCMeta ) :
    """
    Interface for register map export to a language.
    """


    @abc.abstractmethod
    def generate( self, registerMap, registerMapName ) :
        """
        Export a child specific representation of the given register map.

        :param registerMap: RegisterMap object to be exported.
        :param registerMapName: Language specific name of register map.
        """
        pass


class TemplateInterface( metaclass = abc.ABCMeta ) :
    """
    Interface for template management.
    """


    @abc.abstractmethod
    def apply( self ) :
        pass
