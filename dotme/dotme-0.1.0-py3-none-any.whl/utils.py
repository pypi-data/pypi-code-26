import os
import socket
import getpass
from datetime import datetime
from enum import Enum

PROFILE_NAME = 'dotme.yml'
GENERIC_DIR = 'generic'
RC_FILE = '.dotmerc'
FORCE = False
OPTIONS = {
    'copy': False,
    'before': '',
    'after': '',
}

RC_CONFIG = {
    'default': {
        'base': os.path.join('~', RC_FILE),
        'hostname': socket.gethostname(),
        'username': getpass.getuser(),
    }
}

CONFIG_YML = """# This is a example configuration.
#bundles:
#  vim:
#    desc: BASH configurations
#    generic: false
#    links:
#      - from: vimrc
#        to: ~/.vimrc
#      - fromto: [vim, ~/.vim]
#        copy: false
#        before: [echo, 'Hello, there.']
#
#default:
#  copy:
#  before:
#  after:
"""


class Status(Enum):
    Empty = ' EMPTY '
    Symlink = 'SYMLINK'
    File = ' FILE  '
    Dir = '  DIR  '


class Connection(Enum):
    Ok = '  OK   '
    Broken = 'BROKEN '
    Unknown = 'UNKNOWN'


class BackupSuffix:
    def __init__(self):
        time = datetime.now().strftime('%b-%d-%y-%H-%M-%S')
        self.value = '.bak-' + time
