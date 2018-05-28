# coding=utf-8

"""
    parse2csv
    ~~~~~~~~~

    A command-line tool to parse multiple files for named patterns and write the
    values in CSV format.

    :copyright: (c) 2018 by Ali Ghaffaari.
    :license: MIT, see LICENSE for more details.
"""

from .parse2csv import generate  #noqa
from .parse2csv import list_dialects  #noqa
from .parse2csv import default_dialect  #noqa
from .reduct import Reduce  #noqa
