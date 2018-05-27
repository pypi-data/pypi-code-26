#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""

import logging
from genericpath import isfile
from os.path import abspath, join, exists

import yaml

logger = logging.getLogger(__name__)

class Config(object):
    _config = None
    _environment = None

    def __init__(self):
        if not self._config:
            self.read_config()

    def __getitem__(self, item):
        return self._config[item]

    @property
    def environment(self):
        from testosterone.runner import TestosteroneRunner
        return TestosteroneRunner.get_instance().environment

    def read_config(self):
        if exists("context.py"):
            from context import CONTEXT as cfg
        else:
            from testosterone.runner import TestosteroneRunner
            runner = TestosteroneRunner.get_instance()

            config_path = abspath(join(runner.datadir, runner.project, "conf/%s.yaml" % self.environment))
            if not isfile(config_path):
                print("The config file for environment '%s' does not exist: %s" % (self.environment, config_path))
                exit(2)

            with open(config_path) as f:
                cfg = yaml.load(f)

        if not "hosts" in cfg:
            cfg["hosts"] = {}

        self._config = cfg
