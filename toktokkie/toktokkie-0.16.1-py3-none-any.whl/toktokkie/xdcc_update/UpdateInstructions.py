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
from typing import Dict
from toktokkie.metadata.types.MetaType import Int, Str, MetaType
from toktokkie.metadata import Base, TvSeries
from toktokkie.metadata.helper.prompt import prompt_user
from toktokkie.xdcc_update.types.SearchEngine import SearchEngine
from toktokkie.xdcc_update.types.Resolution import Resolution, ResolutionOption
from toktokkie.xdcc_update.types.SearchPattern import SearchPattern, \
    SearchPatternOption


class UpdateInstructions(Base):
    """
    Class that stores the information for XDCC Updates
    """

    @classmethod
    def generate_dict_from_prompts(cls, directory: str) -> Dict[str, MetaType]:
        """
        Generates a dictionary representing the XDCC update instructions from
        user prompts
        :param directory: The directory for which to generate the prompts
        :return: The genrated dictionary
        """

        print("Generating xdcc-update instructions for " +
              os.path.basename(directory))

        metadata = TvSeries.from_json_file(
            os.path.join(directory, ".meta", "info.json")
        )

        season_paths = []
        for season in metadata.seasons.list:
            season_paths.append(season.path)

        season_path = prompt_user("Season Path", Str)
        while not os.path.isdir(os.path.join(directory, season_path)) or \
                season_path not in season_paths:
            print("Please enter a valid directory that also has an entry "
                  "in the metadata file")
            season_path = prompt_user("Season Path", Str)

        data = {
            "season_path": season_path,
            "search_name": prompt_user("Search Name", Str),
            "search_pattern": prompt_user(
                "Search Pattern", SearchPattern,
                SearchPattern(SearchPatternOption.HORRIBLESUBS)),
            "search_engine": prompt_user("Search Engine", SearchEngine,
                                         SearchEngine.parse("horriblesubs")),
            "resolution": prompt_user("Resolution", Resolution,
                                      Resolution(ResolutionOption.X1080p)),
            "preferred_bot": prompt_user("Preferred Bot",
                                         Str, Str("CR-HOLLAND|NEW")),
            "episode_offset": prompt_user("Episode Offset", Int, Int(0))
        }
        return data

    def to_dict(self) -> Dict[str, MetaType]:
        """
        Turns these update instructions into a dictionary of MetaTypes
        :return: The dictionary representing the instructions
        """
        return {
            "season_path": self.season_path,
            "search_name": self.search_name,
            "search_pattern": self.search_pattern,
            "search_engine": self.search_engine,
            "resolution": self.resolution,
            "preferred_bot": self.preferred_bot,
            "episode_offset": self.episode_offset
        }

    # noinspection PyMissingConstructor
    def __init__(self, json_data: Dict[str, any]):
        """
        Initializes the object using JSON data
        :param json_data: The JSON data to use
        """
        self.season_path = Str.from_json(json_data["season_path"])
        self.search_name = Str.from_json(json_data["search_name"])
        self.search_pattern = \
            SearchPattern.from_json(json_data["search_pattern"])
        self.search_engine = SearchEngine.from_json(json_data["search_engine"])
        self.resolution = Resolution.from_json(json_data["resolution"])
        self.preferred_bot = Str.from_json(json_data["preferred_bot"])
        self.episode_offset = Int.from_json(json_data["episode_offset"])
