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


class MyanimelistEpisode(MetaPrimitive):
    """
    Class that models a myanimelist episode, bound to a myanimelist ID
    """

    def __init__(self, mal_id: int, episode: int):
        """
        Initializes the MyanimelistEpisode object
        :param mal_id: The myanimelist ID of the episode
        :param episode: The episode number of the episode
        """
        self.mal_id = mal_id
        self.episode = episode

    def to_json(self) -> Dict[str, int]:
        """
        Turns the object into a JSON-compatible dictionary
        :return: The dictionary representation of the MyanimelistEpisode object
        """
        return {
            "mal_id": self.mal_id, "E": self.episode
        }

    @classmethod
    def from_json(cls, json_data: any):
        """
        Generates a MyanimelistEpisode object from a json dictionary
        :param json_data: The JSON dictionary
        :return: The generated MyanimelistEpisode object
        """
        return cls(json_data["mal_id"], json_data["E"])

    @classmethod
    def parse(cls, string: str):
        """
        Parses the MyanimelistEpisode object from a string in the format
            idXXeXX
        :param string: The string to parse
        :return: The generated MyanimelistEpisode object
        """
        try:
            split = string.lower().replace("id", "").split("e")
            mal_id = int(split[0])
            episode = int(split[1])
            return cls(mal_id, episode)
        except IndexError:
            raise ValueError()

    def __str__(self) -> str:
        """
        :return: A string representation of the object
        """
        return "ID" + str(self.mal_id) + "E" + str(self.episode).zfill(2)
