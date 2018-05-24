"""pdf_to_json: Converting PDF calendars to JSON

Usage:
  pdf_to_json  <calendar_name.pdf>

Options:
  -h --help         Show this screen.
  --to-file=<t/f>   Enter true or false to save the file [default: True]
  --version         Show version.

"""
import re
import os
import json
import pathlib
import subprocess
from fuzzywuzzy import fuzz, process
from ..classification.constants_and_regexes import (REGEXES, DANCE_STYLES,
                                                    CLASS_CATEGORIES)
from ..jsonproc.process_cal import split_on_timestamps, group_event_strings
from ..jsonproc.cal_cleaner import pre_clean_calendar, post_clean_calendar

__version__ = "0.1.0"
__author__ = "Vincent Chov"
__license__ = "MIT"


def parse_calendar(json_filename, to_file=False):
    raw_filename = json_filename.replace('.json', '')
    cal = tabula_pdf_to_raw_json(raw_filename)
    assert type(cal[0]['data']) is list
    raw_data = cal[0]['data']
    pre_cleaned = pre_clean_calendar(raw_data)
    cal_data = post_clean_calendar(pre_cleaned)

    input_path = 'JSONs/{}.json'.format(raw_filename)
    output_path = 'Output/{}.json'.format(raw_filename)

    if to_file is True:
        with open(output_path, 'w') as output_file:
            output_file.write(json.dumps(cal_data, indent=4, sort_keys=True))
    else:
        print(json.dumps(cal_data, indent=4, sort_keys=True))
        return cal_data


def tabula_pdf_to_raw_json(pdf_filename):
    """
        Takes a PDF filename with or without its extension and returns a JSON
        outputted by tabula-cli.jar that's also saved to the JSONs folder.
    """
    # Write the input/output paths using the filename
    # Remove the PDF extension if it was accidentally supplied
    pathlib.Path('JSONs').mkdir(parents=True, exist_ok=True)
    pathlib.Path('PDFs').mkdir(parents=True, exist_ok=True)
    pathlib.Path('Output').mkdir(parents=True, exist_ok=True)
    raw_filename = pdf_filename.replace('.pdf', '')
    input_path = 'PDFs/{}.pdf'.format(raw_filename)
    output_path = 'JSONs/{}.json'.format(raw_filename)

    # Guess the area of the table, extract with lattice mode, output JSON
    options = ['java', '-jar', 'tabula-cli.jar', input_path, '--guess',
               '--lattice', '--format', 'JSON', '--outfile', output_path]

    # Wait until the command to convert the PDF to JSON to load and return it
    conversion_proc = subprocess.Popen(options)
    conversion_proc.wait()
    with open(output_path) as json_file:
        converted_json = json.load(json_file)

    return converted_json


if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)
    pdf_path = args["<calendar_name.pdf>"]
    to_file = 'true' in args["to_file"].lower()
    converted_json = parse_calendar(pdf_path, to_file=to_file)
