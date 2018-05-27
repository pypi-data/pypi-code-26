#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""

import logging

logger = logging.getLogger(__name__)

class ExecutionResult:
    def __init__(self):
        self.command = None
        self.stdin_stream = None
        self.stdout_stream = None
        self.stderr_stream = None
        self.exit_status = None

    def __str__(self):
        return self.stdout

    @property
    def stdout(self):
        return self.stdout_stream.read().decode("utf-8")

    @property
    def stderr(self):
        return self.stderr_stream.read().decode("utf-8")

    def raise_for_error(self):
        if self.exit_status != 0:
            raise RuntimeError("Command '%s' failed with exit status %s, output: %s" % (self.command, self.exit_status, self.stdout + self.stderr))
