#!/usr/bin/env python3
#  -*- coding: utf-8 -*-


try:
    from numba import jit
except ImportError:
    import warnings
    warning_text = \
        '\n\n' + '!' * 79 + '\n' + \
        'Could not import from numba.\n' + \
        'If numba is not installed, performance can be degraded in some functions.' + \
        '\n' + '!' * 79 + '\n'
    warnings.warn(warning_text)

    def _identity_decorator(*args, **kwargs):
        import types
        if (len(args) == 1) and isinstance(args[0], types.FunctionType):
            return args[0]

        def wrapper(fn):
            return fn

        return wrapper

    jit = _identity_decorator
