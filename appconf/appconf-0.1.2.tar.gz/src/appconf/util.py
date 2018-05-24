# -*- coding: utf-8 -*-
""" Various utilities used across the code base."""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import json

# 3rd party imports
from tabulate import tabulate

# local imports
from . import log
from . import nginx


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


def print_sites_json(sites, indent=2):
    """ Print sites as JSON. """
    print(json.dumps([site.as_dict() for site in sites], indent=indent))


def print_sites_pretty(sites):
    """ Pretty print site list as a colored table. """
    fields = nginx.Site.fields()
    fields.remove('config')

    print(tabulate(
        [s.as_row(fields) for s in colored_sites(sites)],
        headers=fields
    ))


def colored_sites(sites):
    """ Colour selected fields in a Site instance"""
    for s in sites:
        colored = nginx.Site(**s.as_dict())
        colored.name = log.cfmt('^1{}^0', s.name)
        colored.status = _format_status(s.status)

        yield colored


def _format_status(status):
    """ Add color to the app status. """
    if status == 'live':
        color = '^32'
    elif status == 'broken':
        color = '^31'
    else:
        color = '^90'

    return log.cfmt(color + status + '^0')
