# coding=utf-8

"""
    parse2csv.reduct
    ~~~~~~~~~~~~~~~~

    Reduction module.

    :copyright: (c) 2018 by Ali Ghaffaari.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division
import os
import glob
import re


class Reduce(object):
    """Supported reduce functions."""
    @staticmethod
    def call(signiture, values):
        """Call the reduce function specified by its signiture on `values`.

        Args:
            signiture : list or str
                Function signiture (usually the entry associated with the field
                under 'reduce' entry in the config file) is a string determining
                the name of the function or a list in which the first element is
                string (mandatory) indicating the function name and the other
                elements are optional specifying the reduce function arguments.
            values : list
                The list of values to be reduced.
        """
        func_name = ''
        args = list()
        if isinstance(signiture, list):
            func_name = signiture[0]
            args = signiture[1:]
        elif isinstance(signiture, str):
            func_name = signiture
        else:
            raise RuntimeError("unknown reduce function signiture")
        func = getattr(Reduce, func_name)
        return func(values, *args)

    @staticmethod
    def first(values):
        """Get the first value."""
        return values[0]

    @staticmethod
    def last(values):
        """Get the last value."""
        return values[-1]

    @staticmethod
    def avg(values):
        """Get average of the values."""
        return sum(values) / len(values)

    @staticmethod
    def avg_tp(values):
        """Get average of the values by preserving its original type."""
        return type(values[0])(sum(values) / len(values))

    @staticmethod
    def count(values):
        """Get the number of values."""
        return len(values)

    @staticmethod
    def min(values):
        """Get the minimum value."""
        return min(values)

    @staticmethod
    def max(values):
        """Get the maximum value."""
        return max(values)

    @staticmethod
    def sum(values):
        """Get the sum of values."""
        return sum(values)

    @staticmethod
    def concat(values):
        """Get concatenation of the values."""
        return ''.join(values)

    @staticmethod
    def filesize(values):
        """Get the file size in bytes."""
        fpath = os.path.realpath(values[0])
        return os.stat(fpath).st_size

    @staticmethod
    def filesize_glob(values):
        """Get cumulative size of the files prefixed by `prefix` in bytes."""
        prefix = values[0] + "*"
        retval = 0
        for fpath in glob.glob(prefix):
            retval += Reduce.filesize([fpath])
        return retval

    @staticmethod
    def parse(values, pattern):
        """Parse concatenation of the values and get the concatenation of the
        matched groups by input regex `pattern`.
        """
        text = ''.join(values)
        return ''.join(re.match(pattern, text).groups())
