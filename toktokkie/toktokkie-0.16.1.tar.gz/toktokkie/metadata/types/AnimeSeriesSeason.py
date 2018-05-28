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
from toktokkie.metadata.types.MetaType import Str
from toktokkie.metadata.types.AgentIdType import AgentIdType
from toktokkie.metadata.types.CommaList import IntCommaList,\
    LanguageCommaList, ResolutionCommaList, Language, Resolution
from toktokkie.metadata.types.TvSeriesSeason import TvSeriesSeason


class AnimeSeriesSeason(TvSeriesSeason):

    default_audio_languages = LanguageCommaList([Language("jpn")])
    """
    The default audio languages used in the prompt for this class
    """

    default_subtitle_languages = LanguageCommaList([Language("eng")])
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
                 mal_ids: IntCommaList,
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
        super().__init__(path, name, tvdb_ids,
                         audio_langs, subtitle_langs, resolutions)
        self.mal_ids = mal_ids

    def get_agent_ids(self, id_type: AgentIdType) -> List[int] or None:
        """
        Retrieves agent IDs for this season based on the provided ID type.
        If the ID type could not be applied to this season, None will
        be returned
        :param id_type: The Agent ID type to check for
        :return: The agent IDs for this season or None if not applicable
        """
        sup = super().get_agent_ids(id_type)
        if sup is not None:
            return sup
        elif id_type == AgentIdType.MYANIMELIST:
            return self.mal_ids.to_json()
        else:
            return None

    def to_json(self) -> Dict[str, any]:
        """
        Turns this object into a JSON-compatible dictionary
        :return: The dictionary
        """
        data = super().to_json()
        data["mal_ids"] = self.mal_ids.to_json()
        return data

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
            IntCommaList.from_json(json_data["mal_ids"]),
            LanguageCommaList.from_json(json_data["audio_langs"]),
            LanguageCommaList.from_json(json_data["subtitle_langs"]),
            ResolutionCommaList.from_json(json_data["resolutions"])
        )

    @classmethod
    def _prompt_to_json(cls, name: str, previous=None) -> Dict[str, any]:
        """
        Generates a AnimeSeriesSeason JSON dictionary based on user prompts
        :param name: The name of the season
        :param previous: Optionally, provide a previously created season object
                         for more applicable default values
        :return: The generated AnimeSeriesSeason JSON dictionary
        """
        data = super()._prompt_to_json(name, previous)
        if previous is None:
            mal_ids = prompt_user("Myanimelist IDs", IntCommaList)
        else:
            mal_ids = \
                prompt_user("Myanimelist IDs", IntCommaList, previous.mal_ids)
        data["mal_ids"] = mal_ids.to_json()
        return data
