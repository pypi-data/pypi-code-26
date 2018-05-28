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


class Scheme:
    """
    Class that models a generic naming scheme that defines how a naming
    scheme should behave
    """

    name = "scheme"
    """
    The name/identifier of this scheme
    """

    @classmethod
    def _format_episode_name(cls, series_name: str, season: int,
                             episode: int, episode_name: str) -> str:
        """
        Formats the episode name. This is the method that should be
        implemented by subclasses
        :param series_name: The name of the series
        :param season: The season of the episode
        :param episode: The episode number of the episode
        :param episode_name: The name of the episode
        :return: The formatted episode name
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    @classmethod
    def generate_episode_name(cls, series_name: str, season: int,
                              episode: int, episode_name: str) -> str:
        """
        Generates an episode name that was checked for illegal file system
        characters beforehand
        :param series_name: The name of the series
        :param season: The season of the episode
        :param episode: The episode number of the episode
        :param episode_name: The name of the episode
        :return: The generated episode name
        """
        return cls.sanitize(cls._format_episode_name(
            series_name, season, episode, episode_name
        ))

    @classmethod
    def generate_episode_name_with_range(cls, series_name: str, season: int,
                                         episodes: List[Tuple[int, str]]) \
            -> str:
        """
        Generates an episode name that was checked for illegal file system
        characters beforehand.
        This formats an episode name for a range of episodes.
        :param series_name: The name of the series
        :param season: The season of the episode
        :param episodes: A list of tuples consisting of
                         episode numbers and names
        :return: The generated episode name
        """
        return cls.sanitize(
            cls._format_episode_name_with_range(series_name, season, episodes)
        )

    @staticmethod
    def sanitize(string: str) -> str:
        """
        Replaces all illegal file system characters with valid ones.
        Also, limit the length of the string to 120 charcters
        :param string: The string to sanitize
        :return: The sanitized string
        """

        illegal_characters = {
            "/": "／",
            "\\": "＼",
            "?": "？",
            "<": "＜",
            ">": "＞",
            ":": "꞉",
            "*": "∗",
            "|": "ǁ",
            "\"": "“"
        }

        sanitized = string
        for illegal_character, replacement in illegal_characters.items():
            sanitized = sanitized.replace(illegal_character, replacement)

        if len(sanitized) > 120:
            sanitized = sanitized[0:120] + "... "
        return sanitized
