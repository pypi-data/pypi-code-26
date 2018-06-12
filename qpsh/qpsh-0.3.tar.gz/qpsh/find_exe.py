# coding: utf-8

import os
import stat
import re
import keyword
import builtins

def find_exe():
    path = os.environ['PATH']
    get_exe_set = lambda slash, split_text: set(sum([[filename.replace('-', '_').replace('.exe', '').replace('.', '_') for filename in os.listdir(path) if os.path.isfile('{}{}{}'.format(path, slash, filename)) and (os.stat('{}{}{}'.format(path, slash, filename)).st_mode & (stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)) and re.fullmatch('[-._a-zA-Z][-._0-9a-zA-Z]*', filename) and filename not in keyword.kwlist + dir(builtins)] for path in os.environ['PATH'].split(split_text) if os.path.exists(path)], []))
    if 'C:\\' in path:
        return get_exe_set('\\', ';')
    return get_exe_set('/', ':')
