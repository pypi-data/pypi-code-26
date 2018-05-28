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

from typing import List
from toktokkie.metadata.types.MetaType import MetaPrimitive
from xdcc_dl.entities.XDCCPack import XDCCPack
from xdcc_dl.pack_search.SearchEngine import SearchEngineType


class SearchEngine(MetaPrimitive):
    """
    A class that handles the selection of a search engine
    """

    def __init__(self, search_engine: str):
        """
        Initializes the SearchEngine object
        :param search_engine: The search engine identifier to use
        """
        self.search_engine = search_engine

    def to_json(self) -> str:
        """
        Turns the object into a string
        :return: The dictionary representation of the Search Engine
        """
        # noinspection PyTypeChecker
        return self.search_engine

    @classmethod
    def from_json(cls, json_data: any):
        """
        Generates a SearchEngine object from JSON data
        :param json_data: The JSON data
        :return: The generated SearchEngine object
        """
        return cls.parse(json_data)

    @classmethod
    def parse(cls, string: str):
        """
        Initializes the SearchEngine object based on a string identifier.
        Errors in the string will raise a ValueError.
        :param string: The string to parse
        """
        if SearchEngineType.resolve(string) is not None:
            return cls(string.lower())
        else:
            raise ValueError("Options: " + str(SearchEngineType.choices()))

    def __str__(self) -> str:
        """
        :return: A string representation of the search engine
        """
        return self.search_engine

    def search(self, search_string: str) -> List[XDCCPack]:
        """
        Searches for XDCC packs using the search engine
        :param search_string: The term for which to search
        :return: The retrieved XDCC packs
        """
        searcher = SearchEngineType.resolve(self.search_engine)
        return searcher.search(search_string)
