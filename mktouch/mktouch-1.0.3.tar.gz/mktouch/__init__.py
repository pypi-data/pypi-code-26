#!/usr/bin/env python
import os
from public import public


def _mkdir(path):
    if path.find("/") > 0 and not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))


def _utime(path):
    try:
        os.utime(path, None)
    except Exception:
        open(path, 'a').close()


@public
def mktouch(path):
    if not path:
        return
    _mkdir(path)
    _utime(path)
