#
# Copyright 2018 Eduardo A. Paris Penas <edward2a@gmail.com>
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
#


import argparse
import logging
import os
import re
import yaml


logger = logging.getLogger(__name__)


def load_args():
    """Parse command line arguments and return namespace object."""
    p = argparse.ArgumentParser()
    p.add_argument('-c', '--config', default='../confi/config.yml', required=False)
    return p.parse_args()


def load_config(cfg_file):
    """Load configuration from file in YAML format and return dict."""
    with open(cfg_file) as f:
        return yaml.load(f)


def load_env(cfg_obj, inner=False):
    """Parse cfg_obj for env: strings and load them from process env."""

    e = 0

    # Regex matchers
    # env_var_id = re.compile('env:[a-z]+?:')
    bool_false = re.compile('^([Nn0]o?|[Ff]alse)$')
    bool_true = re.compile('^([yY1](es)?|[Tt]rue)$')
    # number_regex = re.compile('env:(int|float):')

    for key, value in cfg_obj.items():

        if isinstance(value, dict):
            e+=load_env(value, True)

        elif isinstance(value, str) and value.startswith('env:'):

            try:

                # Handle undefined variables
                #
                # This is for documentation purposes, not required on python
                # as dict() returns KeyError instead of undefined for missing
                # keys.
                #
                # if not os.environ.get(env_var_id.sub('', value)):
                #     e+=1
                #     raise KeyError('Configuration missing in process environment: ' +
                #         env_var_id.sub('', value))

                # String handler
                if value.startswith('env:str:'):
                    cfg_obj[key] = os.environ[value.lstrip('env:str:')]

                # List (array) handler
                elif value.startswith('env:list:'):
                    cfg_obj[key] = os.environ[value.lstrip('env:list:')].split(',')

                # Bool handler
                elif value.startswith('env:bool:'):
                    #cfg_obj[key] = bool(os.environ[value.lstrip('env:bool:')])
                    bool_env = os.environ[value.lstrip('env:bool:')]

                    if bool_false.match(bool_env):
                        cfg_obj[key] = False

                    elif bool_true.match(bool_env):
                        cfg_obj[key] = True

                    else:
                        raise ValueError('Value of environment variable {} is not supported as boolean'.format(bool_env))

                # Int handler
                elif value.startswith('env:int:'):
                    cfg_obj[key] = int(os.environ[value.lstrip('env:int:')])

                # Float handler
                elif value.startswith('env:float:'):
                    cfg_obj[key] = float(os.environ[value.lstrip('env:float:')])

            # Handle missing variables
            except KeyError:
                e+=1
                logger.error('Configuration missing in process environment: ' + value)
                continue

            except ValueError as e:
                e+=1
                logger.error(e)
                continue

    if inner:
        return e
    if e > 0:
        exit(1)
