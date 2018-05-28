"""LICENSE
Copyright 2015 Hermann Krumrey <hermann@krumreyh.com>

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from toktokkie.renaming.agents.Agent import Agent
from toktokkie.renaming.schemes.Scheme import Scheme
from toktokkie.renaming.agents.TVDB import TVDB
from toktokkie.renaming.schemes.Plex import Plex
from toktokkie.renaming.Episode import Episode
from toktokkie.renaming.Renamer import Renamer


schemes = [Plex]
"""
List of available schemes
"""


agents = [TVDB]
"""
List of available agents
"""
