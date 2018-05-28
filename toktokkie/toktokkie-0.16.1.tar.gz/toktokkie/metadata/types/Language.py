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

from toktokkie.metadata.types.MetaType import MetaPrimitive


class Language(MetaPrimitive):
    """
    Class that parses ISO 639-2/B language codes
    """

    languages = {
        "eng": "English",
        "ger": "German",
        "jpn": "Japanese",
        "ita": "Italian",
        "spa": "Spanish",
        "fre": "French",
        "chi": "Chinese",
        "kor": "Korean",
        "rus": "Russian",
        "ara": "Arabic",
        "rum": "Romanian",
        "fin": "Finnish",
        "cze": "Czech",
        "dan": "Danish",
        "nor": "Norwegian",
        "swe": "Swedish"
    }  # TODO Implement more languages
    """
    Dictionary mapping ISO 639-2/B language codes to languages
    """

    def __init__(self, identifier: str):
        """
        Initializes the Language object
        :param identifier: The identifier to parse
        """
        if identifier.lower() not in self.languages:
            raise ValueError(identifier)
        self.language = identifier.lower()

    def get_language_name(self) -> str:
        """
        :return: The name of the language
        """
        return self.languages[self.language]

    def __str__(self) -> str:
        """
        :return: The language
        """
        return self.language

    def to_json(self) -> str:
        """
        :return: The language's JSON representation
        """
        return self.language
