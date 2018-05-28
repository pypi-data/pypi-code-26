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

import re
from enum import Enum
from toktokkie.metadata.types.MetaType import MetaPrimitive
from toktokkie.xdcc_update.types.Resolution import ResolutionFormat, Resolution


class SearchPatternOption(Enum):
    """
    Enum class that defines the various search pattern options that exist
    """

    HORRIBLESUBS = {
        "name": "horriblesubs",
        "search_pattern": "[HorribleSubs] @{NAM} - @{EPI} [@{RES}].mkv",
        "check_pattern": "^[HorribleSubs] @{NAM} - @{EPI} [@{RES}].mkv$",
        "episode_zfill": 2,
        "resolution_format": ResolutionFormat.P_NOTATION
    }

    CHYUU = {
        "name": "chyuu",
        "search_pattern": "[Chyuu] @{NAM} - @{EPI} [@{RES}]",
        "check_pattern": "[Chyuu] @{NAM} - @{EPI} [@{RES}][@{HSH}].mkv",
        "episode_zfill": 2,
        "resolution_format": ResolutionFormat.P_NOTATION
    }

    ASENSHI = {
        "name": "asenshi",
        "search_pattern": "[Asenshi] @{NAM} - @{EPI}",
        "check_pattern": "[Asenshi] @{NAM} - @{EPI} [@{HSH}].mkv",
        "episode_zfill": 2,
        "resolution_format": ResolutionFormat.P_NOTATION
    }

    KOORITSUKAI = {
        "name": "kooritsukai",
        "search_pattern": "[Kooritsukai] @{NAM} - @{EPI} [@{RES}]",
        "check_pattern": "[Kooritsukai] @{NAM} - @{EPI} [@{RES}][@{HSH}].mkv",
        "episode_zfill": 2,
        "resolution_format": ResolutionFormat.P_NOTATION
    }

    DAVINCI = {
        "name": "davinci",
        "search_pattern": "[Davinci] @{NAM} - @{EPI} [@{RES}]",
        "check_pattern": "[Davinci] @{NAM} - @{EPI} [@{RES}][@{HSH}].mkv",
        "episode_zfill": 2,
        "resolution_format": ResolutionFormat.P_NOTATION
    }

    CAPTAIN_TSUBASA = {
        "name": "captain_tsubasa",
        "search_pattern":
            "Captain_Tsubasa(2018)_@{EPI}[Please_sub_this_Viz](english).mkv",
        "check_pattern":
            "Captain_Tsubasa(2018)_@{EPI}[Please_sub_this_Viz](english).mkv",
        "episode_zfill": 2,
        "resolution_format": ResolutionFormat.P_NOTATION
    }

    GENERIC = {
        "name": "generic",
        "search_pattern": "@{NAM} - @{EPI} [@{RES}]",
        "check_pattern": "@{NAM} - @{EPI} [@{RES}]",
        "episode_zfill": 2,
        "resolution_format": ResolutionFormat.P_NOTATION
    }


class SearchPattern(MetaPrimitive):
    """
    Class that models search patterns for search terms
    """

    def __init__(self, search_pattern_option: SearchPatternOption):
        """
        Initializes the SearchPattern object
        :param search_pattern_option: The search pattern option
        """
        self.search_pattern_option = search_pattern_option

        self.name = self.search_pattern_option.value["name"]
        self.search_pattern = \
            self.search_pattern_option.value["search_pattern"]
        self.check_pattern = self.search_pattern_option.value["check_pattern"]
        self.episode_zfill = self.search_pattern_option.value["episode_zfill"]
        self.resolution_format = \
            self.search_pattern_option.value["resolution_format"]

    def to_json(self) -> str:
        """
        Turns the object into a string
        :return: The dictionary representation of the SearchPattern
        """
        return self.search_pattern_option.value["name"]

    @classmethod
    def from_json(cls, json_data: any):
        """
        Generates a SearchPattern object from JSON data
        :param json_data: The JSON data
        :return: The generated SearchPattern object
        """
        return cls.parse(json_data)

    @classmethod
    def parse(cls, string: str):
        """
        Initializes the SearchPattern object based on a string identifier.
        Errors in the string will raise a ValueError
        :param string: The string to parse
        """
        error_msg = "Options: ["
        for option in SearchPatternOption:
            error_msg += option.value["name"] + ","
            if option.value["name"] == string.lower():
                return cls(option)
        raise ValueError(error_msg + "]")

    def __str__(self) -> str:
        """
        :return: A string representation of the resolution
        """
        return self.name

    def generate_search_term(self, series_name: str, episode: int,
                             resolution: Resolution):
        """
        Generates a search term using the search pattern
        :param series_name: The series name
        :param episode: The episode number
        :param resolution: The resolution to search for
        :return: The generated search term
        """
        return self._fill_pattern(series_name, episode, resolution)

    def check_search_result(self, series_name: str, episode: int,
                            resolution: Resolution, result: str) -> bool:
        """
        Checks the result os a search
        :param series_name: The series name
        :param episode: The episode
        :param resolution: The resolution
        :param result: The resulting episode name
        :return: True if the episode name matches, else False
        """
        regex = re.compile(
            self._fill_pattern(series_name, episode, resolution, True)
        )
        return bool(re.search(regex, result))

    def _fill_pattern(self, series_name: str, episode: int,
                      resolution: Resolution, regex: bool = False):
        """
        Fills a pattern with applicable information
        :param series_name: The name of the series
        :param episode: The episode number
        :param resolution: The resolution
        :param regex: Indicates if the pattern should be
                      filled as a regex or not
        :return: The filled pattern
        """
        pattern = self.check_pattern if regex else self.search_pattern
        pattern = pattern.replace("@{NAM}", series_name)
        pattern = pattern.replace(
            "@{RES}", resolution.to_format(self.resolution_format)
        )

        if regex:
            pattern = pattern.replace("[", "\\[")
            pattern = pattern.replace("]", "\\]")
            pattern = pattern.replace("(", "\\(")
            pattern = pattern.replace(")", "\\)")
            pattern = pattern.replace("@{HSH}", "[a-zA-Z0-9]+")
            pattern = pattern.replace(
                "@{EPI}", str(episode).zfill(self.episode_zfill) + "(v[0-9]+)?"
            )

        else:
            pattern = pattern.replace(
                "@{EPI}", str(episode).zfill(self.episode_zfill)
            )

        return pattern
