# -*- coding: utf-8 -*-
"""The package 'filesysobjects' provides utilities for the handling of
file system like resource paths as class trees containing files as objects.

"""
from __future__ import absolute_import
from sys import version_info, platform

import os
import re


__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez" \
                " @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.20'
__uuid__ = "4135ab0f-fbb8-45a2-a6b1-80d96c164b72"

__docformat__ = "restructuredtext en"


class FileSysObjectsError(Exception):
    pass


# pylint: disable-msg=W0105

#
# adjust to current Python version
#
V3K = False  #: Python3.5+
if version_info[:2] > (
        3,
        4, ):
    V3K = True
    ISSTR = (str, bytes)  #: string and unicode
    unicode = str  # @ReservedAssignment
    """Superpose for generic Python3 compatibility."""

elif version_info[:2] > (
        2,
        6, ) and version_info[:2][0] < 3:
    ISSTR = (str, unicode)  #: string and unicode
else:
    raise FileSysObjectsError("Requires Python 2.7+, or 3.5+:" +
                                  str(version_info[:2]))


class AppPathError(FileSysObjectsError):
    """Path error."""
    pass


class PathError(FileSysObjectsError):
    """Path error."""
    pass


class PathToolsError(FileSysObjectsError):
    """Generic exception for module *pathtools*."""
    pass


class PrettyPrintError(FileSysObjectsError):
    """Generic exception for module *pprint*."""
    pass


#
# current platform as bit-array
#

# categories - bit-blocks
RTE_GENERIC = 512  #: Undefined platform for special cases
RTE_UNC = 1024  #: UNC [MS-DTYP]_
RTE_CYGWIN = 2048  #: Cygwin [CYGWIN]_
RTE_WIN32 = 4096  #: all Windows systems [MS-DTYP]_
RTE_POSIX = 8192  #: Posix systems using *fcntl* [POSIX]_.
RTE_URI = 16384  #: URI - [RFC3986]_

# family: generic
RTE_LFSYS = RTE_GENERIC + 1  #: local - generic - maps for file-URI to FILEURI
RTE_LDSYS = RTE_GENERIC + 2  #: local - generic - maps for file-URI to FILEURI
RTE_RFSYS = RTE_GENERIC + 3  #: local - generic - maps for file-URI to FILEURI - absolute-rule
RTE_SHARE = RTE_GENERIC + 4  #: local - generic - maps for file-URI to FILEURI5

RTE_LOCAL = RTE_GENERIC + 5  #: dyanmic local platform
RTE_CNP = RTE_POSIX + 1 #: cross native Posix systems using *fcntl* [POSIX]_.
RTE_CNW = RTE_WIN32 + 1 #: cross native all Windows systems [MS-DTYP]_, slightly different from RTE_WIN32

# family: posix
RTE_DARWIN = RTE_POSIX + 1  #: Darwin/OS-X, as Posix system [POSIX]_, no macpath-legacy.
RTE_OSX = RTE_POSIX + 2  #: Darwin/OS-X, as Posix system [POSIX]_, no macpath-legacy.
RTE_SOLARIS = RTE_POSIX + 16  #: UNIX/Solaris, as Posix system [POSIX]_.
RTE_BSD = RTE_POSIX + 32  #: BSD, - OpenBSD, FreeBSD, NetBSD - as Posix system [POSIX]_.
RTE_LINUX = RTE_POSIX + 64  #: Linux with specific add-ons - OS, DIST, GNU - as Posix system [POSIX]_.

# members" Linux
RTE_CENTOS  = RTE_LINUX + 1  #: CentOS
RTE_CENTOS4 = RTE_LINUX + 2  #: CentOS-4
RTE_CENTOS5 = RTE_LINUX + 3  #: CentOS-5
RTE_CENTOS6 = RTE_LINUX + 4  #: CentOS-6
RTE_CENTOS7 = RTE_LINUX + 5  #: CentOS-7

RTE_FEDORA = RTE_LINUX + 32  #: Fedora
RTE_FEDORA19 = RTE_LINUX + 33  #: Fedora-19
RTE_FEDORA27 = RTE_LINUX + 34  #: Fedora-27

RTE_DEBIAN = RTE_LINUX + 64  #: Debian
RTE_DEBIAN6 = RTE_LINUX + 65  #: Debian - squeeze
RTE_DEBIAN7 = RTE_LINUX + 66  #: Debian - wheezy
RTE_DEBIAN8 = RTE_LINUX + 67  #: Debian - jessy
RTE_DEBIAN9 = RTE_LINUX + 68  #: Debian - stretch

RTE_SUSE = RTE_LINUX + 96  #: OpenSUSE

RTE_UBUNTU = RTE_LINUX + 128  #: OpenSUSE

# family: bsd
RTE_DRAGONFLYBSD = RTE_BSD + 1
RTE_NETBSD = RTE_BSD + 64
RTE_OPENBSD = RTE_BSD + 256
RTE_FREEBSD = RTE_BSD + 512


# family: uri
RTE_FILEURI = RTE_URI + 1  #: file-URI [RFC8089]_
RTE_FILEURI0 = RTE_URI + 2  #: file-URI in minimal representation, see [RFC8089]_ Appendix A+B+D+E
RTE_FILEURI4 = RTE_URI + 3  #: file-URI for UNC in strict 4shlash representation, see [RFC8089]_ Appendix A+B+D+E
RTE_FILEURI5 = RTE_URI + 4  #: file-URI for UNC in common 5slash representation, see [RFC8089]_ Appendix A+B+D+E

RTE_SMB = RTE_URI + 8  #: SMB [SMBCIFS]_
RTE_NFS = RTE_URI + 9  #: see [RFC2224]_
RTE_RSYNC = RTE_URI + 10  #: see [RFC5781]_

RTE_HTTP = RTE_URI + 16  #: see [RFC3986]_
RTE_HTTPS = RTE_URI + 17  #: see [RFC3986]_
RTE_FTP = RTE_URI + 18  #: see [RFC1738]_
RTE_TFTP = RTE_URI + 19  #: see [RFC3617]_

RTE_GIT = RTE_URI + 32  #: see [RFC]_

RTE_LDAP = RTE_URI + 64  #: see [RFC2255]_
RTE_SNMP = RTE_URI + 65  #: see [RFC4088]_

RTE_SSH = RTE_URI + 128  #: see [RFCSSHURI]_
RTE_VNC = RTE_URI + 129  #: see [RFC7869]_

RTE_PKCS11 = RTE_URI + 256  #: see [RFC7512]_
RTE_XMPP = RTE_URI + 257  #: see [RFC5122]_


# family: win32
# currently no sub-categories, some are contained in 
# the 'family: generic': drives, shares
#
RTE_DOS = RTE_WIN32 + 1  #: MS-DOS - frozen
RTE_WINNT4 = RTE_WIN32 + 8  #: Windows-NT4 - frozen
RTE_WINNT4WS = RTE_WIN32 + 9  #: Windows-NT4-Workstation - frozen
RTE_WINNT4S = RTE_WIN32 + 10  #: Windows-NT4-Server - frozen
RTE_WIN2000 = RTE_WIN32 + 16  #: Windows-2000 - frozen
RTE_WINS2000WS = RTE_WIN32 + 17  #: Windows-2000-Workstation - frozen
RTE_WINS2000S = RTE_WIN32 + 18  #: Windows-2000-Server - frozen
RTE_WINS2008 = RTE_WIN32 + 19  #: Windows-2008-Server - frozen

RTE_POWERSHELL1 = RTE_WIN32 + 32  #: PowerShell-1-Windows
RTE_POWERSHELL2 = RTE_WIN32 + 33  #: PowerShell-2-Windows
RTE_POWERSHELL2LINUX = RTE_WIN32 + 64  #: PowerShell-2-Linux

RTE_WIN7 = RTE_WIN32 + 128  #: Windows7
RTE_WIN10 = RTE_WIN32 + 136  #: Windows10
RTE_WINS2012 = RTE_WIN32 + 144  #: Windows-2012-Server


if platform in ('linux', 'linux2'):
    RTE = RTE_LINUX

elif platform == 'bsd':
    RTE = RTE_BSD

elif platform == 'darwin':
    RTE = RTE_DARWIN

elif platform == 'cygwin':
    RTE = RTE_POSIX | RTE_WIN32 | RTE_CYGWIN

elif platform == 'win32':
    RTE = RTE_WIN32

else:
    raise FileSysObjectsError("Platform not supported:" + str(platform))

#RTE_LOCAL = RTE  #: local

rte2num = {
    'bsd': RTE_BSD,
    'centos': RTE_CENTOS,
    'centos4': RTE_CENTOS4,
    'centos5': RTE_CENTOS5,
    'centos6': RTE_CENTOS6,
    'centos7': RTE_CENTOS7,
    'cnp': RTE_CNP,
    'cnw': RTE_CNW,
    'cygwin': RTE_CYGWIN,
    'debian': RTE_DEBIAN,
    'debian6': RTE_DEBIAN6,
    'debian7': RTE_DEBIAN7,
    'debian8': RTE_DEBIAN8,
    'debian9': RTE_DEBIAN9,
    'dos': RTE_DOS,
    'dragonfly': RTE_DRAGONFLYBSD,
    'fedora': RTE_FEDORA,
    'fedora19': RTE_FEDORA19,
    'fedora27': RTE_FEDORA27,
    'file': RTE_FILEURI,
    'fileuri': RTE_FILEURI,
    'fileuri0': RTE_FILEURI0,
    'fileuri4': RTE_FILEURI4,
    'fileuri5': RTE_FILEURI5,
    'freebsd': RTE_FREEBSD,
    'ftp': RTE_FTP,
    'git': RTE_GIT,
    'http': RTE_HTTP,
    'https': RTE_HTTPS,
    'ldap': RTE_LDAP,
    'ldsys': RTE_LDSYS,
    'lfsys': RTE_LFSYS,
    'linux': RTE_LINUX,
    'local': RTE_LOCAL,
    'netbsd': RTE_NETBSD,
    'nfs': RTE_NFS,
    'openbsd': RTE_OPENBSD,
    'pkcs11': RTE_PKCS11,
    'posix': RTE_POSIX,
    'powershell1': RTE_POWERSHELL1,
    'powershell2': RTE_POWERSHELL2,
    'powershell2linux': RTE_POWERSHELL2LINUX,
    'rfsys': RTE_RFSYS,
    'rsync': RTE_RSYNC,
    'share': RTE_SHARE,
    'smb': RTE_SMB,
    'snmp': RTE_SNMP,
    'solaris': RTE_SOLARIS,
    'ssh': RTE_SSH,
    'suse': RTE_SUSE,
    'tftp': RTE_TFTP,
    'ubuntu': RTE_UBUNTU,
    'unc': RTE_UNC,
    'uri': RTE_URI,
    'vnc': RTE_VNC,
    'win': RTE_WIN32,
    'win10': RTE_WIN10,
    'win2000': RTE_WIN2000,
    'win32': RTE_WIN32,
    'win7': RTE_WIN7,
    'winnt2000s': RTE_WINS2000S,
    'winnt2000ws': RTE_WINS2000WS,
    'winnt2008': RTE_WINS2008,
    'winnt2012': RTE_WINS2012,
    'winnt4': RTE_WINNT4,
    'winnt4s': RTE_WINNT4S,
    'winnt4ws': RTE_WINNT4WS,
    'xmpp': RTE_XMPP,
    RTE_BSD: RTE_BSD,
    RTE_CENTOS4: RTE_CENTOS4,
    RTE_CENTOS5: RTE_CENTOS5,
    RTE_CENTOS6: RTE_CENTOS6,
    RTE_CENTOS7: RTE_CENTOS7,
    RTE_CENTOS: RTE_CENTOS,
    RTE_CNP: RTE_POSIX,
    RTE_CNW: RTE_WIN32,
    RTE_CYGWIN: RTE_CYGWIN,
    RTE_DARWIN: RTE_DARWIN,
    RTE_DEBIAN6: RTE_DEBIAN6,
    RTE_DEBIAN7: RTE_DEBIAN7,
    RTE_DEBIAN8: RTE_DEBIAN8,
    RTE_DEBIAN9: RTE_DEBIAN9,
    RTE_DEBIAN: RTE_DEBIAN,
    RTE_DOS: RTE_DOS,
    RTE_DRAGONFLYBSD: RTE_DRAGONFLYBSD,
    RTE_FEDORA19: RTE_FEDORA19,
    RTE_FEDORA27: RTE_FEDORA27,
    RTE_FEDORA: RTE_FEDORA,
    RTE_FILEURI0: RTE_FILEURI0,
    RTE_FILEURI4: RTE_FILEURI4,
    RTE_FILEURI5: RTE_FILEURI5,
    RTE_FILEURI: RTE_FILEURI,
    RTE_FREEBSD: RTE_FREEBSD,
    RTE_FTP: RTE_FTP,
    RTE_GENERIC: RTE_GENERIC,
    RTE_GENERIC: RTE_GENERIC,
    RTE_GIT: RTE_GIT,
    RTE_HTTP: RTE_HTTP,
    RTE_HTTPS: RTE_HTTPS,
    RTE_LDAP: RTE_LDAP,
    RTE_LDSYS: RTE_LDSYS,
    RTE_LFSYS: RTE_LFSYS,
    RTE_LINUX: RTE_LINUX,
    RTE_LOCAL: RTE_LOCAL,
    RTE_NETBSD: RTE_NETBSD,
    RTE_NFS: RTE_NFS,
    RTE_OPENBSD: RTE_OPENBSD,
    RTE_OSX: RTE_OSX,
    RTE_PKCS11: RTE_PKCS11,
    RTE_POSIX: RTE_POSIX,
    RTE_POWERSHELL1: RTE_POWERSHELL1,
    RTE_POWERSHELL2: RTE_POWERSHELL2,
    RTE_POWERSHELL2LINUX: RTE_POWERSHELL2LINUX,
    RTE_RFSYS: RTE_RFSYS,
    RTE_RSYNC: RTE_RSYNC,
    RTE_SHARE: RTE_SHARE,
    RTE_SMB: RTE_SMB,
    RTE_SNMP: RTE_SNMP,
    RTE_SOLARIS: RTE_SOLARIS,
    RTE_SSH: RTE_SSH,
    RTE_SUSE: RTE_SUSE,
    RTE_TFTP: RTE_TFTP,
    RTE_UBUNTU: RTE_UBUNTU,
    RTE_UNC: RTE_UNC,
    RTE_URI: RTE_URI,
    RTE_VNC: RTE_VNC,
    RTE_WIN10: RTE_WIN10,
    RTE_WIN2000: RTE_WIN2000,
    RTE_WIN32: RTE_WIN32,
    RTE_WIN32: RTE_WIN32,
    RTE_WIN7: RTE_WIN7,
    RTE_WINNT4: RTE_WINNT4,
    RTE_WINNT4S: RTE_WINNT4S,
    RTE_WINNT4WS: RTE_WINNT4WS,
    RTE_WINS2000S: RTE_WINS2000S,
    RTE_WINS2000WS: RTE_WINS2000WS,
    RTE_WINS2008: RTE_WINS2008,
    RTE_WINS2012: RTE_WINS2012,
    RTE_XMPP: RTE_XMPP,
}

num2rte = {
    RTE_BSD: 'bsd',
    RTE_CENTOS: 'centos',
    RTE_CENTOS4: 'centos4',
    RTE_CENTOS5: 'centos5',
    RTE_CENTOS6: 'centos6',
    RTE_CENTOS7: 'centos7',
    RTE_CNP: 'cnp',
    RTE_CNW: 'cnw',
    RTE_CYGWIN: 'cygwin',
    RTE_DEBIAN: 'debian',
    RTE_DEBIAN6: 'debian6',
    RTE_DEBIAN7: 'debian7',
    RTE_DEBIAN8: 'debian8',
    RTE_DEBIAN9: 'debian9',
    RTE_DOS: 'dos',
    RTE_DRAGONFLYBSD: 'dragonfly',
    RTE_FEDORA: 'fedora',
    RTE_FEDORA19: 'fedora19',
    RTE_FEDORA27: 'fedora27',
    RTE_FILEURI: 'file',
    RTE_FILEURI: 'fileuri',
    RTE_FILEURI0: 'fileuri0',
    RTE_FILEURI4: 'fileuri4',
    RTE_FILEURI5: 'fileuri5',
    RTE_FREEBSD: 'freebsd',
    RTE_FTP: 'ftp',
    RTE_GIT: 'git',
    RTE_HTTP: 'http',
    RTE_HTTPS: 'https',
    RTE_LDAP: 'ldap',
    RTE_LDSYS: 'ldsys',
    RTE_LFSYS: 'lfsys',
    RTE_LINUX: 'linux',
    RTE_LOCAL: 'local',
    RTE_NETBSD: 'netbsd',
    RTE_NFS: 'nfs',
    RTE_OPENBSD: 'openbsd',
    RTE_PKCS11: 'pkcs11',
    RTE_POSIX: 'posix',
    RTE_POWERSHELL1: 'powershell1',
    RTE_POWERSHELL2: 'powershell2',
    RTE_POWERSHELL2LINUX: 'powershell2linux',
    RTE_RFSYS: 'rfsys',
    RTE_RSYNC: 'rsync',
    RTE_SHARE: 'share',
    RTE_SMB: 'smb',
    RTE_SNMP: 'snmp',
    RTE_SOLARIS: 'solaris',
    RTE_SSH: 'ssh',
    RTE_SUSE: 'suse',
    RTE_TFTP: 'tftp',
    RTE_UBUNTU: 'ubuntu',
    RTE_UNC: 'unc',
    RTE_URI: 'uri',
    RTE_VNC: 'vnc',
    RTE_WIN32: 'win',
    RTE_WIN10: 'win10',
    RTE_WIN2000: 'win2000',
    RTE_WIN32: 'win32',
    RTE_WIN7: 'win7',
    RTE_WINS2000S: 'winnt2000s',
    RTE_WINS2000WS: 'winnt2000ws',
    RTE_WINS2008: 'winnt2008',
    RTE_WINS2012: 'winnt2012',
    RTE_WINNT4: 'winnt4',
    RTE_WINNT4S: 'winnt4s',
    RTE_WINNT4WS: 'winnt4ws',
    RTE_XMPP: 'xmpp',
}


#
# File system node type enums as bit values.
#
T_FILE = 2
"""Files."""

T_DIR = 4
"""Directories."""

T_NODES = 8
"""Files and empty directories. Is superposed by T_FILES and T_DIR."""

T_SYML = 16
"""Symbolic links."""

T_HARDL = 32
"""Hard links."""

T_DEV = 64
"""Devices nodes."""

T_MNT = 128
"""Mount points."""

T_EXP = 256
"""Exported filesystems."""

T_LOCAL = 512
"""Local file system entries only."""

T_ALL = T_FILE | T_DIR | T_NODES | T_SYML
"""All files and empty directories."""

#
# Search directions control parameters for *findpattern()*.
#
L_TDOWN_WALK = 0
"""See os.walk(topdown=True)"""

L_UP_WALK = 1
"""See os.walk(topdown=False)"""

L_UP_EXT = 3
"""Caches M_UP_WALK, and provides same behavior as M_TDOWN_WALK."""

L_MEM_CACHE_ONE = 4
"""Caches one node-level only."""

#
# Bit values for the search proceeding behaviour of *findpattern()*.
#
M_IGNORE = 0
"""Filters and parameters are ignored."""

M_FILTERS = 1
"""Applies to all filters"""

M_PARAMS = 2
"""Applies to all parameters"""

M_FILTPAR = 3
"""Applies all filters and parameters - M_FILTERS | M_PARAMS"""

M_ACCURATE = 4
"""ffs."""

M_FIRST = 8
"""Breaks after first match."""

M_LAST = 16
"""Matches all, but returns the last only."""

M_ALL = 32
"""Returns all matched results."""

M_NEST = 64
"""Clears nested directory path matches."""

M_NOCANON = 128
"""Do not convert input paths to canonical absolute."""

M_REL = 256
"""Keep relative names."""

#
# Output formats for results:
#
OF_LIST_RAW = 1
"""Raw as *DirEntry*."""

OF_LIST_STR = 2
"""List of strings."""

OF_LIST_OID = 3
"""List of dotted object identifier notation."""

OF_JSON_STR = 4
"""JSON list of strings."""

OF_JSON_TREE = 5
"""JSON structured tree format."""

OF_XML_STR = 6
"""XML list of strings."""

OF_XML_TREE = 7
"""XML structured tree format."""


#
# type of quotes
#
Q_SINGLE_TRIPLE = 1  #: triple quotes: '''quoted'''
Q_DOUBLE_TRIPLE = 2  #: double quotes: """quoted"""
Q_ALL_TRIPLE = 3  #: both types: '''quoted''' """quoted"""


#
# Control of glob and re application onto wildcards
# could lead to dramatic performance enhancement.
#
W_LITERAL = 0  #: literally a literal, e.g. no support for quotes
W_LITERAL_QUOTED = 1  #: literal with support for quotes only
W_GLOB = 2  #: support for *glob*
W_RE = 4  #: support for *re*
W_FULL = W_LITERAL_QUOTED|W_GLOB|W_RE  #: support for *re* and *glob*
# pylint: enable-msg=W0105


#               sep      pathsep      pf        rte-bits
rte_cnp =      ('/',     ':',         'cnp',    RTE_CNP)  #: cnp record
rte_cnw =      ('\\',    ';',         'cnw',    RTE_CNW)  #: cnw record
rte_cygwin =   ('/',     ':',         'cygwin', RTE_CYGWIN | RTE_POSIX)  #: Cygwin record
rte_fileuri =  ('/',     os.pathsep,  'file',   RTE_FILEURI)  #: URI record
rte_fileuri0 = ('/',     os.pathsep,  'file',   RTE_FILEURI0)  #: URI record
rte_fileuri4 = ('/',     os.pathsep,  'file',   RTE_FILEURI4)  #: URI record
rte_fileuri5 = ('/',     os.pathsep,  'file',   RTE_FILEURI5)  #: URI record
rte_posix =    ('/',     ':',         'posix',  RTE_POSIX)  #: POSIX record
rte_smb =      ('/',     os.pathsep,  'smb',    RTE_SMB)  #: UNC record
rte_unc =      ('\\',    os.pathsep,  'unc',    RTE_UNC)  #: UNC record
rte_uri =      ('/',     os.pathsep,  'uri',    RTE_URI)  #: URI record
rte_http =     ('/',     os.pathsep,  'http',   RTE_HTTP)  #: URI record
rte_https =    ('/',     os.pathsep,  'https',  RTE_HTTPS)  #: URI record
rte_win32 =    ('\\',    ';',         'win',    RTE_WIN32)  #: WIN32 record


rte_rfsys =    ('/',     os.pathsep,  'rfsys',  RTE_RFSYS)  #: remote filesystem record, either share or netapp
rte_share =    ('\\',    os.pathsep,  'share',  RTE_SHARE)  #: remote filesystem record, either share or netapp

if RTE & RTE_WIN32:
    rte_local =    (os.sep,  os.pathsep,  'win',  RTE_LOCAL)  #: local record
else:
    rte_local =    (os.sep,  os.pathsep,  'posix',  RTE_LOCAL)  #: local record

#: map of target bit-mask to correspoding result record
#: map of target strings to correspoding result record
rte_map = {
    ':': rte_posix,
    ';': rte_win32,
    'bsd': rte_posix,
    'cnp': rte_cnp,
    'cnw': rte_cnw,
    'cygwin': rte_cygwin,
    'darwin': rte_posix,
    'file': rte_fileuri,
    'fileuri': rte_fileuri,
    'fileuri0': rte_fileuri0,
    'fileuri4': rte_fileuri4,
    'fileuri5': rte_fileuri5,
    'ftp': RTE_URI,
    'git':  RTE_URI,
    'http': rte_http,
    'https': rte_https,
    'ldap':  RTE_URI,
    'ldsys': rte_local,
    'lfsys': rte_local,
    'linux': rte_posix,
    'local': rte_local,
    'nfs':  RTE_URI,
    'pkcs11':  RTE_URI,
    'posix': rte_posix,
    'rsync':  RTE_URI,
    'share': rte_share,
    'smb': rte_smb,
    'snmp':  RTE_URI,
    'solaris': rte_posix,
    'ssh':  RTE_URI,
    'tftp':  RTE_URI,
    'unc': rte_unc,
    'uri': rte_uri,
    'vnc':  RTE_URI,
    'win': rte_win32,
    'win32': rte_win32,
    'xmpp':  RTE_URI,
    RTE_BSD: rte_posix,
    RTE_CNP: rte_cnp,
    RTE_CNW: rte_cnw,
    RTE_CYGWIN: rte_cygwin,
    RTE_DARWIN: rte_posix,
    RTE_FILEURI0: rte_fileuri0,
    RTE_FILEURI4: rte_fileuri4,
    RTE_FILEURI5: rte_fileuri5,
    RTE_FILEURI: rte_fileuri,
    RTE_FTP: RTE_URI,
    RTE_GIT: RTE_URI,
    RTE_HTTP: rte_http,
    RTE_HTTPS: rte_https,
    RTE_LDAP: RTE_URI,
    RTE_LDSYS: rte_local,
    RTE_LFSYS: rte_local,
    RTE_LINUX: rte_posix,
    RTE_LOCAL: rte_local,
    RTE_NFS: RTE_URI,
    RTE_PKCS11: RTE_URI,
    RTE_POSIX: rte_posix,
    RTE_RFSYS: rte_rfsys,
    RTE_RSYNC: RTE_URI,
    RTE_SHARE: rte_share,
    RTE_SMB: rte_smb,
    RTE_SNMP: RTE_URI,
    RTE_SOLARIS: rte_posix,
    RTE_SSH: RTE_URI,
    RTE_TFTP: RTE_URI,
    RTE_UNC: rte_unc,
    RTE_URI: rte_uri,
    RTE_VNC: RTE_URI,
    RTE_WIN32: rte_win32,
    RTE_XMPP: RTE_URI,
}


def getspf(pf, **kw):
    """Evaluates the resulting parameters for the source platform.

    See also `tpf and spf <filesysobjects_design.html#tpf-and-spf>`_.

    Args:
        **spf**:
            Source platform, defines the input syntax domain.
            For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

            For additi0onal details refer to
            :ref:`tpf and spf <TPF_AND_SPF>`,
            `paths.getspf() <paths.html#getspf>`_,
            :ref:`normapppathx() <def_normapppathx>`,
            `normpathx() <paths.html#normpathx>`_.

    Returns:
        The path syntax parameters for the target platform: ::

            return (sep, pathsep, spf, rte)

            sep := [/\\\\]
            pathsep := [:;]
            spf := string-representation
            string-representation := predefined | custom
            predefined := ( <rte_map.keys()> )
            rte := bitmask
            bitmask := ( <RTE_*> )

    Raises:
        pass-through

    """
    return gettpf(pf, **kw)[:-1]

def gettpf(pf, **kw):
    """Evaluates the resulting parameters for the target platform.

    See also `tpf and spf <filesysobjects_design.html#tpf-and-spf>`_.

    Args:
        **pf**:
            Target platform for the file pathname. Supports multiple
            entries, where the first has precedence.

            For details refer to 'normpathx] <#normpathx>`_.

        kw:
            apppre:
                Application prefix. ::

                    apppre = (True|False)

                default := False

            pathsep:
                Prepends to the path separator set by the *spf*, thus has
                precedence over the standard separator of the source platform.
                The resulting first character decides the type of the
                scanner *APPPATHSCANNER*. ::

                    pathsep := (';' | ':')

                default = ''

    Returns:
        The path syntax parameters for the target platform: ::

            return (sep, pathsep, tpf, rte, apppre)

            sep := [/\\\\]
            pathsep := [:;]
            tpf := string-representation
            rte := bitmask
            apppre := (True | False)

            string-representation := predefined | custom
            predefined := ( <rte_map.keys()> )
            bitmask := ( <RTE_*> )

    Raises:
        pass-through

    """
    apppre = kw.get('apppre', False)
    pathsep = kw.get('pathsep', '')

    outpf = 0
    if not pf:
        pf = RTE  # RTE_LOCAL  # == RTE
    _t = pf
    if type(pf) is int:
        _t = pf
        if pf in rte_map.keys():
            _t = pf

    else:
        if pf.lower() in rte_map.keys():
            _t = pf.lower()

    try:
        if apppre:
            # app prefix, special for remote files systems
            if _t == 'share':
                ret = list(rte_map[RTE_FILEURI5])
            elif _t == 'rfsys':
                ret = list(rte_map[RTE_FILEURI])
            elif apppre and _t in ('lfsys', 'ldsys'):
                ret = list(rte_map[RTE_FILEURI])
            else:
                ret = list(rte_map[_t])
        else:
            _r = rte2num[_t]
            if _r == RTE_CNW:
                ret = list(rte_map[RTE_CNW])
            elif _r == RTE_CNP:
                ret = list(rte_map[RTE_CNP])
            elif _r & (RTE_WIN32 | RTE_UNC):
                ret = list(rte_map[RTE_WIN32])
            elif _r & (RTE_POSIX | RTE_CYGWIN):
                ret = list(rte_map[RTE_POSIX])
            elif _r == RTE_LOCAL or _r == RTE_GENERIC:
                ret = list(rte_map[RTE_LOCAL])
            else:
                ret = list(rte_map[_r])

        if type(pf) is int:
            ret[3] |= pf
        ret.append(apppre)

    except:
        raise FileSysObjectsError("Category not supported: tpf=" + str(pf))

    if apppre and ret[3] & RTE_WIN32:
        ret[0] = '/'

    elif ret[3] & RTE_LOCAL:
        if _t in ('lfsys', RTE_LFSYS,):
            ret[3] = RTE_LFSYS
        elif _t in ('ldsys', RTE_LDSYS,):
            ret[3] = RTE_LDSYS
        elif _t in ('share', RTE_SHARE,):
            ret[3] = RTE_SHARE
        elif _t in ('rfsys', RTE_RFSYS,):
            ret[3] = RTE_RFSYS

    elif ret[3] & RTE_URI:
        if RTE & RTE_WIN32:
            psep = ';'
        else:
            psep = ':'

    elif ret[3] & RTE_UNC:
        if RTE & RTE_WIN32:
            psep = ';'
        else:
            psep = ':'
        if apppre:
            sep = '/'

    elif _t == ';':
        ret[3] |= RTE_GENERIC

    elif _t == ':':
        ret[3] |= RTE_GENERIC

    if not ret:
        raise FileSysObjectsError("target platform not supported: tpf=" + str(pf))

    return tuple(ret)


__all__ = [
    "apppaths",
    "configdata",
    "osdata",
    "paths",
    "pathtools",
    "userdata",
]


_debug = 0
_quiet = 1
_verbose = 1
_tracebacklimit = 0
