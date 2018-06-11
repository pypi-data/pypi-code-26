# coding: utf-8

import os
import stat
import re
import keyword
import builtins

def find_exe():
    return set(sum([[filename.replace('-', '_').replace('.', '_') for filename in os.listdir(path) if os.path.isfile('{}/{}'.format(path, filename)) and (os.stat('{}/{}'.format(path, filename)).st_mode & (stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)) and re.fullmatch('[-_a-zA-Z][-_0-9a-zA-Z]*', filename) and filename not in keyword.kwlist + dir(builtins)] for path in os.environ['PATH'].split(':')], []))
