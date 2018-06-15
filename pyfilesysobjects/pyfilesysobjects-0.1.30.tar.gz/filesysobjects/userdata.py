# -*- coding: utf-8 -*-
"""The filesysobjects.userdata module provides information on user data locations.
"""
from __future__ import absolute_import
from __future__ import print_function

import os
from pysourceinfo.fileinfo import getcaller_package_filename

from filesysobjects import FileSysObjectsError
from filesysobjects import V3K, RTE, RTE_BSD, RTE_CYGWIN, RTE_DARWIN, RTE_LINUX, \
    RTE_WIN32

# Seems to require init on Windows before import/call of pysource.
if RTE & RTE_WIN32:
    # Missing that API call, use following dummy for now.
    import inspect
    __dummy4Init = inspect.stack()
    # pylint: disable-msg=F0401
    if V3K:
        import winreg  # @UnresolvedImport @UnusedImport
        import win32.win32security as win32security  # @UnresolvedImport @UnusedImport
        import win32.win32api as win32api  # @UnresolvedImport @UnusedImport

    else:
        import _winreg as winreg  # @UnresolvedImport @UnusedImport @Reimport
        import win32api  # @UnresolvedImport @Reimport
        import win32security  # @UnresolvedImport @Reimport
    # pylint: enable-msg=F0401
else:
    # pylint: disable-msg=F0401
    import pwd  # @UnresolvedImport
    # pylint: enable-msg=F0401

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez" \
                "@Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.20'
__uuid__ = "4135ab0f-fbb8-45a2-a6b1-80d96c164b72"

__docformat__ = "restructuredtext en"


class UserdataException(FileSysObjectsError):
    pass


def gethome():
    """Gets home directory with complete local file path name, eventually drive.
    """
    if RTE & RTE_WIN32:
        return os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    elif RTE & (RTE_BSD | RTE_CYGWIN | RTE_DARWIN | RTE_LINUX):
        return os.environ['HOME']
    else:  # eventually may not yet work if not unix
        return os.environ['HOME']


def getcurrent_username():
    """Gets current user name.
    """
    if RTE & RTE_WIN32:
        return win32api.GetUserName()
    elif RTE & (RTE_BSD | RTE_CYGWIN | RTE_DARWIN | RTE_LINUX):
        return pwd.getpwuid(os.getuid())[0]
    else:
        return os.environ['HOME']


def getdir_userhome(user=''):
    """Gets HOME directory of user, default current user.
    """
    if RTE & RTE_WIN32:
        if not user:
            user = getcurrent_username()
        sid = win32security.ConvertSidToStringSid(
            win32security.LookupAccountName(None, user)[0])

        key = winreg.OpenKey(  # @UndefinedVariable
            winreg.HKEY_LOCAL_MACHINE,  # @UndefinedVariable
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList" + "\\"
            + sid)
        value = winreg.QueryValueEx(  # @UndefinedVariable
            key, "ProfileImagePath")[0]
        return value
    elif RTE & (RTE_BSD | RTE_CYGWIN | RTE_LINUX):
        return os.path.expanduser('~' + user)
    elif RTE & RTE_DARWIN:
        return os.environ['HOME']
    else:  # eventually may not yet work if not unix
        return os.environ['HOME']


def getdir_userdata(user=None):
    """Gets data directory with complete local file path name, eventually drive.
    """
    if RTE & (RTE_WIN32 | RTE_CYGWIN):
        return os.environ['LOCALAPPDATA']
    elif RTE & RTE_LINUX:
        return os.environ['HOME']
    elif RTE & RTE_DARWIN:
        return os.environ['HOME']
    else:  # eventually may not yet work if not unix
        return os.environ['HOME']


def getdir_userconfigdata(user=None):
    """Gets configuration data directory for configuration.

    Args:
        **user**:
            The user name, default is current.

    Returns:
        The user configuration directory of current platform.

    Raises:
        pass-through
    """
    if RTE & (RTE_WIN32 | RTE_CYGWIN):
        # LOCALAPPDATA=C:\Users\acue\AppData\Local
        return os.environ['LOCALAPPDATA']
    elif RTE & RTE_LINUX:
        return os.environ['HOME'] + os.sep + '.config'
    elif RTE & RTE_DARWIN:
        return os.environ['HOME']
    else:  # eventually may not yet work if not unix
        return os.environ['HOME']


def getdir_userappconfigdata(appname='', user=None):
    """Gets configuration directory for applications.

    Args:
        **appname**:
            The application name, for default see: ::

               pysourceinfo.fileinfo.getcaller_package_filename()

        **user**:
            The user name, default is current.

    Returns:
        The user configuration directory of current platform.

    Raises:
        pass-through

    """
    if not appname:
        appname = getcaller_package_filename(3)

    if RTE & (RTE_WIN32 | RTE_CYGWIN):
        # APPDATA=C:\Users\acue\AppData\Roaming
        return os.environ['APPDATA'] + os.sep + appname
    elif RTE & RTE_LINUX:
        return os.environ['HOME'] + os.sep + '.local/share/' + appname
    elif RTE & RTE_DARWIN:
        return os.environ['HOME'] + os.sep + appname
    else:  # eventually may not yet work if not unix
        return os.environ['HOME'] + os.sep + '.' + appname

def getdir_userappdata(appname='', user=None):
    """Gets data directory for applications.

    Args:
        **appname**:
            The application name, for default see: ::

               pysourceinfo.fileinfo.getcaller_package_filename()

        **user**:
            The user name, default is current.

    Returns:
        The user configuration directory of current platform.

    Raises:
        pass-through
    """
    if not appname:
        appname = getcaller_package_filename(3)

    if RTE & (RTE_WIN32 | RTE_CYGWIN):
        # APPDATA=C:\Users\acue\AppData\Roaming
        return os.environ['APPDATA'] + os.sep + appname
    elif RTE & RTE_LINUX:
        return os.environ['HOME'] + os.sep + '.local/share/' + appname
    elif RTE & RTE_DARWIN:
        return os.environ['HOME'] + os.sep + appname
    else:  # eventually may not yet work if not unix
        return os.environ['HOME'] + os.sep + '.' + appname

