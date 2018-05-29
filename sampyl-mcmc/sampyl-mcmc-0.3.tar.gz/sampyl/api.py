"""
sampyl.api
~~~~~~~~~~~~~~~~~~~~

Model for classes and functions associated with building a model

:copyright: (c) 2018 by Mat Leonard.
:license: MIT, see LICENSE for more details.

"""

from sampyl.core import np


class Model():
    def __init__(self):

        self._logps = []

    def logp(self):

        if -np.inf in set(self._logps):
            return -np.inf

        total_logp = sum(self._logps)
        return total_logp

    def add(self, *args):
        self._logps.extend(args)
