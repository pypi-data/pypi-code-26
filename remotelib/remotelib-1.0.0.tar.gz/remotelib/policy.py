#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""

import logging
import sys

logger = logging.getLogger(__name__)

class PolicyError(Exception):
    pass

class Policy:
    @classmethod
    def handle_result(cls, result):
        pass

class StopOnErrorPolicy(Policy):
    @classmethod
    def handle_result(cls, result):
        if result.exit_status != 0:
            logger.error("command '%s' exited with exit code %s, stdout+stderr:" % (result.command, result.exit_status))
            [logger.error(line) for line in (result.stdout + result.stderr).splitlines()]
            raise PolicyError

class ContinueOnErrorPolicy(Policy):
    @classmethod
    def handle_result(cls, result):
        pass
