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
from typing import List


def resolve_season(season_path: str) -> int:
    """
    Setermines a season's season number based on the path's name
    :param season_path: The path to check
    :return: The season number
    """

    season_name = os.path.basename(season_path.lower())
    try:
        if season_name.startswith("season "):
            season_number = int(season_name.split(" ", 1)[1])
        else:
            season_number = 0
    except (IndexError, ValueError):
        season_number = 0
    return season_number


def get_episode_files(season_path: str) -> List[str]:
    """
    Searches a directory for all eligible episode files
    :param season_path: The path to check
    :return: A list of episode file paths
    """

    episodes = []

    for child in os.listdir(season_path):
        child_path = os.path.join(season_path, child)

        if os.path.isfile(child_path) and not child.startswith("."):
            episodes.append(child_path)

    return episodes
