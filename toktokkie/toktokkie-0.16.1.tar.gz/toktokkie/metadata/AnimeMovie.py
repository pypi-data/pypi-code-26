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
from toktokkie.exceptions import InvalidMetadataException
from toktokkie.metadata.Movie import Movie
from toktokkie.metadata.types.MetaType import MetaType, Str, Int
from toktokkie.metadata.helper.prompt import prompt_user


class AnimeMovie(Movie):
    """
    Class that models an anime movie
    """

    type = Str("anime_movie")
    """
    The type of the Metadata
    """

    @classmethod
    def generate_dict_from_prompts(cls, directory: str) -> Dict[str, MetaType]:
        """
        Generates a Metadata dictionary based on user prompts.
        :param directory: The path to the directory for which to generate
                          the metadata
        :return: The generated metadata dictionary
        """
        data = super().generate_dict_from_prompts(directory)
        data["mal_id"] = prompt_user("Myanimelist ID", Int)
        return data

    def to_dict(self) -> dict:
        """
        Generates a JSON-compatible dictionary representation of the
        metadata object. Should be extended by child classes
        :return: The dictionary representation
        """
        data = super().to_dict()
        data["mal_id"] = self.mal_id
        return data

    def __init__(self, json_data: Dict[str, any]):
        """
        Initializes the Metadata object. If the provided JSON data is incorrect
        (i.e. missing elements or invalid types), an InvalidMetadata exception
        will be thrown.
        :param json_data: The JSON dictionary to use
                          to generate the metadata object
        """
        super().__init__(json_data)
        try:
            self.mal_id = Int.from_json(json_data["mal_id"])
        except KeyError:
            raise InvalidMetadataException()
