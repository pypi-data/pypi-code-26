# -*- coding: utf-8 -*-
""" Logging helpers """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import re
import sys


class ShellColors(object):
    """ Simple utility for coloring shell output """
    COLOR_RE = re.compile(r'\^(\d{1,2})')

    def __init__(self, opcode):
        """ Create color formatter using the given opcode """
        self.opcode = opcode

    def __call__(self, msg, *args, **kw):
        """
        :param msg: Message
        :param args: Positional arguments for msg.format()
        :param kw: Keyword arguments for msg.format()
        :return: Formatted string
        """
        if len(args) or len(kw):
            msg = msg.format(*args, **kw)

        return ShellColors.COLOR_RE.sub(self.opcode, msg)


cfmt = ShellColors(opcode=r'\033[\1m')


def debug(msg, *args, **kw):
    """ Log debug message. """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    log_raw(cfmt('-- ^90{}^0', msg))


def info(msg, *args, **kw):
    """ Log info message. """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    log_raw(cfmt('-- ^32{}^0', msg))


def warning(msg, *args, **kw):
    """ Log warning message. """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    log_raw(cfmt('-- ^33{}^0', msg))


def err(msg, *args, **kw):
    """ Log error message. """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    log_raw(cfmt('-- ^31{}^0', msg))


def log_raw(msg):
    """ Raw log message.

    All other logging functions should call this one in the end.
    """
    print(msg, file=sys.stderr)
