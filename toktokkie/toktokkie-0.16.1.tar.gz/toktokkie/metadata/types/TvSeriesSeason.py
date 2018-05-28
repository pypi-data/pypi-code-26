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

from typing import Dict, List
from toktokkie.metadata.helper.prompt import prompt_user
from toktokkie.metadata.types.MetaType import MetaType, Str
from toktokkie.metadata.types.AgentIdType import AgentIdType
from toktokkie.metadata.types.CommaList import IntCommaList,\
    LanguageCommaList, ResolutionCommaList, Language, Resolution


class TvSeriesSeason(MetaType):
    """
    A TV Series Season that can easily be serialized into a dictionary
    """

    default_audio_languages = LanguageCommaList([Language("eng")])
    """
    The default audio languages used in the prompt for this class
    """

    default_subtitle_languages = LanguageCommaList([])
    """
    The default subtitle languages used in the prompt for this class
    """

    default_resolutions = ResolutionCommaList([Resolution(1920, 1080)])
    """
    The default resolutions used in the prompt for this class
    """

    def __init__(self,
                 path: Str,
                 name: Str,
                 tvdb_ids: IntCommaList,
                 audio_langs: LanguageCommaList,
                 subtitle_langs: LanguageCommaList,
                 resolutions: ResolutionCommaList):
        """
        Initializes the TV Series Season
        :param path: The name of the season's directory
        :param name: The name of the season
        :param tvdb_ids: The TVDB Ids of the season
        :param audio_langs: The audio languages of the season
        :param subtitle_langs: The subtitle languages of the season
        :param resolutions: The resolutions of the season
        """
        self.path = path
        self.name = name
        self.tvdb_ids = tvdb_ids
        self.audio_langs = audio_langs
        self.subtitle_langs = subtitle_langs
        self.resolutions = resolutions

    def get_agent_ids(self, id_type: AgentIdType) -> List[int] or None:
        """
        Retrieves agent IDs for this season based on the provided ID type.
        If the ID type could not be applied to this TvSeries, None will
        be returned
        :param id_type: The Agent ID type to check for
        :return: The agent IDs for this season or None if not applicable
        """
        if id_type == AgentIdType.TVDB:
            return self.tvdb_ids.to_json()
        else:
            return None

    def to_json(self) -> Dict[str, any]:
        """
        Turns this object into a JSON-compatible dictionary
        :return: The dictionary
        """
        return {
            "path": self.path.to_json(),
            "name": self.name.to_json(),
            "tvdb_ids": self.tvdb_ids.to_json(),
            "audio_langs": self.audio_langs.to_json(),
            "subtitle_langs": self.subtitle_langs.to_json(),
            "resolutions": self.resolutions.to_json()
        }

    @classmethod
    def from_json(cls, json_data: any):
        """
        Generates a tv series season from JSON data
        :param json_data: The JSON data to use
        :return: The generated TvSeries object
        """
        return cls(
            Str.from_json(json_data["path"]),
            Str.from_json(json_data["name"]),
            IntCommaList.from_json(json_data["tvdb_ids"]),
            LanguageCommaList.from_json(json_data["audio_langs"]),
            LanguageCommaList.from_json(json_data["subtitle_langs"]),
            ResolutionCommaList.from_json(json_data["resolutions"])
        )

    @classmethod
    def _prompt_to_json(cls, name: str, previous=None) -> Dict[str, any]:
        """
        Generates a TvSeriesSeason JSON dictionary based on user prompts
        :param name: The name of the season
        :param previous: Optionally, provide a previously created season object
                         for more applicable default values
        :return: The generated TvSeriesSeason JSON dictionary
        """

        print("Season \"" + name + "\":")
        path = Str(name)
        name = prompt_user("Name", Str, Str(name))

        if previous is None:
            audio_defaults = cls.default_audio_languages
            subtitle_defaults = cls.default_subtitle_languages
            resolution_defaults = cls.default_resolutions
            tvdb_ids = prompt_user("TVDB IDs", IntCommaList)
        else:
            audio_defaults = previous.audio_langs
            subtitle_defaults = previous.subtitle_langs
            resolution_defaults = previous.resolutions
            tvdb_ids = prompt_user("TVDB IDs", IntCommaList, previous.tvdb_ids)

        audio_langs = prompt_user(
            "Audio Languages", LanguageCommaList, audio_defaults
        )
        subtitle_langs = prompt_user(
            "Subtitle Languages", LanguageCommaList, subtitle_defaults
        )
        resolutions = prompt_user(
            "Resolutions", ResolutionCommaList, resolution_defaults
        )

        return {
            "path": path.to_json(),
            "name": name.to_json(),
            "tvdb_ids": tvdb_ids.to_json(),
            "audio_langs": audio_langs.to_json(),
            "subtitle_langs": subtitle_langs.to_json(),
            "resolutions": resolutions.to_json()
        }

    @classmethod
    def prompt(cls, name: str, previous=None):
        """
        Generates a TvSeriesSeason object based on user prompts
        :param name: The name of the season
        :param previous: Optionally, provide a previously created season object
                         for more applicable default values
        :return: The generated TvSeriesSeason object
        """
        return cls.from_json(cls._prompt_to_json(name, previous))
