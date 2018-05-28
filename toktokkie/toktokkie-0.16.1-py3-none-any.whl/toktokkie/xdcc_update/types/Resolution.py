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

from enum import Enum
from toktokkie.metadata.types.MetaType import MetaPrimitive


class ResolutionOption(Enum):
    """
    Enum that lists all resolution options for XDCC updating
    """

    X1080p = "1080p"
    X720p = "720p"
    X480p = "480p"


class ResolutionFormat(Enum):
    """
    Enum that lists the formats in which a resolution can be displayed
    """

    P_NOTATION = "@{Y}p"
    X_NOTATION = "@{X}x@{Y}"


class Resolution(MetaPrimitive):
    """
    A resolution that's either 1080p, 720p, 480p
    """

    def __init__(self, resolution_option: ResolutionOption):
        """
        Initializes the resolution object
        :param resolution_option: The resolution option
        """
        self.resolution_option = resolution_option
        if self.resolution_option == ResolutionOption.X1080p:
            self.x, self.y = (1920, 1080)
        elif self.resolution_option == ResolutionOption.X720p:
            self.x, self.y = (1280, 720)
        elif self.resolution_option == ResolutionOption.X480p:
            self.x, self.y = (720, 480)
        else:
            self.x, self.y = (0, 0)

    def to_json(self) -> str:
        """
        Turns the object into a string
        :return: The dictionary representation of the resolution
        """
        return str(self.resolution_option.value)

    @classmethod
    def from_json(cls, json_data: any):
        """
        Generates a resolution object from JSON data
        :param json_data: The JSON data
        :return: The generated Resolution object
        """
        return cls.parse(json_data)

    @classmethod
    def parse(cls, string: str):
        """
        Initializes the resolution object based on a string in the
        format like 1080p. Errors in the string will raise a ValueError
        :param string: The string to parse
        """
        error_msg = "Options: ["
        for option in ResolutionOption:
            error_msg += option.value + ","
            if option.value == string.lower():
                return cls(option)
        raise ValueError(error_msg + "]")

    def __str__(self) -> str:
        """
        :return: A string representation of the resolution
        """
        return str(self.resolution_option.value)

    def to_format(self, resolution_format: ResolutionFormat):
        """
        Formats the resolution into a different format
        :param resolution_format:
        :return:
        """
        pattern = resolution_format.value
        return pattern\
            .replace("@{X}", str(self.x))\
            .replace("@{Y}", str(self.y))
