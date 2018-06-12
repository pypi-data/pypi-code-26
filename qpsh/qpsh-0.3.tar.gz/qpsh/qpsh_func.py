# coding: utf-8

import os
import sys
import re
import subprocess
from .find_exe import find_exe


class Command:
    def __init__(self, command):
        self.command = command

    def __repr__(self):
        qpsh(self.command)
        return ''

    def __call__(self, arg='', get_return=False):
        return qpsh('{} {}'.format(self.command, arg), get_return)


def qpsh(command, get_return=False):
    if get_return:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        decode = lambda x: x.decode('utf8')
        return decode(result.stdout), decode(result.stderr)

    if line_break:
        print('\n')
    subprocess.run(command, shell=True)
    if line_break:
        print('\n')

if 'bpython' in sys.modules:
    line_break = True
else:
    line_break = False

for command in find_exe():
    try:
        exec('{command} = Command("{command}")'.format(command=command))
    except:
        print(command)
        print(sys.exc_info())
        sys.exit()

from .cd import cd


shell = os.getenv('SHELL')
if not shell:
    if os.path.exists('/bin/bash'):
        shell = '/bin/bash'
    else:
        alias = qpsh('doskey /macros', True)[0].replace('\r', '')
        alias = re.sub('=[- /0-9a-zA-Z]+', lambda x: '="{}"'.format(x.group()[1:]), alias)
if shell:
    alias = subprocess.run([os.getenv('SHELL', '/bin/bash'), '-ic', 'alias'], stdout=subprocess.PIPE).stdout.decode('utf8')

for each_alias in alias.split('\n'):
    each_alias = re.search('[0-9a-zA-Z]+=[\'\"][- /0-9a-zA-Z]+[\'\"]', each_alias)
    if each_alias is not None:
        exec('{} = Command({})'.format(*each_alias.group().split('=')))

if 'ls' not in globals():
    ls = Command('dir')
