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

from typing import List, Type
from toktokkie.metadata.types.Language import Language
from toktokkie.metadata.types.Resolution import Resolution
from toktokkie.metadata.types.MetaType import MetaPrimitive, Str, Int
from toktokkie.metadata.types.MyanimelistEpisode import MyanimelistEpisode
from toktokkie.metadata.types.SeasonEpisode import SeasonEpisode
from toktokkie.metadata.types.EpisodeRange import SeasonEpisodeRange, \
    MyanimelistEpisodeRange


class CommaList(MetaPrimitive):
    """
    A class that automatically parses comma-separated strings into
    various different objects and supports JSON serialization
    """

    meta_type = Str  # type: Type[MetaPrimitive]
    """
    The type of the comma list. Defaults to Str.
    """

    def __init__(self, _list: List[MetaPrimitive]):
        """
        Initializes a comma list. Casts to the correw
        :param _list: The list to use
        """
        self.list = []
        for element in _list:
            if type(element) != self.meta_type:
                element = self.meta_type.parse(str(element))
            self.list.append(element)

    @classmethod
    def parse(cls, string: str):
        """
        Parses a comma-separated list
        :param string: The string to parse
        :return: The parsed list
        """
        parsed = string.split(",") if string != "" else []
        parsed = list(map(lambda x: x.strip(), parsed))
        parsed = list(map(lambda x: Str(x), parsed))
        return cls(parsed)

    def to_json(self) -> List[any]:
        """
        Converts this object into a JSON-compatible list
        :return: The JSON-compatible list
        """
        data = []
        for element in self.list:
            data.append(element.to_json())
        return data

    @classmethod
    def from_json(cls, json_data: List[any]):
        """
        Generates a string-based comma list from a JSON list
        :param json_data: The JSON list to use
        :return: The generated CommaList object
        """
        return cls(list(map(lambda x: cls.meta_type.from_json(x), json_data)))

    def __str__(self) -> str:
        """
        Provides a string representation of the comma-separated list
        :return: The string representation of the list
        """
        return str(list(map(lambda x: str(x), self.list)))


class StrCommaList(CommaList):
    """
    A String Comma List
    """
    pass


class IntCommaList(CommaList):
    """
    An Integer Comma List
    """
    meta_type = Int


class ResolutionCommaList(CommaList):
    """
    A Resolution Comma List
    """
    meta_type = Resolution


class LanguageCommaList(CommaList):
    """
    A Language Comma List
    """
    meta_type = Language


class SeasonEpisodeCommaList(CommaList):
    """
    An Episode Exclusion Comma List
    """
    meta_type = SeasonEpisode


class SeasonEpisodeRangeCommaList(CommaList):
    """
    An Episode Exclusion Comma List
    """
    meta_type = SeasonEpisodeRange


class MyanimelistEpisodeCommaList(CommaList):
    """
    A Myanimelist Episode Comma List
    """
    meta_type = MyanimelistEpisode


class MyanimelistEpisodeRangeCommaList(CommaList):
    """
    A Myanimelist Episode Range Comma List
    """
    meta_type = MyanimelistEpisodeRange
