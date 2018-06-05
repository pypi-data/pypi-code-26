# -*- coding: utf-8 -*-

"""CLI for PyBEL-CX."""

import logging
import sys

import click

from pybel import from_lines, to_bel_lines
from .cx import from_cx_file, to_cx_file

log = logging.getLogger(__name__)


@click.group()
def main():
    """Convert between BEL and CX."""


@main.command()
@click.option('-f', '--file', default=sys.stdin, help='CX document')
@click.option('-o', '--output', default=sys.stdout, help='BEL document')
def cx_to_bel(file, output):
    """Convert a CX document from STDIN and write a BEL Script to STDOUT."""
    try:
        graph = from_cx_file(file)
    except Exception:
        log.exception('error occurred while loading CX.')
        sys.exit(1)

    try:
        for line in to_bel_lines(graph):
            click.echo(line, file=file)
    except Exception:
        log.exception('error occurred in conversion to BEL.')
        sys.exit(2)

    sys.exit(0)


@main.command()
@click.option('-f', '--file', default=sys.stdin, help='CX document')
@click.option('-c', '--connection')
@click.option('-o', '--output', default=sys.stdout, help='BEL document')
def bel_to_cx(file, connection, output):
    """Convert a BEL Script from STDIN and write a CX document to STDOUT."""
    try:
        graph = from_lines(file, manager=connection)
    except Exception:
        log.exception('error occurred while loading BEL.')
        sys.exit(1)

    try:
        to_cx_file(graph, output)
    except Exception:
        log.exception('error occurred in conversion to CX.')
        sys.exit(2)

    sys.exit(0)


if __name__ == '__main__':
    main()
