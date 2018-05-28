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

import json
from toktokkie.metadata.Base import Base
from toktokkie.metadata.TvSeries import TvSeries
from toktokkie.metadata.AnimeSeries import AnimeSeries
from toktokkie.metadata.Movie import Movie
from toktokkie.metadata.AnimeMovie import AnimeMovie

metadata_types = [Base, TvSeries, AnimeSeries, Movie, AnimeMovie]
"""
All available metadata types
"""


def resolve_metadata(metadata_file: str) -> Base:
    """
    Automatically resolves a metadata type based on the info.json's metadata
    type parameter.
    :param metadata_file: The metadata file for which to resolve the metadata
    :return: The read metadata file
    """
    with open(metadata_file, "r") as f:
        data = json.load(f)

    metadata_class = \
        list(filter(lambda x: x.type == data["type"], metadata_types))[0]

    return metadata_class.from_json_file(metadata_file)


def check_metadata_subtype(metadata_object: Base, to_check: Base or str) \
        -> bool:
    """
    Checks if a metadata class is a subclass of another metadata class based
    either on an explicit metdata class or even just the type string.
    ValueErrors get raised when the to_check parameter isn't either a
    valid Metadata class or a valid metadata type string.
    :param metadata_object: The metadata object to check
    :param to_check: The metadata class to check against
    :return: True if the metadata object is a subclass of the to_check class
    """

    try:
        if issubclass(type(to_check), str):
            try:
                to_check = list(filter(
                    lambda x: x.type.to_json() == to_check.lower(),
                    metadata_types
                ))[0]
                return issubclass(type(metadata_object), to_check)
            except IndexError:
                raise ValueError(to_check)

        elif issubclass(to_check, Base):
            return metadata_object.is_subclass_of(to_check)

        else:
            raise ValueError(to_check)

    except TypeError:
        raise ValueError(to_check)
