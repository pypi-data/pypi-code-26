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
import json
from typing import Dict
from toktokkie.metadata.helper.prompt import prompt_user
from toktokkie.metadata.types.MetaType import MetaType, Str
from toktokkie.metadata.types.CommaList import StrCommaList
from toktokkie.exceptions import InvalidMetadataException


class Base:
    """
    The Base Metadata class. It defines general metadata methods and
    common interfaces.
    """

    # -------------------------------------------------------------------------
    # These Methods and Variables should be extended by subclasses
    # -------------------------------------------------------------------------

    type = Str("base")
    """
    The type of the Metadata. Shoudl generally be overridden by child classes
    """

    @classmethod
    def generate_dict_from_prompts(cls, directory: str) -> Dict[str, MetaType]:
        """
        Generates a Metadata dictionary based on user prompts.
        :param directory: The path to the directory for which to generate
                          the metadata
        :return: The generated metadata dictionary
        """
        name = os.path.basename(directory)
        print("Generating " + cls.type + " metadata for " + name)
        data = {
            "type": cls.type,
            "name": prompt_user("Name", Str, Str(name)),
            "tags": prompt_user("Tags", StrCommaList, StrCommaList([]))
        }
        return data

    def to_dict(self) -> dict:
        """
        Generates a JSON-compatible dictionary representation of the
        metadata object. Should be extended by child classes
        :return: The dictionary representation
        """
        return {
            "type": self.type,
            "name": self.name,
            "tags": self.tags
        }

    def __init__(self, json_data: Dict[str, any]):
        """
        Initializes the Metadata object. If the provided JSON data is incorrect
        (i.e. missing elements or invalid types), an InvalidMetadata exception
        will be thrown.
        :param json_data: The JSON dictionary to use
                          to generate the metadata object
        """
        try:
            self.name = Str.from_json(json_data["name"])
            self.tags = StrCommaList.from_json(json_data["tags"])
        except KeyError:
            raise InvalidMetadataException()

    # -------------------------------------------------------------------------

    @classmethod
    def generate_from_prompts(cls, directory: str):
        """
        Generates a Metadata object from user prompts and a dictionary
        :param directory: The dictionary to use
        :return: The generated metadata object
        """
        data = cls.generate_dict_from_prompts(directory)
        return cls(cls.jsonize_dict(data))

    @classmethod
    def from_json_file(cls, json_file: str):
        """
        Generates a Metadata object from a JSON file path
        :param json_file: The path to the JSON file
        :return: The generated metadata object
        """
        with open(json_file, "r") as f:
            data = json.load(f)
        return cls(data)

    def to_json(self) -> Dict[str, any]:
        """
        Converts this object into a JSON dictionary
        :return: The JSOn dictionary
        """
        return self.jsonize_dict(self.to_dict())

    def write(self, json_file: str):
        """
        Writes the metadata to a file in JSON format
        :param json_file: The path to the JSON file in
                          which to write the metadata
        :return: None
        """
        data = self.to_json()  # Must be in front of file open
        with open(json_file, "w") as f:
            f.write(json.dumps(
                data,
                sort_keys=True,
                indent=4,
                separators=(",", ": ")
            ))

    @staticmethod
    def jsonize_dict(data: Dict[str, MetaType]) -> dict:
        """
        Resolves all parameters of a dictionary and turns it into a
        json-compatible dictionary
        :param data: The dictionary resolve
        :return: The resolved JSON-compatible dictionary
        """
        for key, value in data.items():
            data[key] = value.to_json()
        return data

    @classmethod
    def is_subclass_of(cls, metadata_type: any) -> bool:
        """
        Checks if this metadata type is a subclass of another metadata type
        :param metadata_type: The metadata type to check for
        :return: True if the metadata object/class is a subclass of the
                 provided class
        """
        return issubclass(cls, metadata_type)
