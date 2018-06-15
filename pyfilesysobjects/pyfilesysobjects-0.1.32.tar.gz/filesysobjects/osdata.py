# -*- coding: utf-8 -*-
"""The filesysobjects.osdata module provides information on OS data locations.
"""
from __future__ import absolute_import
from __future__ import print_function

import os
from pysourceinfo.fileinfo import getcaller_package_filename

from filesysobjects import FileSysObjectsError
from filesysobjects import RTE, RTE_CYGWIN, RTE_DARWIN, RTE_LINUX, \
    RTE_WIN32

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez" \
                "@Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.20'
__uuid__ = "4135ab0f-fbb8-45a2-a6b1-80d96c164b72"

__docformat__ = "restructuredtext en"


class OsDataError(FileSysObjectsError):
    pass


def getdir_osconfigdata():
    """Gets data directory for configuration.
    """
    if RTE & (RTE_WIN32 | RTE_CYGWIN):
        # ALLUSERSPROFILE=C:\ProgramData
        return os.environ['ALLUSERSPROFILE']
    elif RTE & RTE_LINUX:
        return '/etc'
    elif RTE & RTE_DARWIN:
        return '/etc'
    else:  # eventually may not yet work if not unix
        return '/etc'


def getdir_osappconfigdata(appname=''):
    """Gets configuration directory for applications.
    """
    if not appname:
        appname = getcaller_package_filename(3)

    if RTE & (RTE_WIN32 | RTE_CYGWIN):
        # CommonProgramFiles=C:\Program Files\Common Files
        # CommonProgramFiles(x86)=C:\Program Files (x86)\Common Files
        # CommonProgramW6432=C:\Program Files\Common Files
        return os.environ['CommonProgramFiles'] + os.sep + appname
    elif RTE & RTE_LINUX:
        return '/etc/' + appname
    elif RTE & RTE_DARWIN:
        return '/etc/' + appname
    else:  # eventually may not yet work if not unix
        return '/etc/' + appname


def getdir_osappdata(appname=''):
    """Gets data directory for applications.
    """
    if not appname:
        appname = getcaller_package_filename(3)

    if RTE & (RTE_WIN32 | RTE_CYGWIN):
        # CommonProgramFiles=C:\Program Files\Common Files
        # CommonProgramFiles(x86)=C:\Program Files (x86)\Common Files
        # CommonProgramW6432=C:\Program Files\Common Files
        return os.environ['CommonProgramFiles'] + os.sep + appname
    elif RTE & RTE_LINUX:
        return '/etc/' + appname
    elif RTE & RTE_DARWIN:
        return '/etc/' + appname
    else:  # eventually may not yet work if not unix
        return '/etc/' + appname

def getdir_ospath():
    """Gets standard data directories for executables.
    """
    if RTE & (RTE_WIN32 | RTE_CYGWIN):
        # CommonProgramFiles=C:\Program Files\Common Files
        # CommonProgramFiles(x86)=C:\Program Files (x86)\Common Files
        # CommonProgramW6432=C:\Program Files\Common Files
        return os.environ['CommonProgramFiles']
    elif RTE & RTE_LINUX:
        return '/etc'
    elif RTE & RTE_DARWIN:
        return '/etc'
    else:  # eventually may not yet work if not unix
        return '/etc'
