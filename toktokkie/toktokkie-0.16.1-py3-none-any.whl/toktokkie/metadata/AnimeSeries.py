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

from typing import Dict, List
from toktokkie.metadata.helper.prompt import prompt_user
from toktokkie.metadata.TvSeries import TvSeries
from toktokkie.metadata.types.AgentIdType import AgentIdType
from toktokkie.metadata.types.MetaType import Str, MetaType
from toktokkie.metadata.types.AnimeSeriesSeason import AnimeSeriesSeason
from toktokkie.exceptions import InvalidMetadataException
from toktokkie.metadata.types.CommaList import MyanimelistEpisodeCommaList, \
    MyanimelistEpisodeRangeCommaList, IntCommaList


class AnimeSeries(TvSeries):

    # -------------------------------------------------------------------------
    # These Methods and Variables should be extended by subclasses
    # -------------------------------------------------------------------------

    type = Str("anime_series")
    """
    The metadata type
    """

    season_type = AnimeSeriesSeason
    """
    The type of season to use. Can be used by subclasses to add more attributes
    to seasons
    """

    @classmethod
    def generate_dict_from_prompts(cls, directory: str) -> Dict[str, MetaType]:
        """
        Generates an Anime Series from user prompts
        :param directory: The directory to generate the metadata for
        :return: The generated metadata dictionary
        """
        data = super().generate_dict_from_prompts(directory)

        data["mal_check_ignores"] = prompt_user(
            "Myanimelist Check Ignores", IntCommaList, IntCommaList([])
        )
        data["mal_excludes"] = prompt_user(
            "Myanimelist Excludes",
            MyanimelistEpisodeCommaList, MyanimelistEpisodeCommaList([])
        )
        data["mal_irregular_season_starts"] = prompt_user(
            "Myanimelist Irregular Season Starts",
            MyanimelistEpisodeCommaList, MyanimelistEpisodeCommaList([])
        )
        data["mal_multi_episodes"] = prompt_user(
            "Myanimelist Multi-Episodes (x episodes/1 file)",
            MyanimelistEpisodeRangeCommaList,
            MyanimelistEpisodeRangeCommaList([])
        )
        return data

    def to_dict(self) -> Dict[str, MetaType]:
        """
        Turns the metadata into a dictionary
        :return: The dictionary representation of the metadata
        """
        data = super().to_dict()
        data["mal_check_ignores"] = self.mal_check_ignores
        data["mal_excludes"] = self.mal_excludes
        data["mal_irregular_season_starts"] = \
            self.mal_irregular_season_starts
        data["mal_multi_episodes"] = self.mal_multi_episodes
        return data

    def __init__(self, json_data: dict):
        """
        Initializes the metadata object
        :param json_data: The JSON metadata to use
        """
        super().__init__(json_data)
        try:
            self.mal_check_ignores = IntCommaList.from_json(
                json_data["mal_check_ignores"]
            )
            self.mal_excludes = MyanimelistEpisodeCommaList.from_json(
                json_data["mal_excludes"]
            )
            self.mal_irregular_season_starts = \
                MyanimelistEpisodeCommaList.from_json(
                    json_data["mal_irregular_season_starts"]
                )
            self.mal_multi_episodes = \
                MyanimelistEpisodeRangeCommaList.from_json(
                    json_data["mal_multi_episodes"]
                )

        except KeyError:
            raise InvalidMetadataException()

    def get_agent_excludes(self, id_type: AgentIdType) \
            -> List[Dict[str, int]] or None:
        """
        Retrieves excluded episodes using the provided agent ID type
        :param id_type: The ID type to check for
        :return: The excluded episode list, or None if id type not applicable
        """
        sup = super().get_agent_excludes(id_type)
        if sup is not None:
            return sup
        elif id_type == AgentIdType.MYANIMELIST:
            return self.merge_excludes(
                self.mal_excludes, self.mal_multi_episodes
            )
        else:
            return None

    def get_season_start(self, id_type: AgentIdType, season: int) -> int:
        """
        Retrieves irregular season episode starts for the provided agent type
        and season
        :param id_type: The agent ID type
        :param season: The season to get the season start for
        :return: The episode at which that season starts
        """

        if id_type == AgentIdType.MYANIMELIST:
            irregulars = self.mal_irregular_season_starts.to_json()
            hits = list(filter(lambda x: x["S"] == season, irregulars))
            if len(hits) == 0:
                return 1
            elif len(hits) >= 1:
                return hits[0]["E"]
                # TODO New data structure so that duplicate entries can't exist
        else:
            return super().get_season_start(id_type, season)

    def get_multi_episode_ranges(self, id_type: AgentIdType) \
            -> List[Dict[str, Dict[str, int]]] or None:
        """
        Retrieves ranges of multiple episodes contained within a single file
        :param id_type: The type of ID
        :return: A list of dictionaries representing the episode ranges
        """
        sup = super().get_multi_episode_ranges(id_type)
        if sup is not None:
            return sup
        if id_type == AgentIdType.MYANIMELIST:
            return self.mal_multi_episodes.to_json()
        else:
            return None

    # -------------------------------------------------------------------------
