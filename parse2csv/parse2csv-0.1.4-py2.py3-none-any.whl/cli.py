# coding=utf-8

"""
    parse2csv.cli
    ~~~~~~~~~~~~~

    This module implements command-line interface.

    :copyright: (c) 2018 by Ali Ghaffaari.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import print_function
import sys

import click

from . import parse2csv
from . import release


@click.command()
@click.argument('inputs', type=click.File('r'), nargs=-1)
@click.option('-o', '--output', type=click.File('w'), default="-",
              help="Write to this file instead of stdout.")
@click.option('-c', '--configfile', type=click.File('r'), required=True,
              help="Use this configuration file.")
@click.option('-d', '--dialect', type=click.Choice(parse2csv.list_dialects()),
              default=parse2csv.default_dialect(), show_default=True,
              help="Use this CSV dialect.")
@click.version_option(version=release.__version__)
def cli(**kwargs):
    """Parse the input files for named patterns and dump their values in CSV
    format.
    """
    if not kwargs.get('inputs'):
        print('[ERROR] No input file provided', file=sys.stderr)
        exit(1)

    parse2csv.generate(output=kwargs.get('output'),
                       inputs=kwargs.get('inputs'),
                       configfile=kwargs.get('configfile'),
                       dialect=kwargs.get('dialect'))
