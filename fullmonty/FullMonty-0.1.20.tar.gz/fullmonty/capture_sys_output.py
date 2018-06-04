# coding=utf-8

"""
A context manager for capturing stdout and stderr.

from:  https://stackoverflow.com/questions/18651705/argparse-unit-tests-suppress-the-help-message
By:  Martijn Pieters https://stackoverflow.com/users/100297/martijn-pieters
"""
from contextlib import contextmanager
from cStringIO import StringIO

import sys


@contextmanager
def capture_sys_output():
    """
    Usage::

        with capture_sys_output() as (stdout, stderr):
            arg_parser.parse_known_args(['-h'])

        self.assertEqual(stderr.getvalue(), '')
        help_message = stdout.getvalue()

    """
    capture_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = capture_out, capture_err
        yield capture_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err
