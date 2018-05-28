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
from colorama import Fore, Style
from typing import Dict, List, Type
from toktokkie.metadata import TvSeries, check_metadata_subtype
from toktokkie.renaming.helper.resolve import resolve_season, get_episode_files
from toktokkie.renaming.schemes.Scheme import Scheme
from toktokkie.renaming.agents.Agent import Agent
from toktokkie.renaming.Episode import Episode


class Renamer:
    """
    Class that handles the renaming of a series
    """

    def __init__(self, path: str, metadata: TvSeries,
                 scheme: Type[Scheme], agent: Type[Agent]):
        """
        Initializes the Renamer. ValueErrors will be thrown if an error
        is encountered at any point during the initialization process
        :param path: The path to the directory to rename
        :param metadata: The metadata to use for information
        :param scheme: The scheme to use for renaming
        :param agent: The agent to use for renaming
        """

        self.path = path
        self.metadata = metadata
        self.scheme = scheme
        self.agent = agent

        required_metadata_type = agent.id_type.value
        if not check_metadata_subtype(self.metadata, required_metadata_type):
            raise ValueError("Agent Type not applicable to metadata")

        self.raw_episodes = self.parse_directory()
        self.episodes = self.initialize_episodes()

    def parse_directory(self) -> Dict[int, Dict[str, str or List[int]]]:
        """
        Parses the directory provided as self.path, searches for episode
        content. Only files not starting with "." are included
        :return: A dictionary keyed by season, containing information about
                 the season's episodes by name, path and agent IDs
        """

        episodes = {}
        for season in self.metadata.seasons.list:
            season_path = os.path.join(self.path, season.path)
            season_number = resolve_season(season_path)
            season_ids = season.get_agent_ids(self.agent.id_type)

            if season_ids is None:
                raise ValueError("Invalid agent ID type")

            if season_number not in episodes:
                episodes[season_number] = []

            for episode in get_episode_files(season_path):
                episodes[season_number].append({
                    "name": os.path.basename(episode),
                    "path": episode,
                    "agent_ids": season_ids
                })

        return episodes

    def initialize_episodes(self) -> List[Episode]:
        """
        Initializes the episode objects that generate the new name for the
        episodes
        :return: The list of generated Episode objects
        """

        episodes = []

        for season in sorted(self.raw_episodes):

            eps = sorted(self.raw_episodes[season], key=lambda x: x["name"])
            episode_count = \
                self.metadata.get_season_start(self.agent.id_type, season)
            excluded = self.metadata.get_agent_excludes(self.agent.id_type)

            for episode in eps:

                # Skip excluded episodes
                while True:
                    exclude = list(filter(
                        lambda x: x["S"] == season
                        and x["E"] == episode_count,
                        excluded
                    ))
                    if len(exclude) == 0:
                        break
                    else:
                        episode_count += 1

                # Check for multi episodes
                multi_range = None
                for multi_episode in self.metadata.get_multi_episode_ranges(
                        self.agent.id_type
                ):
                    multi_s = multi_episode["start"]["S"]
                    multi_e = multi_episode["start"]["E"]

                    if multi_s == season and multi_e == episode_count:
                        multi_range = (multi_e, multi_episode["end"]["E"])

                # noinspection PyTypeChecker
                episodes.append(Episode(
                    episode["path"],
                    self.metadata.name,
                    episode["agent_ids"],
                    season,
                    episode_count,
                    self.scheme,
                    self.agent,
                    multi_range
                ))

                # Skip multi-episode parts
                if multi_range is not None:
                    episode_count = multi_range[1]

                episode_count += 1

        return episodes

    def rename(self, noconfirm: bool):
        """
        Renames the contained files according to the naming scheme.
        :param noconfirm: Skips the confirmation phase if True
        :return: None
        """

        max_current = \
            len(max(self.episodes, key=lambda x: len(x.current)).current)

        for episode in self.episodes:
            print(Fore.LIGHTCYAN_EX + episode.current.ljust(max_current + 1) +
                  Style.RESET_ALL + " ---> " + Fore.LIGHTYELLOW_EX +
                  episode.new + Style.RESET_ALL)

        if not noconfirm:
            confirm = input("Start the renaming Process? (y/n)")
            if confirm != "y":
                print("Renaming aborted")
                sys.exit(0)

        for episode in self.episodes:
            episode.rename()
