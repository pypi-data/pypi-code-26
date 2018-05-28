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
import sys
import logging
from typing import Type, List
from xdcc_dl.entities.XDCCPack import XDCCPack
from xdcc_dl.logging.Logger import Logger
from xdcc_dl.xdcc import download_packs
from toktokkie.metadata.TvSeries import TvSeries
from toktokkie.renaming import Renamer, Agent, Scheme
from toktokkie.renaming.helper.resolve import resolve_season
from toktokkie.xdcc_update.UpdateInstructions import UpdateInstructions
from toktokkie.exceptions import MissingUpdateInstructionsException


class XDCCUpdater:
    """
    Class that handles XDCC updates
    """

    def __init__(self, path: str, metadata: TvSeries,
                 scheme: Type[Scheme], agent: Type[Agent],
                 create: bool = False):
        """
        Initializes the XDCCUpdater
        :param path: The path to the directory to update
        :param metadata: The metadata of the directory
        :param scheme: The naming scheme to use
        :param agent: The agent to use
        :param create: If set to True, will prompt user to create new
                       xdcc-update instructions
        """
        self.path = path
        self.metadata = metadata
        self.scheme = scheme
        self.agent = agent

        self.update_instructions_file = \
            os.path.join(path, ".meta", "xdcc-update.json")

        if create:

            if os.path.isfile(self.update_instructions_file):
                if input("File exists. Overwrite? (y/n)") != "y":
                    print("Aborted")
                    sys.exit(1)

            self.update_instructions = \
                UpdateInstructions.generate_from_prompts(path)
            self.update_instructions.write(self.update_instructions_file)

        elif not os.path.isfile(self.update_instructions_file):
            raise MissingUpdateInstructionsException()

        else:
            self.update_instructions = UpdateInstructions.from_json_file(
                self.update_instructions_file
            )

    def update(self):
        """
        Starts the XDCC Update procedure
        :return: None
        """
        episode_count = self.update_names()
        packs = self.search(episode_count + 1)

        # Download
        Logger.logging_level = logging.INFO
        download_packs(packs)

        self.update_names()

    def update_names(self) -> int:
        """
        Updates the names of the existing episodes and returns the
        episode number of the next missing episode.
        :return: The episode number of the next missing episode
        """

        episode_offset = self.update_instructions.episode_offset.to_json()
        destination = os.path.join(
            self.path,
            self.update_instructions.season_path.to_json()
        )
        episode_count = 0
        renamer = Renamer(self.path, self.metadata, self.scheme, self.agent)
        for episode in renamer.episodes:
            if episode.location == destination:
                episode_count += 1
                if episode.current != episode.new:
                    episode.rename()

        return episode_count + episode_offset

    def search(self, episode_count: int) -> List[XDCCPack]:
        """
        Conducts a search for the next episode
        :param episode_count: The episode to look for
        :return: A list of XDCCPacks to download
        """

        # Get Metadata
        season_path = self.update_instructions.season_path.to_json()
        destination = os.path.join(
            self.path, season_path
        )
        series_name = self.metadata.name.to_json()
        search_name = self.update_instructions.search_name.to_json()
        resolution = self.update_instructions.resolution
        search_pattern = self.update_instructions.search_pattern
        search_engine = self.update_instructions.search_engine
        preferred_bot = self.update_instructions.preferred_bot.to_json()

        # Search
        search_term = search_pattern.generate_search_term(
            search_name, episode_count, resolution
        )
        packs = search_engine.search(search_term)
        packs = list(filter(lambda x: search_pattern.check_search_result(
            search_name, episode_count, resolution, x.get_filename()
        ), packs))
        preferred = list(filter(lambda x: x.get_bot() == preferred_bot, packs))

        if len(preferred) >= 1:
            pack = preferred[0]
        elif len(packs) >= 1:
            pack = packs[0]
        else:
            return []  # Premature exit if no packs found

        # Generate episode name
        season = resolve_season(season_path)
        episode_name = self.scheme.generate_episode_name(
            series_name, season, episode_count, "Episode " + str(episode_count)
        )

        pack.set_directory(destination)
        pack.set_filename(episode_name, override=True)
        pack.set_original_filename(
            pack.original_filename.replace("'", "_")
        )  # Fixes filenames

        # Recursively check for next episode
        return [pack] + self.search(episode_count + 1)
