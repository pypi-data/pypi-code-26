#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""

import logging

logger = logging.getLogger(__name__)

class Script:

    def __init__(self, content=None):
        self.content = content

    @classmethod
    def from_file(cls, path):
        with open(path) as f:
            c = f.read()

        s = Script()
        s.content = c
        return s
