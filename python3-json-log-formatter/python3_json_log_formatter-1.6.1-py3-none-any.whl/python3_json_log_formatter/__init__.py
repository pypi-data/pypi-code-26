#!/usr/bin/env python3
"""
This file is part of json_log_formatter.

json_log_formatter is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

json_log_formatter is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with json_log_formatter.  If not, see <http://www.gnu.org/licenses/>.
"""

from logging import Formatter
from json import (dumps, loads)
from datetime import (
    datetime
)
import re

RE_FORMAT_ARGS = re.compile(
    r'%(\([^\)]+\))?(?P<frmt>[bcdeEfFgGnosxX])'
    ).finditer

# See https://lstu.fr/5USChPA9 for details
CAST_TYPES = {
    's': str,

    'b': bin,
    'c': str,
    'd': int,
    'o': oct,
    'x': hex,
    'X': hex,
    'n': int,

    'e': float,
    'E': float,
    'f': float,
    'F': float,
    'g': float,
    'G': float,
}


class JsonFormatter(Formatter):
    """ Outputs log records in JSON format. """

    def __init__(self, attributes=None, json_kwargs=None,
                 resolve_args=True, datefmt=None, style='%'):
        """ Construct a new JSON formatter.

        :param attributes: Attributes of the log object to include.
            Default is `None`, which means include all attributes.

        :param json_kwargs: Keyword arguments directly passed into
            `json.dumps()`

        :param datefmt: Date format. See Python docs.

        :param style: Formatter style. See Python docs.

        :param resolve_args: Whether to inject `args` into `message`. Default
            is `True`. Setting to `False` will result in the json log entry
            to include both a `msg` and `args` item.
        """
        self.attributes = attributes
        self.json_kwargs = json_kwargs or {'indent': 2}
        self.resolve_args = resolve_args
        if 'indent' not in self.json_kwargs:
            self.json_kwargs['indent'] = 2
        super(JsonFormatter, self).__init__(datefmt=datefmt, style=style)

    def lets_make_a_date(self, timestamp):
        """ Return a tiemstamp as a date.

        :param timestamp: Timestamp to format.
        """
        if not self.datefmt:
            return timestamp
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime(self.datefmt)

    def try_cast(self, message, args):
        """ Cast unruly args to their respective types.

        Unfortunately, we must do this since Python's format args are *very*
        type-sensitive.

        :param message: Message to format.

        :param args: Tuple of args to format.
        """
        i = -1
        l_args = list(args)
        for match in iter(RE_FORMAT_ARGS(message)):
            i += 1
            f_char = match.group('frmt')
            cast_type = CAST_TYPES[f_char]
            # TODO: uncommnet line only for debugging.
            # print('casting {} to {}'.format(l_args[i], cast_type.__name__))
            l_args[i] = cast_type(l_args[i])
        return (message, tuple(l_args))

    def format(self, record):
        """ Format a record in JSON format.

        :param record: LogRecord to format.

        :return: String formatted as a json object.
        """
        data = {}
        for (a, v) in record.__dict__.items():
            if self.attributes is not None and a not in self.attributes:
                continue
            if any((a.startswith('_'), )):
                continue
            try:
                v2 = dict(v)
                data[a] = dumps(v2, **(self.json_kwargs or {}))
            except Exception as e:
                pass
            try:
                v2 = loads(v)
                data[a] = dumps(v2, **(self.json_kwargs or {}))
            except Exception as e:
                pass

            if isinstance(v, (float, int, bool)):
                data[a] = v
            elif isinstance(v, (list, tuple, set)):
                data[a] = type(v)([str(x) for x in v])
            elif isinstance(v, dict):
                data[a] = str(type(v)([(x, str(y)) for (x, y) in v.items()]))
            else:
                data[a] = str(v).replace('\\\\', '\\')
        if self.resolve_args:
            try:
                data['msg'] = data['msg'] % data['args']
            except TypeError as te:
                (data['msg'], data['args']) = self.try_cast(data['msg'],
                                                            data['args'])
            # Try again
            try:
                data['msg'] = data['msg'] % data['args']
            except TypeError as te:
                raise Exception('Formatting "{}" with {}: {}'.format(
                    data['msg'], data['args'], te
                ))
            del data['args']
        # Format the dates
        for k in ('created', ):
            data[k] = self.lets_make_a_date(data[k])
        # data['created'] = self.lets_make_a_date(data['created'])
        # Format the messages
        return dumps(data, **(self.json_kwargs or {})).replace('\\\\', '\\')
