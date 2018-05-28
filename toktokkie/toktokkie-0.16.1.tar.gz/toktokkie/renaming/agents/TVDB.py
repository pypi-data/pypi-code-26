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

import tvdb_api
from typing import List
from toktokkie.renaming.agents.Agent import Agent
from toktokkie.metadata.types.AgentIdType import AgentIdType
from tvdb_api import tvdb_episodenotfound, tvdb_seasonnotfound, \
    tvdb_shownotfound


class TVDB(Agent):
    """
    Class that uses TheTVDB.com to fetch episode names
    """

    name = "tvdb"
    """
    The name/identifier of this agent
    """

    id_type = AgentIdType.TVDB
    """
    Requires TVDB IDs
    """

    @classmethod
    def fetch_episode_name(cls, series_ids: List[int], season: int,
                           episode: int) -> str:
        """
        Fetches an episode name for an episode from TheTVDB.com
        :param series_ids: Agent IDs for searching the series
        :param season: The season of the episode
        :param episode: The episode number of the episode
        :return: The episode name
        """

        for agent_id in series_ids:
            try:
                tvdb = tvdb_api.Tvdb()
                return tvdb[agent_id][season][episode]["episodename"]

            except (tvdb_episodenotfound, tvdb_seasonnotfound,
                    tvdb_shownotfound, ConnectionError, KeyError) as e:
                # If not found, or other error, just return generic name
                if str(e) == "cache_location":  # pragma: no cover
                    print("TheTVDB.com is down!")

            except Exception as e:

                print("Error fetching TVDB data: " + str(e))

        return "Episode " + str(episode)
