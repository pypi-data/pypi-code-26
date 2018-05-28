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

from typing import Tuple, List
from toktokkie.renaming.schemes.Scheme import Scheme


class Plex(Scheme):
    """
    Generates a naming scheme like this:

    Series Name - SXXEXX - Episode Name

    Plex Media Server accepts this format
    """

    name = "plex"
    """
    The name/identifier of this scheme
    """

    @classmethod
    def _format_episode_name(cls, series_name: str, season: int, episode: int,
                             episode_name: str) -> str:
        """
        Formats the episode name
        :param series_name: The name of the series
        :param season: The season of this episode
        :param episode: The episode number of this episode
        :param episode_name: The name of this episode
        :return: The generated episode name
        """
        return series_name + " - S" + str(season).zfill(2) + \
            "E" + str(episode).zfill(2) + " - " + episode_name

    @classmethod
    def _format_episode_name_with_range(cls, series_name: str, season: int,
                                        episodes: List[Tuple[int, str]])\
            -> str:
        """
        Formats the episode name. This is the method that should be
        implemented by subclasses. Formats a range of episodes.
        :param series_name: The name of the series
        :param season: The season of the episode
        :param episodes: A list of tuples consisting of
                         episode numbers and names
        :return: The formatted episode name
        """
        first = episodes[0]
        last = episodes[len(episodes) - 1]
        return series_name + " - S" + str(season).zfill(2) + \
            "E" + str(first[0]).zfill(2) + "-E" + str(last[0]).zfill(2) + \
            " - " + first[1] + " ǁ " + last[1]
