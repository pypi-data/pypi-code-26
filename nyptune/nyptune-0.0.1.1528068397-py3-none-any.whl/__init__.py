"""Nyptune hides a copy of your environment in your Jypyter notebooks so that other people can easily reproduce your work"""

import time, os, platform

__version__ = "0.0.1." + str(int(time.time()))

from .magic import *


def load_ipython_extension(ipy):
    ipy.register_magics(CacheMagics)
