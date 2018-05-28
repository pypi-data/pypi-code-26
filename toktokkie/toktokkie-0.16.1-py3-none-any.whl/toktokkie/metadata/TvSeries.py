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

import os
from typing import Dict, List
from toktokkie.metadata.Base import Base
from toktokkie.metadata.helper.prompt import prompt_user
from toktokkie.exceptions import InvalidMetadataException
from toktokkie.metadata.types.AgentIdType import AgentIdType
from toktokkie.metadata.types.SeasonEpisode import SeasonEpisode
from toktokkie.metadata.types.TvSeriesSeason import TvSeriesSeason
from toktokkie.metadata.types.MetaType import Str, MetaType, MetaList
from toktokkie.metadata.types.CommaList import SeasonEpisodeCommaList, \
    SeasonEpisodeRangeCommaList


class TvSeries(Base):
    """
    A metadata model for tv series
    """

    # -------------------------------------------------------------------------
    # These Methods and Variables should be extended by subclasses
    # -------------------------------------------------------------------------

    type = Str("tv_series")
    """
    The metadata type
    """

    season_type = TvSeriesSeason
    """
    The type of season to use. Can be used by subclasses to add more attributes
    to seasons
    """

    @classmethod
    def generate_dict_from_prompts(cls, directory: str) -> Dict[str, MetaType]:
        """
        Generates a TV Series from user prompts
        :param directory: The directory to generate the metadata for
        :return: The generated metadata dictionary
        """
        data = super().generate_dict_from_prompts(directory)
        seasons = []

        for season in sorted(os.listdir(directory)):
            season_dir = os.path.join(directory, season)
            if os.path.isfile(season_dir) or season.startswith(".meta"):
                continue

            if len(seasons) > 0:
                previous = seasons[len(seasons) - 1]
                season_obj = cls.season_type.prompt(season, previous)
            else:
                season_obj = cls.season_type.prompt(season)

            seasons.append(season_obj)

        data["seasons"] = MetaList(seasons)
        data["tvdb_excludes"] = prompt_user(
            "TVDB Excludes", SeasonEpisodeCommaList, SeasonEpisodeCommaList([])
        )
        data["tvdb_irregular_season_starts"] = prompt_user(
            "TVDB Irregular Season Starts",
            SeasonEpisodeCommaList, SeasonEpisodeCommaList([])
        )
        data["tvdb_multi_episodes"] = prompt_user(
            "TVDB Multi-Episodes (x episodes/1 file)",
            SeasonEpisodeRangeCommaList, SeasonEpisodeRangeCommaList([])
        )
        return data

    def to_dict(self) -> Dict[str, MetaType]:
        """
        Turns the metadata into a dictionary
        :return: The dictionary representation of the metadata
        """
        data = super().to_dict()
        data["seasons"] = self.seasons
        data["tvdb_excludes"] = self.tvdb_excludes
        data["tvdb_irregular_season_starts"] = \
            self.tvdb_irregular_season_starts
        data["tvdb_multi_episodes"] = self.tvdb_multi_episodes
        return data

    def __init__(self, json_data: dict):
        """
        Initializes the metadata object
        :param json_data: The JSON metadata to use
        """
        super().__init__(json_data)
        try:
            self.seasons = MetaList([])
            self.tvdb_excludes = \
                SeasonEpisodeCommaList.from_json(json_data["tvdb_excludes"])
            self.tvdb_irregular_season_starts = \
                SeasonEpisodeCommaList.from_json(
                    json_data["tvdb_irregular_season_starts"]
                )
            self.tvdb_multi_episodes = SeasonEpisodeRangeCommaList.from_json(
                json_data["tvdb_multi_episodes"]
            )

            for season in json_data["seasons"]:
                self.seasons.append(self.season_type.from_json(season))

        except KeyError:
            raise InvalidMetadataException()

    def get_agent_excludes(self, id_type: AgentIdType) \
            -> List[Dict[str, int]] or None:
        """
        Retrieves excluded episodes using the provided agent ID type
        :param id_type: The ID type to check for
        :return: The excluded episode list, or None if id type not applicable
        """

        if id_type == AgentIdType.TVDB:
            return self.merge_excludes(
                self.tvdb_excludes, self.tvdb_multi_episodes
            ).to_json()
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

        if id_type == AgentIdType.TVDB:
            irregulars = self.tvdb_irregular_season_starts.to_json()
            hits = list(filter(lambda x: x["S"] == season, irregulars))
            if len(hits) == 0:
                return 1
            elif len(hits) >= 1:
                return hits[0]["E"]
                # TODO New data structure so that duplicate entries can't exist
        else:
            return 1

    def get_multi_episode_ranges(self, id_type: AgentIdType) \
            -> List[Dict[str, Dict[str, int]]] or None:
        """
        Retrieves ranges of multiple episodes contained within a single file
        :param id_type: The type of ID
        :return: A list of dictionaries representing the episode ranges
        """

        if id_type == AgentIdType.TVDB:
            return self.tvdb_multi_episodes.to_json()
        else:
            return None

    # -------------------------------------------------------------------------

    # noinspection PyMethodMayBeStatic
    def merge_excludes(self, excludes: SeasonEpisodeCommaList,
                       ranges: SeasonEpisodeRangeCommaList) \
            -> SeasonEpisodeCommaList:
        """
        Merges a SeasonEpisodeCommaList and a SeasonEpisodeRangeCommaList
        into a single SeasonEpisodeCommaList that contains all episodes to skip
        :param excludes: The single episodes to exclude
        :param ranges: The ranges which will be completely excluded,
                       with the exception of the first episode
        :return: The combined SeasonEpisodeCommaList exclusion list
        """
        excluded = excludes.list

        for multi in ranges.list:
            episode = multi.start.episode + 1
            while episode <= multi.end.episode:
                excluded.append(SeasonEpisode(multi.start.season, episode))
                episode += 1

        return SeasonEpisodeCommaList(excluded)
