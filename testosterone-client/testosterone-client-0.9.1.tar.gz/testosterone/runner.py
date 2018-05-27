#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""
import importlib
import inspect
import json
import logging
import unittest
from copy import deepcopy
from fnmatch import fnmatch
from os.path import abspath, join, isfile

import os

import sys
from pprint import pprint

import itertools
from time import time

from datetime import datetime

from testosterone.config import Config
from testosterone.test import Test
from testosterone.utils import locate, interactive_select

logger = logging.getLogger(__name__)
logging.getLogger("remotelib").setLevel(logging.WARNING)
logging.getLogger("paramiko").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

class TestosteroneRunner(object):
    __instance = None

    def __new__(cls):
        if TestosteroneRunner.__instance is None:
            TestosteroneRunner.__instance = object.__new__(cls)
        return TestosteroneRunner.__instance

    def __init__(self):
        self.project = None
        self.args = None

        self.config = Config()
        self.config.read_config()

    @classmethod
    def get_instance(cls):
        """

        @rtype: TestosteroneRunner
        """
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    @property
    def datadir(self):
        return self.args.data or abspath("data")

    @property
    def project_dir(self):
        return abspath(join(self.datadir, self.project))

    @property
    def environment(self):
        return self.args.environment

    def determine_project(self):
        project = self.args.project

        if project:
            assert project in os.listdir(self.datadir)

        else:
            all_projects = os.listdir(self.datadir)
            project = interactive_select(all_projects, "Please select project: (in the future you can skip this step by specifying -p/--project <name>)")

        self.project = project

    def fetch_tests(self):
        test_dir = join(self.project_dir, "tests")
        test_files = locate('*.py', test_dir)

        test_modules = []
        for test_file in test_files:
            name = test_file.replace(test_dir, "", 1)[1:]
            name = name.replace("/", ".")
            name = name[:-3]
            test_modules.append(name)

        return test_modules

    def run(self):
        self.determine_project()

        env_cfg = join(self.project_dir, "conf", "%s.yaml" % self.environment)
        if not isfile(env_cfg):
            logger.error("Environment '%s' is invalid, unable to find %s" % (self.environment, env_cfg))
            exit(2)
        
        self.config = Config()
        self.config.read_config()
        
        tests = self.fetch_tests()
        tests_to_run = []

        if self.args.test_name:
            if "*" in self.args.test_name:
                tests_to_run = [t for t in tests if fnmatch(t, self.args.test_name)]
            elif self.args.test_name in tests:
                tests_to_run = [self.args.test_name]
            else:
                logger.error("The selected test '%s' is unavailable" % self.args.test_name)

        if self.args.all:
            tests_to_run = deepcopy(tests)

        if not tests_to_run:
            available_tests = deepcopy(tests)
            available_tests.append("<all>")
            selected_test = interactive_select(available_tests, "Select a test to run (in the future you can skip this step by specifying -t/--test <name> or -a/--all)")
            if selected_test == "<all>":
                tests_to_run = deepcopy(tests)
            else:
                tests_to_run = [selected_test]
        
        sys.path.insert(0, join(self.project_dir, "tests"))

        runner = unittest.TextTestRunner()

        ## new
        test_classes = self.get_tests(tests_to_run[0])
        for test_class in test_classes:
            self.run_test_class(test_class)

        ## old
        suite_list = []
        for test in tests_to_run:
            s = unittest.defaultTestLoader.loadTestsFromName(test)
            suite_list.append(s)

        suite = unittest.TestSuite(suite_list)
        runner.run(suite)
        
        self.shutdown_services()

    def get_tests(self, module_name):
        test_classes = []

        mod = importlib.import_module(module_name)
        for key, value in mod.__dict__.items():
            if key.startswith("_"):
                continue

            if not inspect.isclass(value):
                continue

            if value == Test:
                continue

            if not issubclass(value, Test):
                continue

            test_classes.append(value)

        return test_classes

    def get_variations(self, test_class):
        variation_dict = test_class.VARIATIONS
        return [e for e in (dict(zip(variation_dict, x)) for x in itertools.product(*variation_dict.values()))]

    def run_test_class(self, test_class):
        # list<dict>
        variations = self.get_variations(test_class)

        for variation in variations:
            test_instance = test_class()
            test_instance.variation = variation
            for key, value in variation.items():
                setattr(test_instance, key, value)
            self.run_test(test_instance)

    def run_test(self, test_instance):
        for key in dir(test_instance):
            if not key.startswith("test_"):
                continue

            logger.info("Running: %s.%s::%s variation %s" % (test_instance.__module__, test_instance.__class__.__name__, key, json.dumps(test_instance.variation)))
            start = datetime.now()
            getattr(test_instance, key)()
            end = datetime.now()
            logger.info("Test finished successfully (duration %s)" % (end-start))

    def shutdown_services(self):
        print("shutting down services")
        from testosterone.web import WEB_REGISTRY
        for name, web in WEB_REGISTRY.items():
            web.shutdown()
        from testosterone.db import DB_REGISTRY
        for name, db in DB_REGISTRY.items():
            db.shutdown()
    