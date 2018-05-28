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

from typing import List


class Agent:
    """
    Generic Agent class that defines what a renaming agent should implement
    """

    name = "agent"
    """
    The name/identifier of this agent
    """

    id_type = None
    """
    The ID type required for fetching episode name data
    """

    @classmethod
    def fetch_episode_name(cls, series_ids: List[int], season: int,
                           episode: int) -> str:
        """
        Fetches an episode name for an episode
        :param series_ids: Agent IDs for searching the series
        :param season: The season of the episode
        :param episode: The episode number of the episode
        :return: The episode name
        """
        raise NotImplementedError()
