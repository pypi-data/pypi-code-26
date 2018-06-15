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


#
# current platform as bit-array
#

# bit-blocks
RTE_UNC = 256  #: UNC [MS-DTYP]_
RTE_CYGWIN = 512  #: Cygwin [CYGWIN]_
RTE_WIN32 = 1024  #: all Windows systems [MS-DTYP]_
RTE_CNW = 1024  #: cross native all Windows systems [MS-DTYP]_
RTE_POSIX = 2048  #: Posix systems using *fcntl* [POSIX]_.
RTE_CNP = 2048  #: cross native Posix systems using *fcntl* [POSIX]_.
RTE_URI = 4096  #: URI - [RFC3986]_

RTE_GENERIC = 8192  #: Undefined platform for special cases
RTE_LOCAL = 8192  #: local - generic

# posix
RTE_LINUX = RTE_POSIX + 1  #: Linux with specific add-ons - OS, DIST, GNU - as Posix system [POSIX]_.
RTE_BSD = RTE_POSIX + 2  #: BSD, - OpenBSD, FreeBSD, NetBSD - as Posix system [POSIX]_.
RTE_DARWIN = RTE_POSIX + 4  #: Darwin/OS-X, as Posix system [POSIX]_, no macpath-legacy.
RTE_OSX = RTE_POSIX + 8  #: Darwin/OS-X, as Posix system [POSIX]_, no macpath-legacy.
RTE_SOLARIS = RTE_POSIX + 32  #: UNIX/Solaris, as Posix system [POSIX]_.

# uri
RTE_FILEURI = RTE_URI + 1  #: file-URI [RFC8089]_
RTE_FILEURI0 = RTE_URI + 2  #: file-URI [RFC8089]_ Appendix A+B+D+E
RTE_FILEURI4 = RTE_URI + 3  #: file-URI [RFC8089]_ Appendix A+B+D+E
RTE_FILEURI5 = RTE_URI + 4  #: file-URI [RFC8089]_ Appendix A+B+D+E

RTE_SMB = RTE_URI + 10  #: SMB [SMBCIFS]_
RTE_HTTP = RTE_URI + 11  #: see [RFC3986]_
RTE_HTTPS = RTE_URI + 12  #: see [RFC3986]_
RTE_LDAP = RTE_URI + 13  #: see [RFC2255]_
RTE_SNMP = RTE_URI + 14  #: see [RFC4088]_
RTE_NFS = RTE_URI + 15  #: see [RFC2224]_
RTE_FTP = RTE_URI + 16  #: see [RFC1738]_
RTE_TFTP = RTE_URI + 17  #: see [RFC3617]_
RTE_PKCS11 = RTE_URI + 18  #: see [RFC7512]_
RTE_SSH = RTE_URI + 19  #: see [RFCSSHURI]_
RTE_VNC = RTE_URI + 20  #: see [RFC7869]_
RTE_GIT = RTE_URI + 21  #: see [RFC]_
RTE_XMPP = RTE_URI + 22  #: see [RFC5122]_
RTE_RSYNC = RTE_URI + 22  #: see [RFC5781]_

RTE = RTE_POSIX  #: current runtime-environment

rte2num = {
    'bsd': RTE_BSD,
    'cygwin': RTE_CYGWIN,
    'fileuri': RTE_FILEURI,
    'fileuri0': RTE_FILEURI0,
    'fileuri4': RTE_FILEURI4,
    'fileuri5': RTE_FILEURI5,
    'ftp': RTE_FTP,
    'git': RTE_GIT,
    'http': RTE_HTTP,  # TODO: replace by RTE_URI virtual platform bit
    'https': RTE_HTTPS,  # TODO: replace by RTE_URI virtual platform bit
    'ldap': RTE_LDAP,
    'linux': RTE_LINUX,
    'nfs': RTE_NFS,
    'pkcs11': RTE_PKCS11,
    'posix': RTE_POSIX,
    'rsync': RTE_RSYNC,
    'smb': RTE_SMB,
    'snmp': RTE_SNMP,
    'solaris': RTE_SOLARIS,
    'ssh': RTE_SSH,
    'tftp': RTE_TFTP,
    'unc': RTE_UNC,
    'uri': RTE_URI,  # TODO: replace by RTE_URI virtual platform bit
    'vnc': RTE_VNC,
    'win': RTE_WIN32,
    'win32': RTE_WIN32,
    'xmpp': RTE_XMPP,
    RTE_BSD: RTE_BSD,
    RTE_CYGWIN: RTE_CYGWIN,
    RTE_FILEURI0: RTE_FILEURI0,
    RTE_FILEURI4: RTE_FILEURI4,
    RTE_FILEURI5: RTE_FILEURI5,
    RTE_FILEURI: RTE_FILEURI,
    RTE_FTP: RTE_FTP,
    RTE_GENERIC: RTE_GENERIC,
    RTE_GIT: RTE_GIT,
    RTE_HTTP: RTE_HTTP,
    RTE_HTTPS: RTE_HTTPS,
    RTE_LDAP: RTE_LDAP,
    RTE_LINUX: RTE_LINUX,
    RTE_NFS: RTE_NFS,
    RTE_PKCS11: RTE_PKCS11,
    RTE_POSIX: RTE_POSIX,
    RTE_RSYNC: RTE_RSYNC,
    RTE_SMB: RTE_SMB,
    RTE_SNMP: RTE_SNMP,
    RTE_SOLARIS: RTE_SOLARIS,
    RTE_SSH: RTE_SSH,
    RTE_TFTP: RTE_TFTP,
    RTE_UNC: RTE_UNC,
    RTE_URI: RTE_URI,
    RTE_VNC: RTE_VNC,
    RTE_WIN32: RTE_WIN32,
    RTE_XMPP: RTE_XMPP,

    # unidirectional
    RTE_DARWIN: RTE_DARWIN,
    RTE_OSX: RTE_OSX,
    RTE_WIN32: RTE_WIN32,
    RTE_GENERIC: RTE_GENERIC,

# TODO:
    RTE_LOCAL: RTE,
    RTE_CNW: RTE_WIN32,
    RTE_CNP: RTE_POSIX,
}

num2rte = {
    RTE_BSD: 'bsd',
    RTE_CYGWIN: 'cygwin',
    RTE_FILEURI0: 'fileuri0',
    RTE_FILEURI4: 'fileuri4',
    RTE_FILEURI5: 'fileuri5',
    RTE_FILEURI: 'fileuri',
    RTE_FTP: 'ftp',
    RTE_GIT: 'git',
    RTE_HTTP: 'http',
    RTE_HTTPS: 'https',
    RTE_LDAP: 'ldap',
    RTE_LINUX: 'linux',
    RTE_NFS: 'nfs',
    RTE_PKCS11: 'pkcs11',
    RTE_POSIX: 'posix',
    RTE_RSYNC: 'rsync',
    RTE_RSYNC: 'rsync',
    RTE_SMB: 'smb',
    RTE_SNMP: 'snmp',
    RTE_SOLARIS: 'solaris',
    RTE_SSH: 'ssh',
    RTE_TFTP: 'tftp',
    RTE_UNC: 'unc',
    RTE_URI:  'uri',
    RTE_VNC: 'vnc',
    RTE_WIN32: 'win32',
    RTE_XMPP: 'xmpp',

    # unidirectional
    RTE_DARWIN: 'darwin',
    RTE_OSX: 'osx',
    RTE_GENERIC: 'generic',

    RTE_LOCAL: 'local',
}


if platform in ('linux', 'linux2'):
    RTE = RTE_POSIX | RTE_LINUX

elif platform == 'bsd':
    RTE = RTE_POSIX | RTE_BSD

elif platform == 'darwin':
    RTE = RTE_POSIX | RTE_DARWIN

elif platform == 'cygwin':
    RTE = RTE_POSIX | RTE_WIN32 | RTE_CYGWIN

elif platform == 'win32':
    RTE = RTE_WIN32

else:
    raise FileSysObjectsError("Platform not supported:" + str(platform))


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
OF_LIST_STR = 1
"""List of strings."""

OF_JSON_STR = 2
"""JSON list of strings."""

OF_JSON_TREE = 3
"""JSON structured tree format."""

OF_XML_STR = 4
"""XML list of strings."""

OF_XML_TREE = 5
"""XML structured tree format."""

#
# Control of glob and re application onto wildcards
# could lead to dramatic performance enhancement.
W_LITERAL = 0
W_GLOB = 1
W_RE = 2
W_FULL = 16
# pylint: enable-msg=W0105


#               sep      pathsep      pf        rte-bits
rte_cnp =      ('/',     ':',         'cnp',    RTE_POSIX)  #: cnp record
rte_cnw =      ('\\',    ';',         'cnw',    RTE_WIN32)  #: cnw record
rte_cygwin =   ('/',     ':',         'cygwin', RTE_CYGWIN | RTE_POSIX)  #: Cygwin record
rte_fileuri =  ('/',     os.pathsep,  'file',   RTE_FILEURI)  #: URI record
rte_fileuri0 = ('/',     os.pathsep,  'file',   RTE_FILEURI0)  #: URI record
rte_fileuri4 = ('/',     os.pathsep,  'file',   RTE_FILEURI4)  #: URI record
rte_fileuri5 = ('/',     os.pathsep,  'file',   RTE_FILEURI5)  #: URI record
rte_local =    (os.sep,  os.pathsep,  'local',  RTE)  #: local record
rte_posix =    ('/',     ':',         'posix',  RTE_POSIX)  #: POSIX record
rte_smb =      ('/',     os.pathsep,  'smb',    RTE_SMB)  #: UNC record
rte_unc =      ('\\',    os.pathsep,  'unc',    RTE_UNC)  #: UNC record
rte_uri =      ('/',     os.pathsep,  'uri',    RTE_URI)  #: URI record
rte_http =     ('/',     os.pathsep,  'http',    RTE_HTTP)  #: URI record
rte_https =    ('/',     os.pathsep,  'https',    RTE_HTTPS)  #: URI record
rte_win32 =    ('\\',    ';',         'win',    RTE_WIN32)  #: WIN32 record

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
    'fileuri': rte_fileuri,
    'fileuri0': rte_fileuri0,
    'fileuri4': rte_fileuri4,
    'fileuri5': rte_fileuri5,
    'ftp': RTE_URI,
    'git':  RTE_URI,
    'http': rte_http,
    'https': rte_https,
    'ldap':  RTE_URI,
    'linux': rte_posix,
    'local': rte_local,
    'nfs':  RTE_URI,
    'pkcs11':  RTE_URI,
    'posix': rte_posix,
    'rsync':  RTE_URI,
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
    RTE_LINUX: rte_posix,
    RTE_LOCAL: rte_local,
    RTE_NFS: RTE_URI,
    RTE_PKCS11: RTE_URI,
    RTE_POSIX: rte_posix,
    RTE_RSYNC: RTE_URI,
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
            predefined := (
                  'bsd' | 'darwin' | 'linux' | 'posix' | 'solaris'
                | 'uri' | 'win'    | 'win32'
            )
            rte := bitmask
            bitmask := (
                  RTE_WIN32  | RTE_POSIX | RTE_LINUX
                | RTE_DARWIN | RTE_OSX   | RTE_BSD
            )

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
            predefined := (
                'bsd' | 'darwin' | 'linux' | 'posix' | 'solaris'
                | 'uri' | 'win' | 'win32'
            )
            bitmask := (
                RTE_BSD | RTE_DARWIN | RTE_LINUX | RTE_POSIX
                | RTE_SOLARIS | RTE_URI | RTE_WIN32
                | RTE_GENERIC | RTE_UNC | RTE_URI | RTE_FILEURI
                | RTE_FILEURI0 | RTE_FILEURI4 | RTE_FILEURI5
                | RTE_SMB | RTE_HTTP | RTE_HTTPS | RTE_LDAP
                | RTE_SNMP | RTE_NFS | RTE_FTP | RTE_TFTP
                | RTE_PKCS11 | RTE_SSH | RTE_VNC | RTE_GIT
                | RTE_XMPP | RTE_RSYNC
            )

    Raises:
        pass-through

    """
    apppre = kw.get('apppre', False)
    pathsep = kw.get('pathsep', '')

    outpf = 0
    if not pf:
        pf = RTE  # RTE_LOCAL  # == RTE

    if type(pf) is int:
        _t = pf
        if _t & RTE_POSIX:
            _t = pf & 255 | RTE_POSIX
        elif _t & RTE_WIN32:
            _t = pf & 255 | RTE_WIN32
        elif _t & RTE_CYGWIN:
            _t = pf & 255 | RTE_CYGWIN

    else:
        _t = re.sub(
            r'.*?(bsd|darwin|linux|solaris|win32|win|posix|cnw|cnp|uri).*',
            r'\1', pf.lower())

    try:
        ret = list(rte_map[_t])
        if type(pf) is int:
            ret[3] |= pf
        ret.append(apppre)

    except:
        raise FileSysObjectsError("Category not supported: tpf=" + str(_t))

    if apppre and ret[3] & RTE_WIN32:
        ret[0] = '/'

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
        raise FileSysObjectsError("target platform not supported: tpf=" + str(_t))

    return tuple(ret)
#    return (sep, psep, tpf, outpf, apppre)



__all__ = [
    "apppaths",
    "configdata",
    "osdata",
    "paths",
    "pathtools",
    "userdata",
]
