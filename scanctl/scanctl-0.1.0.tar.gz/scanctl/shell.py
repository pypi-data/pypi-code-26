# -*- coding: utf-8 -*-

# Copyright 2018 Spotify AB
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

from asyncio.subprocess import PIPE

import asyncio
import logging


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    out, err = await proc.communicate()
    out = out.decode('ascii').rstrip()
    err = err.decode('ascii').rstrip()

    logging.debug(out)
    logging.debug(err)

    if proc.returncode != 0:
        raise Exception(f'command {cmd} returned {proc.returncode}: {err}')

    return out, err
