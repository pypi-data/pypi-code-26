# -*- coding: utf-8 -*-
""" Various utilities used across the code base."""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import re
from logging import getLogger

# 3rd party imports

# local imports


L = getLogger(__name__)


def remove_indent(text):
    """ Remove common indent from the text. """
    lines = text.split(os.linesep)

    min_indent = -1
    for line in (l for l in lines if l.strip()):
        without_indent = line.lstrip()
        indent = len(line) - len(without_indent)

        if min_indent == -1 or indent < min_indent:
            min_indent = indent

    return '\n'.join(l[min_indent:] for l in lines)


def filter_sites(sites, filters):
    """ Filter site list using a set of given filters. """
    if not filters:
        return sites

    results = []

    for site in sites:
        if next((True for f in filters if f.match(site)), False):
            results.append(site)

    return results


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
