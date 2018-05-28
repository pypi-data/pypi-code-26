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

from typing import Dict
from toktokkie.metadata.types.MetaType import MetaPrimitive


class SeasonEpisode(MetaPrimitive):
    """
    Class that models a season/episode
    """

    def __init__(self, season: int, episode: int):
        """
        Initializes the SeasonEpisode object
        :param season: The season of the episode
        :param episode: The episode number of the episode
        """
        self.season = season
        self.episode = episode

    def to_json(self) -> Dict[str, int]:
        """
        Turns the object into a JSON-compatible dictionary
        :return: The dictionary representation of the SeasonEpisode object
        """
        return {
            "S": self.season, "E": self.episode
        }

    @classmethod
    def from_json(cls, json_data: any):
        """
        Generates a SeasonEpisode object from a json dictionary
        :param json_data: The JSON dictionary
        :return: The generated SeasonEpisode object
        """
        return cls(json_data["S"], json_data["E"])

    @classmethod
    def parse(cls, string: str):
        """
        Parses the SeasonEpisode object from a string in the format sXXeXX
        :param string: The string to parse
        :return: The generated SeasonEpisode object
        """
        try:
            split = string.lower().replace("s", "").split("e")
            season = int(split[0])
            episode = int(split[1])
            return cls(season, episode)
        except IndexError:
            raise ValueError()

    def __str__(self) -> str:
        """
        :return: A string representation of the object
        """
        return "S" + str(self.season).zfill(2) + \
               "E" + str(self.episode).zfill(2)
