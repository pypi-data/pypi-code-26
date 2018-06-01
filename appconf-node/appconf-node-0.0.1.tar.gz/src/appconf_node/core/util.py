# -*- coding: utf-8 -*-
""" Various utilities used across the code base."""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
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
