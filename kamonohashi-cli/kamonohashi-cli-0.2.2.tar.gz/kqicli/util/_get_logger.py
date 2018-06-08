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


from __future__ import print_function, absolute_import, unicode_literals, with_statement

import os
from logging import getLogger, StreamHandler, DEBUG, INFO, Formatter
from logging.handlers import TimedRotatingFileHandler

from kamonohashi.util._file_helper import create_folder

LOG_DIR = os.path.expanduser('~') + '/.kqi/'

create_folder(LOG_DIR)


def get_logger():
    logger = getLogger()

    # def handler of console
    console_formatter = Formatter('[%(levelname)s] %(message)s')
    console_handler = StreamHandler()
    console_handler.setLevel(INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # def handler of file
    file_formatter = Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
    file_handler = TimedRotatingFileHandler(filename=LOG_DIR+'debug.log', when='D', backupCount=10)
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger
