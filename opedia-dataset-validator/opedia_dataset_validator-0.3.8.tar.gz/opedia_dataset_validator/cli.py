from __future__ import absolute_import
from . import printer
from . import validator
import click
import json
import sys


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-a', '--all-errors', is_flag=True,
              help='Print all errors. [default: only the first error of each kind]')
@click.option('-v', '--value', is_flag=True,
              help='Print cell values in error report. [default: False]')
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.File(mode='w', encoding='utf-8'))
@click.version_option()
def main(all_errors, value, input, output):
    """A tool to validate Opedia dataset files.

    INPUT should be an Opedia dataset Excel file conforming to the sepcification
    at https://github.com/mdashkezari/opedia/tree/master/template.

    OUTPUT should be an output file path or - for STDOUT. Output will be in the
    form of a tab-delimited text file encoded in UTF-8.
    """
    errors = validator.validate(input)
    printer.print_tsv_errors(errors, output, print_all=all_errors,
                             header=True, print_value=value)
