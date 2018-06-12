# -*- coding: utf-8 -*-

import sys
import time
from pathlib import Path

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


def per_chunk(iterable, n=1, fillvalue=None):
    """
    From http://stackoverflow.com/a/8991553/610569
        >>> list(per_chunk('abcdefghi', n=2))
        [('a', 'b'), ('c', 'd'), ('e', 'f'), ('g', 'h'), ('i', None)]
        >>> list(per_chunk('abcdefghi', n=3))
        [('a', 'b', 'c'), ('d', 'e', 'f'), ('g', 'h', 'i')]
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def timing(f, output_to=sys.stderr, **kwargs):
    """ Decorator to time function. """
    def wrap(*args, **kwargs):
        time_start = time.time()
        ret = f(*args)
        #took = time.time() - time_start
        took = time.strftime("%H:%M:%S", time.gmtime(time.time() - time_start))
        print('{} took {}'.format(f.__name__, took), file=output_to)
        return ret
    return wrap

def absolute_path(path):
    return str(Path(path).resolve())
