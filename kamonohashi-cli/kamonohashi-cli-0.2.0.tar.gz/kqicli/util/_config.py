# -*- coding: utf-8 -*-
# Copyright 2018 NS Solutions Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function, absolute_import, with_statement

import sys
import json
import os
from click import ClickException

from kamonohashi.util._module_logger import get_logger

DEFAULT_CONFIG_FILE = os.path.expanduser('~/.kqi.config')

logger = get_logger(__name__)


def read_config():
    """Read config

    Return:
        config (dict): read config
    """
    logger.debug('Start to read config file')

    if os.path.exists(DEFAULT_CONFIG_FILE):
        with open(DEFAULT_CONFIG_FILE, 'r') as f:
            logger.debug('Finished to read a config file')
            return json.loads(f.read())
    else:
        raise ClickException("No configuration file(~/.kqi.config) is found. Log into KAMONOHASHI first to use 'account login' command.")


def write_config(server=None, token=None, timeout=30):
    config = {}
    if server:
        config['server'] = server
    if token:
        config['token'] = token
    if timeout:
        config['timeout'] = timeout
    with open(DEFAULT_CONFIG_FILE, 'w+') as f:
        logger.debug('Writing a config file')
        json.dump(config, f, indent=4)
        logger.debug('Overwrote a config file')


def __create_config(config_file):
    try:
        logger.info('Could not find config so start creating')
        with open(config_file, 'w') as f:
            root = {
                'server': '',
                'token': 'dummy',
                'timeout': 30,
            }
            json.dump(root, f, indent=4)
        logger.info('created a new {config} file.')
        sys.exit(0)
    except IOError as e:
        logger.error('Could not create a config file: ¥n{e}'.format(e=e))
        sys.exit(255)
