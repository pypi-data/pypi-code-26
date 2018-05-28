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
from toktokkie.metadata.types.SeasonEpisode import SeasonEpisode
from toktokkie.metadata.types.MyanimelistEpisode import MyanimelistEpisode


class EpisodeRange(MetaPrimitive):
    """
    Class that models an episode range
    This can be used for example if you have a single file consisting
    of multiple episodes
    """

    episode_type = SeasonEpisode
    """
    Allows use of different episode types
    """

    def __init__(self, start: MetaPrimitive, end: MetaPrimitive):
        """
        Initializes the EpisodeRange object
        :param start: The first episode in the range
        :param end: The last episode in the range
        """
        self.start = start
        self.end = end

    def to_json(self) -> Dict[str, Dict[str, int]]:
        """
        Turns the object into a JSON-compatible dictionary
        :return: The dictionary representation of the EpisodeRange object
        """
        return {
            "start": self.start.to_json(), "end": self.end.to_json()
        }

    @classmethod
    def from_json(cls, json_data: any):
        """
        Generates an EpisodeRange object from a json dictionary
        :param json_data: The JSON dictionary
        :return: The generated EpisodeRange object
        """
        return cls(
            cls.episode_type.from_json(json_data["start"]),
            cls.episode_type.from_json(json_data["end"])
        )

    @classmethod
    def parse(cls, string: str):
        """
        Parses the EpisodeRange object from a string
        in the format sXXeXX-XX
        :param string: The string to parse
        :return: The generated EpisodeRange object
        """
        try:
            split = string.lower().split("-")
            start = cls.episode_type.parse(split[0])
            end = cls.episode_type(start.season, int(split[1]))
            if start.episode <= end.episode:
                return cls(start, end)
            else:
                return cls(end, start)
        except IndexError:
            raise ValueError()

    def __str__(self) -> str:
        """
        :return: A string representation of the object
        """
        return str(self.start) + "-" + str(self.end)

    def diff(self) -> int:
        """
        Calculates the difference between the episodes
        :return: The difference
        """
        # noinspection PyUnresolvedReferences
        return abs(self.end.episode - self.start.episode)


class SeasonEpisodeRange(EpisodeRange):
    """
    Alias for regular season/episode ranges
    """
    pass


class MyanimelistEpisodeRange(EpisodeRange):
    """
    Episode Range for Myanimelist episodes
    """
    episode_type = MyanimelistEpisode
