# -*- coding: utf-8 -*-
#
# This file is part of fedscm_admin.
# Copyright © 2018 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
"""
Configuration related helper functions
"""
from __future__ import absolute_import
import os

import click
from six.moves import configparser


def get_config():
    """
    An abstraction of using ConfigParser for the project
    :return: ConfigParser object
    """
    config = configparser.ConfigParser()
    home_dir = os.path.expanduser('~')
    paths = [
        '/etc/fedscm-admin/config.ini',
        os.path.join(home_dir, '.config', 'fedscm-admin', 'config.ini'),
    ]
    if os.environ.get('FEDSCM_ADMIN_TEST_CONFIG', 'false').lower() == 'true':
        test_config_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../tests/test_config.ini'))
        paths.append(test_config_path)

    custom_config_path = os.environ.get('FEDSCM_ADMIN_CONFIG')
    if custom_config_path:
        if os.path.exists(custom_config_path):
            paths.append(custom_config_path)

    if not any(os.path.exists(path) for path in paths):
        raise click.ClickException('No configuration file was found')

    config.read(paths)
    return config


def get_config_item(config, item):
    """
    Gets a config item and throws a ClickException if it doesn't exist
    :param config: ConfigParser object from get_config
    :param item: string representing the item in the section you want
    (e.g. pagure_url)
    :return: string of the config item
    """
    try:
        return config.get('admin', item)
    except (configparser.NoOptionError, configparser.NoSectionError):
        read_me_url = 'https://pagure.io/fedscm_admin'
        error_msg = ('The "{0}" setting is not set in the "admin" section. '
                     'Please read {1}.'
                     .format(item, read_me_url))
        raise click.ClickException(error_msg)
