#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: chanconfig/multiple_config.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 18.05.2018
import logging
import os
import pkg_resources
import yaml

from yaml.parser import ParserError

from config import ReadConfigurationError


class MultipleConfig(object):
    """Class for configurations from stdin, config files and env.
    """
    def __init__(
        self, path, package=None, arguments={}, argument_settings={}
    ):
        """Initialize class with given path and optional package name.

        Args:
            path: a str
            package: a str, default None
            arguments: (dict) command arguments
            argument_settings: (dict) as {
                key: (env_name, process_method, default)
            }
        """
        self.logger = logging.getLogger(__name__)

        if package:
            try:
                path = pkg_resources.resource_filename(package, path)
            except ImportError as error:
                self.logger.exception(error)
                raise ReadConfigurationError(path, str(error))

        try:
            with open(path) as ymlfile:
                self.dict = yaml.load(ymlfile)
        except (IOError, ParserError) as error:
            self.logger.exception(error)
            raise ReadConfigurationError(path, str(error))

        self.update(arguments)

        self.update(self.process_argument_settings(argument_settings))

        self.logger.info(
            'Successfully read configurations from {0}'.format(path)
        )

    def __getattr__(self, name):
        return getattr(self.dict, name)

    def __eq__(self, other):
        return self.dict == other

    def __repr__(self):
        return str(self.dict)

    def update(self, update_dict):
        """Update values from another dict

        Args:
            update_dict: a ``dict``
        """
        for key, value in update_dict.items():
            if '--' not in key:
                continue
            update_dict[key.lstrip('--')] = value

        self.dict.update(update_dict)

    def process_argument_settings(self, argument_settings):
        """Process argument settings to a dict

        Args:
            argument_settings: (dict) settings of specified keys

        Return:
            (dict) as {key: val}
        """
        new_val_dict = {}
        for key, val in argument_settings.items():
            env, process, default = val
            new_val_dict[key] = self.dict.get(key)

            if env is not None and os.getenv(env) is not None:
                new_val_dict[key] = os.getenv(env)

            try:
                if process is not None:
                    new_val_dict[key] = process(new_val_dict[key])
            except Exception, e:
                self.logger.exception(e)
                self.logger.info('Set default value of {}'.format(key))
                new_val_dict[key] = None

            if new_val_dict[key] is None:
                new_val_dict[key] = default

        return new_val_dict
