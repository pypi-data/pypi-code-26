# Copyright (C) 2018 Yuval Langer
#
# This file is part of Meditate.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Meditate.

Usage:
  meditate [options]
           [--session-sound=PATH]
           [--interval-sound=PATH]
           [--session-duration=TIME]
           [--interval-duration=TIME]
  meditate [options]

Options:
  -h --help
      This hopefully helpful help message.

  --usage
      A shorter version of the above.

  -v --verbose
      Print all the logging messages!

  --debug
      Same as the above.

  --interval-sound=PATH
      Path to a wave file signifying the passage of time,
        reminding you to come back from mind wandering.

  --start-stop-sound=PATH
      Path to a wave file denoting the start and stop of a session.

  --session-duration=TIME
      Total meditation session time in seconds.
        [default: 1200s]

  --interval-duration=TIME
      Length of each interval in seconds.
        [default: 400s]
"""

import datetime
import itertools
import json
import logging
import os
import pathlib
import re
import typing

import attr


import docopt

import pkg_resources

import simpleaudio

import trio


class MeditateException(Exception):
    """Our base exception class."""

    pass


class DurationConfigurationException(MeditateException):
    """Bad duration input."""

    pass


def validate_path_exists(
        instance: typing.Any,
        attribute: typing.Any,
        value: pathlib.Path,
) -> None:
    """Make sure that the provided path's file actually exists."""
    logger = logging.getLogger(__name__)

    value.resolve(strict=True)
    logger.debug("Path %s resolved", value)


def convert_to_path(
        path: os.PathLike,
) -> pathlib.Path:
    """Mimick `pathlib.Path()`, but doesn't confuse `mypy`'s type analysis."""
    return pathlib.Path(path).expanduser().absolute()


def convert_to_float(
        number: typing.Union[str, int, float],
) -> float:
    """Mimick `float()`, but doesn't confuse `mypy` type analysis."""
    return float(number)


DEFAULT_SOUND_PATH = pathlib.Path(
    pkg_resources.resource_filename(
        __name__,
        "data/sound/140128__jetrye__bell-meditation-cleaned.wav",
    ),
)


@attr.s
class Configuration:
    """Configuration."""

    interval_duration: float = attr.ib(
        converter=convert_to_float,
    )
    session_duration: float = attr.ib(
        converter=convert_to_float,
    )
    start_stop_sound_path: pathlib.Path = attr.ib(
        default=DEFAULT_SOUND_PATH,
        validator=validate_path_exists,
        converter=convert_to_path,
    )
    interval_sound_path: pathlib.Path = attr.ib(
        default=DEFAULT_SOUND_PATH,
        validator=validate_path_exists,
        converter=convert_to_path,
    )


possible_duration_pattern = re.compile(
    "(" + "|".join(
        f"{h}{m}{s}"
        for h in ("", r"\d+h")
        for m in ("", r"\d+m")
        for s in ("", r"\d+s")
        if h or m or s
    ) + ")",
)


def parse_duration_input(
        *,
        input_str: str,
) -> float:
    """Parse a string representing a duration into number of seconds."""
    old_input_str = input_str
    input_str = input_str.strip()

    maybe_matching_duration = re.search(
        r"^((?P<hours>[0-9]+)h)?"
        r"((?P<minutes>[0-9]+)m)?"
        r"((?P<seconds>[0-9]+)s)?$",
        input_str,
    )
    matching_duration = (
        maybe_matching_duration.groupdict()
        if maybe_matching_duration
        else {}
    )

    maybe_hours = matching_duration.get("hours")
    maybe_minutes = matching_duration.get("minutes")
    maybe_seconds = matching_duration.get("seconds")

    if not any((
            maybe_hours,
            maybe_minutes,
            maybe_seconds,
    )):
        raise DurationConfigurationException(
            f"""Received: "{old_input_str}"
Input must be positive and in the shape of the following examples:
1h4m2s, 4m3s, 1h4m, 2h4s, 1h, 60m, 3600s""",
        )

    hours = int(maybe_hours) if maybe_hours else 0
    minutes = int(maybe_minutes) if maybe_minutes else 0
    seconds = int(maybe_seconds) if maybe_seconds else 0

    total_seconds = (
        60.0 * 60 * hours +
        60 * minutes +
        seconds
    )

    return total_seconds


@attr.s
class Session:
    """Meditation session."""

    configuration: Configuration = attr.ib()

    def __attrs_post_init__(self) -> None:
        """Load files into memory."""
        self.interval_wave_object = simpleaudio.WaveObject.from_wave_file(
            self.configuration.interval_sound_path.as_posix(),
        )
        self.start_stop_wave_object = simpleaudio.WaveObject.from_wave_file(
            self.configuration.start_stop_sound_path.as_posix(),
        )

    async def meditate(self) -> None:
        """Start meditation session."""
        print(
            f"{datetime.datetime.utcnow()}: Start a "
            f"{self.configuration.session_duration} "
            f"seconds meditation.",
        )
        self.start_stop_wave_object.play()

        with trio.move_on_after(self.configuration.session_duration):
            for i in itertools.count(1):
                print(
                    f"{datetime.datetime.utcnow()}: Interval {i} starts. "
                    f"({self.configuration.interval_duration} seconds)",
                )

                await trio.sleep(self.configuration.interval_duration)
                self.interval_wave_object.play()

        print(f"{datetime.datetime.utcnow()}: End meditation.")
        self.start_stop_wave_object.play()
        await trio.sleep(5)
        self.start_stop_wave_object.play()
        await trio.sleep(5)
        self.start_stop_wave_object.play().wait_done()
        print(f"{datetime.datetime.utcnow()}: End meditation.")


def load_user_configuration_file() -> Configuration:
    """Load user configuration file."""
    _home = pathlib.Path('~').expanduser()
    xdg_config_home = pathlib.Path(
        os.environ.get('XDG_CONFIG_HOME')
        or (_home / ".config"),
    ) / "meditate"
    # TODO: Replace with ConfigParse
    config_filepath = xdg_config_home / "meditate.json"
    with open(config_filepath, 'r') as f:
        configuration = Configuration(**json.load(f))

    return configuration


class AllNonesException(MeditateException):
    """All provided arguments were None."""

    pass


def first_not_none(*maybes):
    """Return first non-`None`."""
    for maybe in maybes:
        if maybe is not None:
            return maybe
    raise AllNonesException


def load_config(
        *,
        command_line_arguments: dict,
) -> Configuration:
    """Load configuration.

    Use command line arguments,
      or user configuration (TODO),
      or default configuration.
    """
    logger = logging.getLogger(__name__)

    interval_duration = float(
        parse_duration_input(
            input_str=command_line_arguments["--interval-duration"],
        ),
    )
    session_duration = float(
        parse_duration_input(
            input_str=command_line_arguments["--session-duration"],
        ),
    )


    our_configuration = Configuration(
        interval_duration=interval_duration,
        session_duration=session_duration,

    )

    if command_line_arguments["--interval-sound"]:
        our_configuration.interval_sound_path = pathlib.Path(
            command_line_arguments["--interval-sound"],
        ).expanduser().absolute()
    if command_line_arguments["--start-stop-sound"]:
        our_configuration.start_stop_sound_path = pathlib.Path(
            command_line_arguments["--start-stop-sound"],
        ).expanduser().absolute()

    logger.debug("Configuration: %s", our_configuration)

    return our_configuration


def main() -> None:
    """Run program."""
    command_line_arguments = docopt.docopt(__doc__)

    if (
            command_line_arguments.get("--verbose")
            or command_line_arguments.get("--debug")
    ):
        logging.basicConfig(level="DEBUG")

    configuration = load_config(
        command_line_arguments=command_line_arguments,
    )

    session = Session(configuration=configuration)

    trio.run(session.meditate)


if __name__ == '__main__':
    main()
