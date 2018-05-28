# coding=utf-8

"""
    parse2csv.parse2csv
    ~~~~~~~~~~~~~~~~~~~

    The main module.

    :copyright: (c) 2018 by Ali Ghaffaari.
    :license: MIT, see LICENSE for more details.
"""

from collections import defaultdict
import csv

import yaml
import parse

from .reduct import Reduce


def process(data, funcs):
    """Process multi-value fields by applying specified reduce function.

    Args:
        data : dict
            The data to be processed.
        funcs : dict
            A dictionary specifying the reduce function for each multi-value
            field. In case that it is not specified for a particular field it
            is assumed to be `Reduce.first` function.
    """
    reducts = defaultdict(lambda: 'first')
    reducts.update(funcs)
    proc_data = dict()
    for key, values in data.items():
        proc_data[key] = Reduce.call(reducts[key], values)
    return proc_data


def parse_all(content, patterns):
    """Extract the fields from the content.

    Args:
        content : str
            The content to be parsed.
        patterns : list of str
            The list of patterns to find.
    """
    data = defaultdict(list)
    for pat in patterns:
        for match in parse.findall(pat, content):
            for key, value in match.named.items():
                data[key].append(value)
    return data


def list_dialects():
    """Get list of supported CSV dialects."""
    return csv.list_dialects()


def default_dialect():
    """Get default CSV dialects."""
    return 'unix'


def generate(output, inputs, configfile, dialect='unix'):
    """Generate CSV file.

    Args:
        output : file-like object
            Output file.
        inputs : list of file-like objects
            Input files to be processed.
        configfile : file-like object
            Input configuration file.
        dialect : str
            This string specifies the dialect of the output CSV file.
    """
    config = yaml.load(configfile)
    writer = csv.DictWriter(output,
                            fieldnames=config['fields'],
                            restval=config.get('missing_value', 'NA'),
                            extrasaction='ignore',
                            dialect=dialect,
                            quoting=csv.QUOTE_NONE)
    writer.writeheader()
    for inp in inputs:
        data = parse_all(inp.read(), config['patterns'])
        proc_data = process(data, config.get('reduce', {}))
        writer.writerow(proc_data)
