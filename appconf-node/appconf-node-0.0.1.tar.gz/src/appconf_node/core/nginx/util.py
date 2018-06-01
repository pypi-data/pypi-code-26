# -*- coding: utf-8 -*-
""" Various utilities used across the code base."""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import json
from logging import getLogger

# 3rd party imports
from tabulate import tabulate

# local imports
from .site import Site

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


def print_sites(sites, format='pretty', **printer_params):
    printer = None

    if format == 'tab':
        printer = print_sites_pretty
    elif format == 'json':
        printer = print_sites_json

    return printer(sites, **printer_params)


def print_sites_json(sites, indent=2):
    """ Print sites as JSON. """
    print(json.dumps([site.as_dict() for site in sites], indent=indent))


def print_sites_pretty(sites):
    """ Pretty print site list as a colored table. """
    fields = Site.fields()
    fields.remove('config')

    print(tabulate(
        [s.colored().as_row(fields) for s in sites],
        headers=fields
    ))
