# -*- encoding: utf-8

import functools
import sys


def log_on_error(fn):
    @functools.wraps(fn)
    def wrapper(event, context):
        try:
            fn(event, context)
        except Exception as err:
            print(f'event   = {event!r}', file=sys.stderr)
            print(f'context = {context!r}', file=sys.stderr)
            raise

    return wrapper
