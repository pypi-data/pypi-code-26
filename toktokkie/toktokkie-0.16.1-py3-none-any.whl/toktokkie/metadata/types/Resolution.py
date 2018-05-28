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


class Resolution(MetaPrimitive):
    """
    A resolution with an X and Y dimension
    """

    def __init__(self, x: int, y: int):
        """
        Initializes the resolution object
        :param x: The X dimension of the resolution
        :param y: The Y dimension of the resolution
        """
        self.x = x
        self.y = y

    def to_json(self) -> Dict[str, int]:
        """
        Turns the object into a JSON-compatible dictionary
        :return: The dictionary representation of the resolution
        """
        return {
            "x": self.x, "y": self.y
        }

    @classmethod
    def from_json(cls, json_data: any):
        """
        Generates a resolution object from a json dictionary
        :param json_data: The JSON dictionary
        :return: The generated Resolution object
        """
        return cls(json_data["x"], json_data["y"])

    @classmethod
    def parse(cls, string: str):
        """
        Initializes the resolution object based on a string in the
        format like 1920x1080. Errors in the string will raise a ValueError
        :param string: The string to parse
        """
        try:
            split = string.lower().split("x")
            x = int(split[0])
            y = int(split[1])
            return cls(x, y)
        except IndexError:
            raise ValueError()

    def __str__(self) -> str:
        """
        :return: A string representation of the resolution
        """
        return str(self.x) + "x" + str(self.y)
