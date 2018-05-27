#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""

import logging
import sys
from remotelib.policy import ContinueOnErrorPolicy, Policy

logger = logging.getLogger()

if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(name)-12s %(message)s", datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(sh)
    logger.setLevel(logging.DEBUG)

_policy = ContinueOnErrorPolicy

def set_policy(policy):
    global _policy
    assert issubclass(policy, Policy)

    _policy = policy
