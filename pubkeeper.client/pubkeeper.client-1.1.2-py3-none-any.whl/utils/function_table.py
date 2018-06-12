"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.exceptions import NoProtocolError


class FunctionTable(object):
    """ To be used by any protocol dependant class, e,g, Brewer, Patron
    """

    def __init__(self):
        self._functions = {}

    def set(self, functions):
        self._functions = functions

    def reset(self, keep=[]):
        self._functions = {k: v for k, v in self._functions.items()
                           if k in keep}

    def invoke(self, fn, *args, **kwargs):
        if fn not in self._functions:
            raise NoProtocolError()

        return self._functions[fn](*args, **kwargs)
