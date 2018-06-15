# -*- coding: utf-8 -*-
"""The 'filesysobjects.paths' module provides operations on static file
resource paths.
"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sre_constants
import re
import posixpath
import ntpath

from filesysobjects import PathError, \
    ISSTR, \
    gettpf, getspf, \
    rte2num, rte_map, \
    V3K, RTE, RTE_POSIX, RTE_WIN32, FileSysObjectsError, \
    RTE_LOCAL, RTE_CNP, RTE_CNW, \
    RTE_FILEURI0, RTE_FILEURI4, RTE_FILEURI5, RTE_FILEURI

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez" \
                "@Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.20'
__uuid__ = "4135ab0f-fbb8-45a2-a6b1-80d96c164b72"

__docformat__ = "restructuredtext en"

#
# for test and development
# _mydebug = False

#*
# *** static compiled strings ***
#*

# pathname seperator
if RTE & RTE_WIN32:
    OSSEP = os.path.sep  #: os separator
    OSSEPCLS = '[\\\\]'  #: character class os separator
    OSSEPCLSN = '[^\\\\]'  #: character class without separator
else:
    OSSEP = os.path.sep  #: os separator
    OSSEPCLS = '[/]'  #: character class os separator
    OSSEPCLSN = '[^/]'  #: character class without separator

rebaseflags = re.X  # @UndefinedVariable
if V3K:
    rebaseflags |= re.ASCII  # @UndefinedVariable

#
# prohibited characters for optional validation - see strict options
#
INVALIDCHARSWIN = re.compile(r'[:<>*?]')  #: windows
INVALIDCHARSPOSIX = re.compile(r'\0')  #: posix
INVALIDCHARS = re.compile(r'[:<>*?\0]')  #: super position of both

#: maps unambiguous escape characters to escape sequences
ESC_CHAR_MAP = {
    '\a': "\\a",
    '\b': "\\b",
    '\f': "\\f",
    '\n': "\\n",
    '\r': "\\r",
    '\t': "\\t",
    '\v': "\\v",
}

#: list of special escape characters
ESC_CHARS = '[\a\b\f\n\r\t\v]'

#: maps escape characters for escape sequences to unescape
UNESC_CHAR_MAP = {
    'a': "\a",
    'b': "\b",
    'f': "\f",
    'n': "\n",
    'r': "\r",
    't': "\t",
    'v': "\v",
}

# pylint: disable-msg=W0105

# [MS-DTYP] - 2.2.57 - UNC definitions
# pchar = %x20-21 / %x23-29 / %x2D-2E / %x30-39 / %x40-5A / %x5E-7B / %x7D-FF
# pchar = r'[\x20-\x21\x23-\x29\x2D-\x2E\x30-\x39\x40-\x5A\x5E-\x7B\x7D-\xFF]'
# pchar="""[^\x00-\x1f\x22\x2a-\x2c\x2f\x3a-\x3f\x5b-\x5d\x7c]"""

#
# *** splits environment variables ***
#
if RTE & RTE_WIN32:
    _ENV_SPLIT = re.compile(r"""
       (
           (([^%]*?)([%][a-zA-Z0-9_]+[%]))           # 2: defined without brace
         | (([^%]*?)([%][a-zA-Z0-9_]+[^%]?))         # 5: ERROR:
         | ((.*)())                                  # 8: any
       )
       """, rebaseflags)
    """Split-out environment variables for substitution."""

    _ENV_SPLITg = [
        2,
        5,
        8,
    ]
    """Entry points into sub strings environment variables and literals."""
else:
    _ENV_SPLIT = re.compile(r"""
       (
           (([^$]*?)([$][{][a-zA-Z0-9_]+[}]))        # 2: defined with brace
         | (([^$]*?)([$][a-zA-Z0-9_]+[;]?))          # 5: defined without brace
         | (([^$]*?)([$][{][a-zA-Z0-9_]+[^}]?))      # 8: ERROR:
         | ((.*)())                                  # 11: any
       )
       """, rebaseflags)
    """Split-out environment variables for substitution."""

    _ENV_SPLITg = [
        2,
        5,
        8,
        11,
    ]
    """Entry points into sub strings environment variables and literals."""

# pylint: enable-msg=W0105
if V3K:
    pathflags = rebaseflags | re.M | re.ASCII  # @UndefinedVariable
else:
    pathflags = rebaseflags | re.M  # @UndefinedVariable

#: First stage regexpr scanner for 'normpathx', also used in 'escapepathx'.
PATHSCANNER = re.compile(r"""
    (["]{3}[\x01-\xFF]*?["]{3})       # 1  quoted string by 3 double quotes(") - similar to Python
    |([']{3}[\x01-\xFF]*?[']{3})      # 2  quoted string by 3 single quotes(') - similar to Python
    |([\a\b\f\n\r\t\v])               # 3  python escape char - without separate backslash
    |(?<=[^\\\\]){0,1}([\\\\][u][0-9]{4})
                                      # 4  unicode-16
    |(?<=[^\\\\]){0,1}([\\\\][U][0-9]{8})
                                      # 5  unicode-32
    |^(file://[/]{0,1}[/\\\\]{2})(?![/\\\\])
                                      # 6  share/netapp - rfc8089, [MS-DTYP]

    |^(file://)(?![/\\\\])            # 7  non-local - rfc8089 / maps to Posix-App
    |^(file:)(?=/[^/\\\\])            # 8  min - rfc8089
    |^(file://)(?=/)                  # 9  absolute path - rfc8089 rfc1738
    |^(file:)(?=[a-zA-Z]:)            # 10 short-form - rfc8089 - DOS drive

    |^(//)(?=[^\\\\/"]+[\\\\/][\x20-\x21\x23-\x29\x2D-\x2E\x30-\x39\x40-\x5A\x5E-\x7B\x7D-\xFF]{1,80}[\\\\/]*)
                                      # 11 portable UNC

    |^(//)(?=[^/\\\\][^/]*/.+)        # 12 pure posix - with the additional constraint first != [/\\]
    |^([\\\\][\\\\])(?=[^\\\\/"]+[\\\\/][\x20-\x21\x23-\x29\x2D-\x2E\x30-\x39\x40-\x5A\x5E-\x7B\x7D-\xFF]{1,80}[\\\\/]*)
                                      # 13 UNC

    |^([a-zA-Z]:)(?=\\a|\\b|\\f|\\n|\\r|\\t|\\v)
                                      # 14 drive following escaped special escape character

    |^([a-zA-Z]:[\\\\]+)(?![\a\b\f\n\r\t\v])
                                      # 15 drive following 1..n * '[\\]'
    |^([a-zA-Z]:[/]+)                 # 16 drive following 1..n * '[/]'
    |^([a-zA-Z]:)                     # 17 drive only, or relative path
    |(?<=[;:])([a-zA-Z]:[\\\\]+)      # 18 drive following 1..n * '[\\]'
    |(?<=[;:])([a-zA-Z]:[/]+)         # 19 drive following 1..n * '[/]'

    |(?<=[;:])([a-zA-Z]:)             # 20 drive only, or relative path
    |(?<=[\\\\])([/]+)                # 21 os. sep - posix pathname separators
    |(/+)(?=/)                        # 22 n * posix dir-separators
    |(/)                              # 23 1 * posix dir-separators
    |(?<=[\\\\/])([.][.][\\\\/])      # 24 'up-dir: /../ '
    |^([.][.][\\\\/]+)                # 25 'up-dir: ^../ '
    |(?<=[\\\\/])([.][.])$            # 26 'up-dir: /..$ '

    |(?<=[/\\\\])([.][/\\\\])         # 27 'null-dir: \.\ /./'
    |^([.][/\\\\]+)                   # 28 'null-dir: .\ ./'
    |(?<=[/\\\\])([.])$               # 29 'null-dir: \. /.'

    |([\\\\][\\\\])                   # 30 bs pairs
    |([\\\\])(?=\n)                   # 31 single bs - escape '\n'
    |([\\\\])(?=\n)                   # 32 single bs - escape '\n'
    |([\\\\])(?![\\\\])               # 33 single bs - non-escape
    |([:]+)                           # 34 posix path-separators
    |([;]+)                           # 35 win path-separators
    |(?<![^\\\\][\\\\])(\[)           # 36 start char class
    |(?<![^\\\\][\\\\])(\])           # 37 end char class
    |(?<![^\\\\][\\\\])(')            # 38 escaped '
    |(?<![^\\\\][\\\\])(")            # 39 escaped "
    |([^\\\\/\a\b\f\n\r\t\v:;"'\[\]]+)# 40
    |([^\\\\/\a\b\f\n\r\t\v:;]+)(?!.*["'\[\]])
                                      # 41
    |(.)                              # 42 # free char
    """, pathflags)

#
# map matches to actual control sequences
#
SC_BSPAIR = 1000  # '\' pair
SC_CIFS = 1010  # cifs:
SC_CRMASK = 1020  # masked '\n'
SC_DOIT = 1030  # out of range
SC_DQUOTED = 1040  # "
SC_DRIVE = 1050  # dos drive letter - or a directory on Posix !!!
SC_DRIVENPSEP = 1060  # dos drive letter following n * posix_sep
SC_DRIVENWSEP = 1070  # dos drive letter following n * win_sep
SC_DUMMY = 1080  # dummy
SC_EACHOF = 1090  # assure for each
SC_ESCCHAR = 1100  # \[abf...]
SC_FABS = 1110  # file:///path - absolute path - rfc8089 rfc1738
SC_FILE = 1120  # file:
SC_FMIN = 1130  # file:/path - min rfc8089 - Appendix B
SC_FNONLOCAL = 1140  # file://host/path  non-local - rfc8089 - Appendix B / maps to Posix-App
SC_FSHORT= 1150  # file:<dos-drive>:path - short-form - rfc8089
SC_FUNC = 1160  # file:///// | file://// - share/netapp - rfc8089 - Appendix E.3.2
SC_HTTP = 1170  # http:
SC_KEEP = 1180  # keep literally
SC_MASKALL = 1190  # keep literally
SC_NULLDIR = 1200  # '\.\' '/./'
SC_PAPP = 1210  # Posix-Net-App
SC_PDOM = 1220  # Posix-Net-App prefix-compliance to SC_WDOM [MS-DTY]
SC_PSEPP = 1230  # ':'
SC_PSEPW = 1240  # ';'
SC_REPLACE = 1250  # replace an equal set of chars e.g. '/' or '\'
SC_SEPP = 1260  # n * Posix path.sep
SC_SEPW = 1270  # 1 * win path.sep
SC_SLASH = 1280  # 1 * '/'
SC_SLASHPREB = 1290  # '\' + '/'
SC_SMB = 1300  # smb:
SC_SQUOTED = 1310  # '
SC_TOEVEN = 1320  # assure count is even
SC_U16 = 1330  # unicode-16
SC_U16R = 1340  # unicode-16 raw
SC_U32 = 1350  # unicode-32
SC_U32R = 1360  # unicode-32 raw
SC_UNC = 1370  # unc:
SC_UPDIR = 1380  # '/../'
SC_WDOM = 1390  # Win-Domain
SC_CHRCLSSTART = 1400
SC_CHRCLSEND = 1410
SC_ANYONECHR = 1420
SC_ESCAPEDSQUOT = 1430
SC_ESCAPEDDQUOT = 1440


#: Context maps of item indexes corresponding to group indexes onto constants.
#: Performance enhancement by padding, in order to avoid hash calculations via a dictionary.
ASCII_SC_CTRL = [
    0,  # all by *re*
    SC_DQUOTED,      # 1  string
    SC_SQUOTED,      # 2  string
    SC_ESCCHAR,      # 3  python escape sequences
    SC_U16,          # 4  unicode-16
    SC_U32,          # 5  unicode-32

    SC_FUNC ,        # 6  file:///// | file://// - share/netapp - rfc8089 - Appendix E.3.2
    SC_FNONLOCAL,    # 7  rfc8089 - Appendix B
    SC_FMIN,         # 8  rfc8089 - Appendix B
    SC_FABS,         # 9  absolute path- rfc8089, rfc1738
    SC_FSHORT,       # 10 short-form - rfc8089

    SC_PDOM,         # 11  '//' - UNC-Compatible
    SC_PAPP,         # 12 '//' - pure POSIX compliance
    SC_WDOM,         # 13 '\\\\'

    SC_DRIVE,        # 14  DOS drive letter - no following sep

    SC_DRIVENWSEP,   # 15  DOS drive letter with n * win_sep
    SC_DRIVENPSEP,   # 16  DOS drive letter with n * possix_sep

    SC_DRIVE,        # 17  DOS drive letter - no following sep

    SC_DRIVENWSEP,   # 18 DOS drive letter with n * win_sep
    SC_DRIVENPSEP,   # 19 DOS drive letter with n * posix_sep

    SC_DRIVE,        # 20 DOS drive letter - no following sep
    SC_SLASHPREB,    # 21 '\/'
    SC_SEPP,         # 22 n * '/'
    SC_SLASH,        # 23 1 * '/'
    SC_UPDIR,        # 24 'updir/..'
    SC_UPDIR,        # 25 'updir/..'
    SC_UPDIR,        # 26 'updir/..'

    SC_NULLDIR,      # 27 'nulldir/.'
    SC_NULLDIR,      # 28 'nulldir/.'
    SC_NULLDIR,      # 29 'nulldir/.'

    SC_BSPAIR,       # 30 a '\' pair of 1..n
    SC_CRMASK,       # 31 a masked <CR> - r'\\n', else difficult to detect by regexpr
    SC_CRMASK,       # 32 same as SC_CRMASK, but raw - '\\n',
    SC_SEPW,         # 33 '\\',
    SC_PSEPP,        # 34 ':',
    SC_PSEPW,        # 35 ';',
    SC_CHRCLSSTART,  # 36
    SC_CHRCLSEND,    # 37
    SC_ESCAPEDSQUOT, # 38
    SC_ESCAPEDDQUOT, # 39
    SC_DOIT,         # 40
    SC_DOIT,         # 41
    SC_DOIT,         # 42
]
#: Checks for contained dot-directory names in paths, controls parser mode.
_NULLDIRS = re.compile(
    r'.*([/\\\\][.]{1,2}[/\\\\]|[/\\\\][.][.]$|^[.][.][/\\\\])')

_file_uri_scheme = {
    '':  'file',
    '/':  'file',
    '\\':  'file',
    '//':  'netapp',
    '\\\\':  'netapp',
    'fileuri':  'file://',
    'fileuri0': 'file:',
    'fileuri4': 'file:///',
    'fileuri5': 'file:////',
    RTE_FILEURI0: 'file:',
    RTE_FILEURI4: 'file:///',
    RTE_FILEURI5: 'file:////',
    RTE_FILEURI: 'file://',
}
_file_uri_scheme_num = {
    'fileuri':  RTE_FILEURI,
    'fileuri0': RTE_FILEURI0,
    'fileuri4': RTE_FILEURI4,
    'fileuri5': RTE_FILEURI5,
    RTE_FILEURI0: RTE_FILEURI0,
    RTE_FILEURI4: RTE_FILEURI4,
    RTE_FILEURI5: RTE_FILEURI5,
    RTE_FILEURI: RTE_FILEURI,
}

_get_lead_sep = re.compile(r'(/*|[\\\\]*)')


#: short scanner for unescape
PATHSCANNER_UNESC = re.compile(r"""
    (["]{3}[\x01-\xFF]*?["]{3})       #  1  quoted string by 3 double quotes(") - similar to Python
    |([']{3}[\x01-\xFF]*?[']{3})      #  2  quoted string by 3 single quotes(') - similar to Python

    |(?<=[\\\\])([\a\b\f\n\r\t\v])    #  3  python escape char with leading backslash
    |(?<=[^\\\\])([\\u][0-9]{4})      #  4  unicode-16
    |(?<=[^\\\\])([\\U][0-9]{8})      #  5  unicode-32
    |^([\\\\][\\\\])(?=[^\\\\/"]+[\\\\/][\x20-\x21\x23-\x29\x2D-\x2E\x30-\x39\x40-\x5A\x5E-\x7B\x7D-\xFF]{1,80}[\\\\/]*)
                                      #  6 UNC
    |([\\\\][abfnrtv])                #  7  python escaped char with leading backslash
    |([\\\\][\\\\])(?![abfnrtvuU])    #  8 bs pairs - free - not escaping
    |([\\\\][\\\\][abfnrtvuU])        #  9 bs pairs - escaping an escape char
    |([\\\\])(?![\\\\])               # 10 single bs - non-escape
    |([\\\\]['])                      # 11 special escapes - POSIX + Windows
    |([\\\\]["])                      # 12 special escapes - POSIX only (+ URI ?)
    |(?<![^\\\\][\\\\])(\[)           # 13 start char class
    |(?<![^\\\\][\\\\])(\])           # 14 end char class
    |([^\\\\/\a\b\f\n\r\t\v:;"'\[\]]+)# 15
    |([^\\\\/\a\b\f\n\r\t\v:;]+)(?!.*["'\[\]])
                                      # 16
    |(.)                              # 17 # free char
    """, pathflags)

def sub_keep(it, spf=RTE, strip=True, pathsep=''):
    """To be used by re.sub() - keeps mixed.
    """
    g = it.lastindex  # PATHSCANNER ASCII_SC_CTRL
    if it.group(g):
        #        x = it.group(g)
        #         c = ASCII_SC_CTRL[g]
        #         if ASCII_SC_REPLACE_KEEP[g] == SC_KEEP:
        #             pass
        #        return x

        return it.group(g)


_esc_state_shared = []
def sub_esc(it, spf=RTE, strip=False, pathsep='', state=_esc_state_shared,  **kw):
    """To be used by re.sub() - escapes backslashes and non-printable
    characters.

    Args:
        **it**:
            iterator from *re.sub*.

        **spf**:
            Source platform, defines the input syntax domain.
            For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

            For additi0onal details refer to
            :ref:`tpf and spf <TPF_AND_SPF>`,
            `paths.getspf() <paths.html#getspf>`_,
            :ref:`normapppathx() <def_normapppathx>`,
            `normpathx() <paths.html#normpathx>`_.

        **strip**:

        **pathsep**:

        **state**:

        kw:
            **charback**:
                Escapes all backslashes within character classes.
                Could be combined with *force* and *freeback*.

            **force**:
                Escapes all back-slashes, else the special
                characters only. Unix processing of DOS paths
                requires all separators to be escaped.

                default := False

            **freeback**:
                Escapes backslashes outside character classes.
                Could be combined with *charback*.

    Returns:

        Converted format win.
        E.g. ::

           C:\\Windows\\system32\\cmd.exe;C:\\Windows\\system32\\notepad.exe

    Raises:
        pass-through

    """
    try:
        _all = kw['force'] # old - temporary for migration
    except KeyError:
        _all = kw.get('all', False)

    _charback = kw.get('charback', False)
    _freeback = kw.get('freeback', False)

    g = it.lastindex  # PATHSCANNER ASCII_SC_CTRL
    _le = it.end(g)

    if it.group(g):
        x = it.group(g)
        c = ASCII_SC_CTRL[g]

        # FIXME: check for null-dir on 'win'
        if c == SC_BSPAIR:  # pairs of '\\'
            if not state:
                if _all:  # escape anything - blindly
                    return 2 * x
                elif _freeback:  # free standing only
                    return 2 * x
            elif _charback:  # within character classes only
                return 2 * x

        elif c in (SC_CHRCLSSTART, ):  # char class start
            state.append('')

        elif c in (SC_CHRCLSEND, ):  # char class end
            r = ''.join(state) + x
            if V3K:
                state.clear()
            else:
                if state:
                    for i in range(len(state)):
                        state.pop(-1)

            return r

        elif c in (SC_SEPW, ):  # 1 * '\' - win treats '/' equal
#             if _all and not state:  # escape anything - blindly
#                 return 2 * x
            if not state:
                if _all:  # escape anything - blindly
                    return 2 * x
                elif _freeback:  # free standing only
                    return 2 * x
            elif _charback:  # within character classes only
                return 2 * x

        elif c in (SC_WDOM, ):
#             if _all and not state:  # escape anything - blindly
#                 return 2 * x
            if not state:
                if _all:  # escape anything - blindly
                    return 2 * x
                elif _freeback:  # free standing only
                    return 2 * x
            elif _charback:  # within character classes only
                return 2 * x

        elif c == SC_DRIVENWSEP:
            if not state:
                if _all :  # escape anything - blindly
                    return x[:2] + 2 * x[2:]
                if (len(x) - 2) % 2:
                    return x + '\\'

        elif c in (SC_ESCCHAR, ):
            if not state:
                return ESC_CHAR_MAP[x]

        elif c in (SC_CRMASK, ):
            if not state:
                return '\\\\'

        elif c == SC_NULLDIR:
            if not state:
                if g == 27:
                    if x[-1] == '\\':
                        return x + '\\'
                elif g == 28:
                    if x[-1] == '\\':
                        return x + '\\'
                elif g == 29:
                    return x

        return x


_unesc_state_shared = []
def sub_unesc(it, _t=None, spf=None, state=_unesc_state_shared, **kw):
    """To be used by re.sub() - unescapes backslashes and
    non-printable characters.

    Args:
        **it**:
            iterator from *re.sub*.

        **_t**:

        **spf**:
            Source platform, defines the input syntax domain.
            For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

            For additi0onal details refer to
            :ref:`tpf and spf <TPF_AND_SPF>`,
            `paths.getspf() <paths.html#getspf>`_,
            :ref:`normapppathx() <def_normapppathx>`,
            `normpathx() <paths.html#normpathx>`_.

        **state***:

        kw:
            **all** or **force**:
                Unescapes all back/slashes, else the special
                characters only. Unix processing of DOS paths
                requires all separators to be escaped and
                therefore eventually to be unescaped too.

                default := False

    Returns:

        Converted format win.
        E.g.::

           C:\\Windows\\system32\\cmd.exe;C:\\Windows\\system32\\notepad.exe

    Raises:

        pass-through
    """
    try:
        _all = kw['force'] # old - temporary for migration
    except KeyError:
        _all = kw.get('all', False)

    g = it.lastindex  # PATHRULES ASCII_SC_CTRL
    _le = it.end(g)
    if it.group(g):
        x = it.group(g)

        if g == 3:
            if _all:
                return '\\' + x

        elif g == 6:
            if _all:
                return 2 * x

        elif g == 7:  # escaped special char '\\[ab....]'
            return UNESC_CHAR_MAP[x[1]]

        elif g == 8:  # free pairs of '\\' - non/escaping
            if _all:
                return '\\'

        elif g == 9:  # single '\' following escaped char '\[ab....]'
            return x[1:]

        elif g == 11:  # escaped '
            if _all:
                return x[1]

        elif g == 12:  # escaped "
            if _all:
                return x[1]

        elif state:
            if len(x) > 1:
                return state.pop() + x[1:]
            return state.pop()

        return x


def sub_posix(it, spf=RTE, strip=True, pathsep=':', state=None, **kw):
    """To be used by re.sub() - converts to posix.

    Replaces '[/\\]' with '/', and '[;:]' with ':'.

    Posix does not have drives, just ignores the
    drive-property, assumes these are ordinary characters.
    When drives are required as syntax tokens refer to 'Cygwin'.

    Args:
        **it**:
            Iterator from *re.sub*.

        **spf**:
            Source platform, defines the input syntax domain.
            For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

            For additi0onal details refer to
            :ref:`tpf and spf <TPF_AND_SPF>`,
            `paths.getspf() <paths.html#getspf>`_,
            :ref:`normapppathx() <def_normapppathx>`,
            `normpathx() <paths.html#normpathx>`_.


        **strip**:
            Strip redundancies.

        **pathsep**:
            Input separator 'pathsep' to be be
            replaced. ::

               pathsep := ':' ';' ''

            One or more are allowed, is used as a set
            containment of replacement checks. Empty
            string disables the replacement.

        **state**:
            Compile states.

        kw:
           **apppre**:
               Application prefix.

           **keepsep**:
               Keeps seprator, in particular the trailing.

           **stripquote**:
               Strips *filesysobjects* triple-quotes.

    Returns:
        Converted format posix.
        E.g.::

           c:/Windows/system32/cmd.exe:c:/Windows/system32/notepad.exe

    Raises:
        pass-through

    """
    apppre = kw.get('apppre', False)
    keepsep = kw.get('keepsep', False)
    stripquote = kw.get('stripquote', False)

    # tracks multiple path separators, when these are of mixed
    # platforms('/', '\') to be normalized
    if state[0]:
        sx = state[0].pop()
    else:
        sx = 0

    # ignores character classes
    if state[1]:
        inchrclass = True
    else:
        inchrclass = False

    #
    # frequently used values
    #
    g = it.lastindex  # PATHSCANNER ASCII_SC_CTRL
    _le = it.end(g)
    _isfirst = it.start(g) == 0
    _islast = _le == it.endpos
    _charbefore = it.start(g) - 1

    if it.group(g):
        x = it.group(g)
        c = ASCII_SC_CTRL[g]

        if c in (SC_CHRCLSSTART, ):  # char class start
            state[1].append('')

        elif c in (SC_CHRCLSEND, ):  # char class end
            if V3K:
                state[1].clear()
            else:
                if state[1]:
                    for i in range(len(state[1])):
                        state[1].pop(-1)

        elif inchrclass:
            if c in (SC_DQUOTED, SC_SQUOTED):
                if stripquote:
                    return x[3:-3]

        elif c in (SC_DQUOTED, SC_SQUOTED):
            if stripquote:
                return x[3:-3]

        elif c == SC_BSPAIR:  # pairs of '\\'
            if strip:
                if _isfirst:
                    return '/'

                _pre = it.string[_charbefore]
                if _pre in '/\\':  # already done
                    if sx:
                        return '/'
                    return ''
                elif _pre is ':':
                    return '/'
                elif _islast or it.string[_le] is ':':
                    if not keepsep:
                        return ''
                    return '/'
                elif it.string[_le] in '\/':
                    if it.string[_charbefore] is ':':
                        state[0].append(2)
                    else:
                        state[0].append(1)
                    return ''
                return '/'
            else:
                return '//'

        elif c == SC_SLASH:
            if strip:
                if (_isfirst and _islast):
                    return '/'
                elif _islast:
                    if sx == 2:
                        return '/'
                    elif not keepsep:
                        return ''
                elif it.string[_le] is ':':
                    if _isfirst or it.string[_charbefore] is ':':
                        return '/'
                    if not keepsep:
                        return ''

            return '/'

        elif c == SC_SLASHPREB:
            if strip:
                if sx:
                    return '/'
                return ''
            return x

        elif c == SC_SEPP:  # n * '/'
            if strip:
                if _isfirst or it.string[_charbefore] is ':':
                    sx = state[0].append(2)
                return ''

            else:
                return '/' * len(x)

        elif c == SC_SEPW:  # n * '/'

            if _isfirst:  # is app-pre '//'
                return '/'

            if it.string[_charbefore] is ':':
                return '/'

            if strip:
                if _islast or it.string[_le] is ':':
                    if sx == 2:
                        return '/'
                    return ''
                if sx:
                    return '/'

                if it.string[_charbefore] in '/\\':
                    return ''

            else:
                return '/' * len(x)

            if it.endpos > _le:
                if it.string[_le] == '\\':
                    if it.endpos > _le + 1 and it.string[_le + 1] == '\n':
                        pass
                    else:
                        if strip:
                            return ''
                return '/'

        elif c == SC_PSEPP:
            if x[0] not in pathsep:  # 1..n
                return x

            if strip:
                if _islast:  # drop trailing os.pathsep
                    return ''
                return ':'
            else:
                return ':' * len(x)

        elif c == SC_PSEPW:
            # native
            return x

            # mixed
            if x[0] not in pathsep:  # 1..n
                return x

            if spf & RTE_POSIX:  # for posix node names an ordinary character
                return x

            if strip:
                if _islast:  # drop trailing os.pathsep
                    return ''

                if len(it.string) > _le:
                    if it.string[_le] == ':':
                        return ''

                return ':'
            else:
                return ':' * len(x)

        elif c in (SC_FUNC,):  # verified by char contents
            if apppre:
                return 'file://///'
            return '//'

        elif c is SC_UPDIR:
            return '../'

        elif c is SC_FNONLOCAL:  # verified by char contents
            if apppre:
                return 'file://'
            return '//'

        elif c in (SC_FMIN, SC_FABS, SC_FSHORT,):
            if not apppre:
                return ''

        elif c in (SC_WDOM, SC_PDOM, SC_PAPP,):  # verified by char contents
            if strip and it.string[_le] in ':':
                return '/'
            elif strip and _islast:
                return ''
            return '//'

        elif c in (SC_DRIVENPSEP, SC_DRIVENWSEP):  # posix does not have drives
            if strip:  # keep drive-root
                return x[0] + ':/'
            return x[:2] + '/' * (len(x) - 2)

        elif c == SC_DRIVE:
            return x

        elif c == SC_NULLDIR:
            return ''

        elif c == SC_FILE:
            if apppre:
                return x
            return ''

        elif c == SC_UNC:
            if apppre:
                return x
            return '//'

        return x


def sub_uri(it, spf=RTE, strip=True, pathsep='', state=None, **kw):
    """To be used by re.sub() - converts to uri.

    Args:
        **it**:
            Iterator from *re.sub*.

        **spf**:
            Source platform, defines the input syntax domain.
            For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

            For additi0onal details refer to
            :ref:`tpf and spf <TPF_AND_SPF>`,
            `paths.getspf() <paths.html#getspf>`_,
            :ref:`normapppathx() <def_normapppathx>`,
            `normpathx() <paths.html#normpathx>`_.

        **strip**:
            Strip redundancies.

        **pathsep**:
            Input separator 'pathsep' to be be
            replaced. ::

               pathsep := ':' ';' ''

            One or more are allowed, is used as a set
            containment of replacement checks. Empty
            string disables the replacement.

        kw:
           **apppre**:
               Application prefix.

    Returns:
        Converted format uri.
        E.g.::

           http://a/b/c

    Raises:
        pass-through

    """
    apppre = kw.get('apppre', False)

    g = it.lastindex  # PATHRULES ASCII_SC_CTRL
    _le = it.end(g)

    if it.group(g):
        x = it.group(g)
        c = ASCII_SC_CTRL[g]
        if c == SC_BSPAIR:  # pairs of '\\'

            if strip:
                if it.start(g) == 0:
                    #                     if it.string[it.end(g)] in '/\\':
                    #                         return '/'
                    #                     return '//'
                    return '/'

                if it.string[it.start(g) - 1] in '/\\':  # already done
                    return ''
                elif len(it.string) > _le:
                    return '/'
            else:
                return '//'

            if strip:  # want to reduce by look-ahead
                if len(it.string) > _le and it.string[_le] == '\\':
                    # FIXME: a.s.a.p.
                    if it.string.find('\\', _le) < len(it.string) - 1:
                        return ''
                elif len(it.string) > _le and it.string[_le] == '/':
                    # FIXME: a.s.a.p.
                    if it.string.find('/', _le) < len(it.string) - 1:
                        return ''

                return '/'
            else:
                return '//'

        elif c == SC_SLASH:
            return '/'

        elif c == SC_SLASHPREB:
            if strip:
                return ''
            return x

        elif c == SC_SEPP:  # n * '/'
            if strip:
                return ''

            else:
                return '/' * len(x)

        elif c == SC_SEPW:  # n * '/'
            if it.start(g) == 0:  # is app-pre '//'
                if it.start(g) > 1:
                    return '//'
                return '/'
            if strip:
                if it.string[it.start(g) - 1] in '/\\':
                    return ''
                # is app-pre '//'
                elif it.start(g) == 1 and it.string[0] in ('/', '\\'):
                    return ''  # 2SEP has own rules

                if len(it.string) == _le and _le > 1:  # do not '/'
                    return '/'

            if len(it.string) > _le:
                if it.string[_le] == '\\':
                    if len(it.string) > _le + 1 and it.string[_le + 1] == '\n':
                        pass
                    else:
                        if strip:
                            return ''
                return '/'

            if strip:
                return '/'
            else:
                return '/' * len(x)

        elif c == SC_PSEPP:
            if x[0] not in pathsep:  # 1..n
                return x

            if strip:
                if len(it.string) == _le:  # drop trailing os.pathsep
                    return ''

                if len(it.string) > _le:
                    if it.string[_le] == ';':
                        return ''

                return ':'
            else:
                return ':' * len(x)

        elif c == SC_PSEPW:
            if x[0] not in pathsep:  # 1..n
                return x

            if spf & RTE_POSIX:  # for posix node names an ordinary character
                return x

            if strip:
                if len(it.string) == _le:  # do not drop trailing '/'
                    return '/'

                if len(it.string) > _le:
                    if it.string[_le] == ':':
                        return ''

                return ':'
            else:
                return ':' * len(x)

        elif c in (SC_PAPP, SC_WDOM):
            return '//'

        elif c in (SC_DRIVENPSEP, SC_DRIVENWSEP):  # posix does not have drives
            if strip:  # keep drive-root
                return x[0] + ':/'
            return x[:2] + '/' * (len(x) - 2)

        elif c is SC_UPDIR:
            return '../'

        elif c == SC_DRIVE:
            return x

        elif c == SC_NULLDIR:
            return ''

        elif c == SC_FILE:
            if apppre:
                return x
            return ''

        elif c == SC_UNC:
            if apppre:
                return x
            return '//'

        return x


def sub_rfc8089(it, spf=RTE, strip=True, pathsep='', state=None, **kw):
    """To be used by re.sub() - converts to file uri in accordance to RFC8089.
    This is different from most of common URI, e.g. HTTP(S).

    Args:
        **it**:
            Iterator from *re.sub*.

        **spf**:
            Source platform, defines the input syntax domain.
            For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

            For additi0onal details refer to
            :ref:`tpf and spf <TPF_AND_SPF>`,
            `paths.getspf() <paths.html#getspf>`_,
            :ref:`normapppathx() <def_normapppathx>`,
            `normpathx() <paths.html#normpathx>`_.

        **strip**:
            Strip redundancies.

        **pathsep**:
            Input separator 'pathsep' to be be
            replaced. ::

               pathsep := ':' ';' ''

            One or more are allowed, is used as a set
            containment of replacement checks. Empty
            string disables the replacement.

        **state**:
            Compile states.

        kw:
            **apppre**:
                Application prefix.

            **keepsep**:
                Keeps the trailing separator. ::

                   keepsep := (
                         True    # keep trailing sep, indicating a directory
                       | False   # drop trailing sep
                   )

           **stripquote**:
               Strips *filesysobjects* triple-quotes.

    Returns:
        Converted format uri.
        E.g.::

           http://a/b/c

    Raises:
        pass-through

    """
    apppre = kw.get('apppre', False)
    keepsep = kw.get('keepsep', True)
    stripquote = kw.get('stripquote', False)

    # tracks multiple path separators, when these are of mixed
    # platforms('/', '\') to be normalized
    if state[0]:
        sx = state[0].pop()
    else:
        sx = 0

    # ignores character classes
    if state[1]:
        inchrclass = True
    else:
        inchrclass = False

    #
    # frequently used values
    #
    g = it.lastindex  # PATHSCANNER ASCII_SC_CTRL
    _le = it.end(g)
    _isfirst = it.start(g) == 0
    _islast = _le == it.endpos
    _charbefore = it.start(g) - 1

    if it.group(g):
        x = it.group(g)
        c = ASCII_SC_CTRL[g]

        if c in (SC_CHRCLSSTART, ):  # char class start
            state[1].append('')

        elif c in (SC_CHRCLSEND, ):  # char class end
            if V3K:
                state[1].clear()
            else:
                if state[1]:
                    for i in range(len(state[1])):
                        state[1].pop(-1)

        elif inchrclass:
            if c in (SC_DQUOTED, SC_SQUOTED):
                if stripquote:
                    return x[3:-3]

        elif c == SC_BSPAIR:  # pairs of '\\'
            if strip:
                if _isfirst:
                    return '/'

                _pre = it.string[_charbefore]
                if _pre in '/\\':  # already done
                    if sx:
                        return '/'
                    return ''
                elif _pre is ':':
                    return '/'
                elif _islast or it.string[_le] is ':':
                    if not keepsep:
                        return ''
                    return '/'
                elif it.string[_le] in '\/':
                    if it.string[_charbefore] is ':':
                        state[0].append(2)
                    else:
                        state[0].append(1)
                    return ''
                return '/'
            else:
                return '//'

#             if strip:
#                 if it.start(g) == 0:
#                     #                     if it.string[it.end(g)] in '/\\':
#                     #                         return '/'
#                     #                     return '//'
#                     return '/'
#
#                 if it.string[it.start(g) - 1] in '/\\':  # already done
#                     return ''
#                 elif len(it.string) > _le:
#                     return '/'
#             else:
#                 return '//'
#
#             if strip:  # want to reduce by look-ahead
#                 if len(it.string) > _le and it.string[_le] == '\\':
#                     # FIXME: a.s.a.p.
#                     if it.string.find('\\', _le) < len(it.string) - 1:
#                         return ''
#                 elif len(it.string) > _le and it.string[_le] == '/':
#                     # FIXME: a.s.a.p.
#                     if it.string.find('/', _le) < len(it.string) - 1:
#                         return ''
#
#                 return '/'
#             else:
#                 return '//'

        elif c == SC_SLASH:
            if strip:
                if (_isfirst and _islast):
                    return '/'
                elif _islast:
                    if sx == 2:
                        return '/'
                    elif not keepsep:
                        return ''
                elif it.string[_le] is ':':
                    if _isfirst or it.string[_charbefore] is ':':
                        return '/'
                    if not keepsep:
                        return ''

            return '/'

        elif c == SC_SLASHPREB:
            if strip:
                if sx:
                    return '/'
                return ''
            return x
#             if strip:
#                 return ''
#             return x

        elif c == SC_SEPP:  # n * '/'
            if strip:
                if _isfirst or it.string[_charbefore] is ':':
                    sx = state[0].append(2)
                return ''

            else:
                return '/' * len(x)
#             if strip:
#                 return ''
#
#             else:
#                 return '/' * len(x)

        elif c == SC_SEPW:  # n * '/'
            if _isfirst:  # is app-pre '//'
                return '/'

            if it.string[_charbefore] is ':':
                return '/'

            if strip:
                if _islast or it.string[_le] is ':':
                    if sx == 2:
                        return '/'
                    return ''
                if sx:
                    return '/'

                if it.string[_charbefore] in '/\\':
                    return ''

            else:
                return '/' * len(x)

            if it.endpos > _le:
                if it.string[_le] == '\\':
                    if it.endpos > _le + 1 and it.string[_le + 1] == '\n':
                        pass
                    else:
                        if strip:
                            return ''
                return '/'
#             if it.start(g) == 0:  # is app-pre '//'
#                 if it.start(g) > 1:
#                     return '//'
#                 return '/'
#             if strip:
#                 if it.string[it.start(g) - 1] in '/\\':
#                     return ''
#                 # is app-pre '//'
#                 elif it.start(g) == 1 and it.string[0] in ('/', '\\'):
#                     return ''  # 2SEP has own rules
#
#                 if len(it.string) == _le and _le > 1:  # do not '/'
#                     return '/'
#
#             if len(it.string) > _le:
#                 if it.string[_le] == '\\':
#                     if len(it.string) > _le + 1 and it.string[_le + 1] == '\n':
#                         pass
#                     else:
#                         if strip:
#                             return ''
#                 return '/'
#
#             if strip:
#                 return '/'
#             else:
#                 return '/' * len(x)

        elif c == SC_PSEPP:
            if x[0] not in pathsep:  # 1..n
                return x

            if strip:
                if _islast:  # drop trailing os.pathsep
                    return ''
                return ':'
            else:
                return ':' * len(x)
#             if x[0] not in pathsep:  # 1..n
#                 return x
#
#             if strip:
#                 if len(it.string) == _le:  # drop trailing os.pathsep
#                     return ''
#
#                 if len(it.string) > _le:
#                     if it.string[_le] == ';':
#                         return ''
#
#                 return ':'
#             else:
#                 return ':' * len(x)

        elif c == SC_PSEPW:
            # native
#            return x

            # mixed
            if x[0] not in pathsep:  # 1..n
                return x

            if spf & RTE_POSIX:  # for posix node names an ordinary character
                return x

            if strip:
                if _islast:  # drop trailing os.pathsep
                    if keepsep:
                        return x
                    else:
                        return ''

                if len(it.string) > _le:
                    if it.string[_le] == ':':
                        return ''

                return ':'
            else:
                return ':' * len(x)
#             if x[0] not in pathsep:  # 1..n
#                 return x
#
#             if spf & RTE_POSIX:  # for posix node names an ordinary character
#                 return x
#
#             if strip:
#                 if len(it.string) == _le:  # do not drop trailing '/'
#                     return '/'
#
#                 if len(it.string) > _le:
#                     if it.string[_le] == ':':
#                         return ''
#
#                 return ':'
#             else:
#                 return ':' * len(x)

        elif c in (SC_PAPP, SC_WDOM):
            return '//'

        elif c in (SC_DRIVENPSEP, SC_DRIVENWSEP):  # posix does not have drives
            if strip:  # keep drive-root
                return x[0] + ':/'
            return x[:2] + '/' * (len(x) - 2)

        elif c is SC_UPDIR:
            return '../'

        elif c == SC_DRIVE:
            return x

        elif c == SC_NULLDIR:
            return

        elif c == SC_FILE:
            if apppre:
                return x
            return ''

        elif c == SC_UNC:
            if apppre:
                return x
            return '//'

        return x


def sub_win(it, spf=RTE, strip=True, pathsep=';', state=None, **kw):
    """To be used by re.sub() - converts to windows.

    Replaces '[/\\\\]' with '\\\\', and '[;:]' with ';'.

    Args:
        **it**:
            iterator from *re.sub*.

        **spf**:
            Source platform, defines the input syntax domain.
            For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

            For additi0onal details refer to
            :ref:`tpf and spf <TPF_AND_SPF>`,
            `paths.getspf() <paths.html#getspf>`_,
            :ref:`normapppathx() <def_normapppathx>`,
            `normpathx() <paths.html#normpathx>`_.

        **strip**:
            Strip redundancies.

        **pathsep**:
            Input separator 'pathsep' to be be
            replaced. ::

               pathsep := ':' ';' ''

            One or more are allowed, is used as a set
            containment of replacement checks. Empty
            string disables the replacement.

        **state**:
            Compile states.

        kw:
           **apppre**:
               Application prefix.

           **keepsep**:
               Keeps seprator, in particular the trailing.

           **stripquote**:
               Strips *filesysobjects* triple-quotes.

    Returns:
        Converted format win.
        E.g.::

           C:\\Windows\\system32\\cmd.exe;C:\\Windows\\system32\\notepad.exe

    Raises:
        pass-through
    """
    apppre = kw.get('apppre', False)
    keepsep = kw.get('keepsep', False)
    stripquote = kw.get('stripquote', False)

    if apppre:
        # scheme for an URI requested, so slashes only
        sep = '/'
        sep2 = '//'
    else:
        # no scheme, so a UNC
        sep = '\\'
        sep2 = '\\\\'

    # tracks multiple path separators
    if state[0]:
        sx = state[0].pop()
    else:
        sx = 0

    # ignores character classes
    if state[1]:
        inchrclass = True
    else:
        inchrclass = False

    #
    # frequently used values
    #
    g = it.lastindex  # PATHRULES ASCII_SC_CTRL
    _le = it.end(g)
    _isfirst = it.start(g) == 0
    _islast = _le == it.endpos
    _isnotlast = it.endpos > _le
    _charbefore = it.start(g) - 1

    if _isnotlast:
        _nextissep = it.string[_le] in '\\/'
    else:
        _nextispsep = None

    if _isnotlast:
        _nextispsep = it.string[_le] in pathsep
    else:
        _nextispsep = None

    if it.group(g):  # PATHRULES PATHSCANNER ASCII_SC_CTRL
        x = it.group(g)
        c = ASCII_SC_CTRL[g]

        if c in (SC_CHRCLSSTART, ):  # char class start
            state[1].append('')

        elif c in (SC_CHRCLSEND, ):  # char class end
            if V3K:
                state[1].clear()
            else:
                if state[1]:
                    for i in range(len(state[1])):
                        state[1].pop(-1)

        elif inchrclass:
            if c in (SC_DQUOTED, SC_SQUOTED):
                if stripquote:
                    return x[3:-3]

        elif c in (SC_DQUOTED, SC_SQUOTED):
            if stripquote:
                return x[3:-3]

        elif c == SC_BSPAIR:  # pairs of '\\'
            if strip:
                if _isfirst:  # TODO: basically not possible as net-app, see SC_PAP
                    if _isnotlast and _nextissep:
                        state[0].append(2)
                        return ''
                    return sep
                elif _islast:
                    if sx == 2:
                        return sep
                    return ''
                elif _nextispsep:
                    if sx:
                        return sep
                    elif it.string[_charbefore] in pathsep:
                        return sep
                    return ''
                elif _nextissep:
                    if not sx:
                        sx = 1
                    state[0].append(sx)
                    return ''
                return sep

            else:
                return sep2

        elif c in (SC_SLASH, ):  # 1 * '\' - win treats '/' equal
            if strip:
                if sx == 3:
                    return ''

                if _isfirst:
                    if _islast:
                        return sep
                    elif _nextissep:
                        state[0].append(2)
                        return ''

                elif _nextispsep or _islast:
                    if sx == 2:
                        return sep
                    elif it.string[_charbefore] in pathsep:
                        return sep
                    return ''

                elif _isnotlast and _nextissep:
                    state[0].append(1)
                    return ''

                return sep

            return sep

        elif c in (SC_SLASHPREB, ):  # '\/'
            if strip:
                if _islast:
                    if sx == 2:
                        return sep
                    return ''
                elif _nextissep:
                    if not sx:
                        sx = 1
                    state[0].append(sx)
                    return ''
                elif sx == 2:
                    return sep
                return sep
            return sep * len(x)

        elif c in (SC_SEPP, ):  # n * '/'
            if strip:
                if _isfirst:
                    state[0].append(2)
                else:
                    state[0].append(1)
                return ''
            return sep * len(x)

        elif c in (SC_SEPW, ):  # n * '\' - win treats '/' equal
            if not strip:
                return sep * len(x)

            if _isfirst:
                if _isnotlast:
                    if _nextissep:
                        state[0].append(2)
                        return ''
                    if _nextispsep:
                        return sep
                else:
                    return sep

            elif _islast or _nextispsep:
                if sx == 2:
                    return sep
                if it.string[_charbefore] in pathsep:
                    return sep
                return ''

            elif _isnotlast and _nextissep:
                if not sx:
                    sx = 1
                state[0].append(sx)
                return ''

            if sx > 1:
                return sep
            return sep

        elif c == SC_PSEPP:
            # native
            if strip:
                if x[0] in pathsep and _islast:
                    return ''

            return x

        elif c == SC_CRMASK:
            if _isfirst:
                return x

            elif sx:
                return sep + x[1:]

            return x

        elif c in (SC_FUNC,):  # verified by char contents
            if apppre:
                return 'file://///'

            if strip and it.string[_le] in ':':
                return '/'
            elif strip and _islast:
                return ''
            return sep2

        elif c is SC_FABS:

            # lookahead for RFC8089 - appendix E.2.1
            if len(it.string) > _le + 2 and \
                    ord(it.string[_le + 1].upper()) in range(65,91) and \
                    it.string[_le + 2] == ':':
                state[0].append(3)

            if not apppre:
                return ''

        elif c in (SC_FMIN, SC_FSHORT,):
            if not apppre:
                return ''

        elif c == SC_PSEPW:
            if x not in pathsep:  # changed spf/psep
                return x

            if strip:
                _is = it.start(g)
                if not _is or (_is + 1) == it.endpos:
                    return ''

                if x[0] in pathsep and _is > 0 and it.string[_is
                                                          - 1] in pathsep:  # 1..n
                    return ''
                return ';'

            return ';' * len(x)

        elif c is SC_UPDIR:
            return '..\\'

        elif c is SC_FNONLOCAL:
            if not apppre:
                return ''

        elif c is SC_PAPP:
            if strip and _nextispsep:
                return sep
            return sep2


        elif c in (SC_WDOM, SC_PDOM):  # basically sure a UNC or NETAPP
            if strip and _nextispsep:
                return sep
            return sep2

        elif c in (SC_DRIVENWSEP, SC_DRIVENPSEP):
            if strip:  # keep drive-root
                return x[0] + ':' + sep
            return x[:2] + sep * (len(x) - 2)

        elif c == SC_DRIVE:
            return x

        elif c == SC_NULLDIR:
            return ''

        elif c == SC_FILE:
            if apppre:
                return x
            return ''

        elif c == SC_UNC:
            if apppre:
                return x
            return sep2

        return x


sub_path_calls = {  #: 're.sub' callbacks for normalization
    'b': sub_win,
    'cnp': sub_posix,
    'cnw': sub_win,
    'file': sub_rfc8089,
    'http': sub_uri,
    'https': sub_uri,
    'k': sub_keep,
    'keep': sub_keep,
    'posix': sub_posix,
    'rfsys': sub_posix,
    's': sub_posix,
    'share': sub_win,
    'uri': sub_uri,
    'win': sub_win,
    'win32': sub_win,
}


def escapepathx(spath, tpf=None, **kargs):
    """Escape special characters within path names,
    supports cross-platform processing, knows the
    special escape characters of Python and *re*.
    The characters could be masked by quoting, and/or
    enclosing in character classes.

    +----------------+-----------------------+-----------------+
    | input          | -> esc                | -> unesc        |
    +================+=======================+=================+
    |     \\\\abc"\\\\n" |       \\\\\\\\abc"\\\\n"    |     \\\\abc"\\\\n"  |
    +----------------+-----------------------+-----------------+
    |     \\\\"abc\\\\n" |       \\\\\\\\"abc\\\\n"    |     \\\\"abc\\\\n"  |
    +----------------+-----------------------+-----------------+
    |     \\\\abc\\\\n   |         \\\\\\\\abc\\\\\\\\n  |     \\\\abc\\\\n    |
    +----------------+-----------------------+-----------------+
    |   \\\\xy" "z     |     \\\\\\\\xy" "z        |   \\\\xy" "z      |
    +----------------+-----------------------+-----------------+
    |   \\\\"xy z"     |     \\\\\\\\"xy z"        |   \\\\"xy z"      |
    +----------------+-----------------------+-----------------+
    |   \\\\xy z       |       \\\\\\\\xy\\\\ z      |   \\\\xy z        |
    +----------------+-----------------------+-----------------+

    Args:
        **spath**:
            The path to be escaped. ::

               spath := (
                    <path-string>
                  | <path-array>
               )

               path-string := (str | unicode)
               path-array := (list | tuple)

            * *path-string*

              The string representation of a complete path, which may contain literal,
              *glob*, and *re* expressions. The supported character representation
              is *str* or *unicode* for Pyton2.7 and Python3.5+.

            * *path-array*

              The component representation of a path, which consists of it's items,
              either as a *list* or as a *tuple*. Each item may contain literal,
              *glob*, and *re* expressions.


        **tpf**:
            Target path separator, currently not used.

        kargs:

            **charback**:
                Escapes all backslashes within character classes.
                Could be combined with *force* and *freeback*. ::

                   \a\[\\] => \a\[\\\\]

            **force**:
                Controls the escaped scope. Excludes quoted strings and
                character classes. Could be combined with *charback*. ::

                   force = (
                        True    # escape characters and any free backslash
                      | False   # defined escape characters only
                   )

                   force == True

                      \\a\\X\\n => \\\\a\\\\X\\\\n

                   force == False

                      \\a\\X\\n => \\\\a\\X\\\\n

                default := False

            **freeback**:
                Escapes backslashes outside character classes.
                Could be combined with *charback*. ::

                   \a\b\[\\] => \a\\b\\[\\]

    Returns:
        The escaped path with added '*\\\\*' in accordance to the rules and chosen
        options. The return type of the representation is the same as the input
        representation. ::

            str      =>  str
            unicode  =>  unicode
            list     =>  list
            tuple    =>  tuple

    Raises:
        PathError

        FileSysObjectsError

        TypeError

        pass-through

    """
    if not tpf:
        _ttpf = RTE
    else:
        try:
            _ttpf = rte2num[tpf]
        except KeyError:
            raise PathError("escapepathx:Parameter tpf: " + str(tpf))

    try:
        _strip = kargs.pop('strip')
    except KeyError:
        _strip = False

    _state = []
    if type(spath) in ISSTR:
        return PATHSCANNER.sub(lambda x: sub_esc(x, _ttpf, _strip, '', _state, **kargs), spath)

    elif type(spath) in (list, tuple,):
        ret = []
        for spx in spath:
            ret.append(PATHSCANNER.sub(lambda x: sub_esc(x, _ttpf, _strip, _state, **kargs), spx))
        return ret
    else:
        raise FileSysObjectsError("escapepathx:requires (str | list | tuple), got: " + str(spath))

def unescapepathx(spath, **kargs):
    """Unescape path - which has been escaped before. The path representation
    could either be as a string/unicode or split components as a *list*
    or *tuple*.

    .. warning::

       Processes strings accurately which were processed by *escapepathx()*
       before, else the result could be erroneous. In particular for
       windows paths due to the ambiguity of the '\\\\'!

    The same masking rules apply as for the *normpathx()* and
    *escapepathx()* calls. Escape sequences could be protected by quoting,
    which keeps the content literally. See *pathtools.stripquotes*.

    Args:
        **spath**:
            The path to be unescaped. ::

               spath := (
                    <path-string>
                  | <path-array>
               )

               path-string := (str | unicode)
               path-array := (list | tuple)

            * *path-string*

              The string representation of a complete path, which may contain literal,
              *glob*, and *re* expressions. The supported character representation
              is *str* or *unicode* for Pyton2.7 and Python3.5+.

            * *path-array*

              The component representation of a path, which consists of it's items,
              either as a *list* or as a *tuple*. Each item may contain literal,
              *glob*, and *re* expressions.

        kargs:
            **tpf**:
                Target platform, currently not used.

            **netpath**:
                When *True* considers double prefix separators as share and/or
                network application, else assumes these are the result of escaping
                with force.

                default := False

    Returns:
        The unescaped path with removed '\\' in accordance to the rules and chosen
        options. The return type of the representation is the same as the input
        representation. ::

            str      =>  str
            unicode  =>  unicode
            list     =>  list
            tuple    =>  tuple


    Raises:
        PathError

        FileSysObjectsError

        TypeError

        pass-through

    """
    netpath = kargs.get('netpath', False)
    tpf = kargs.get('tpf', RTE)
    if type(tpf) is not int:
        try:
            tpf = rte2num[tpf]
        except KeyError:
            raise PathError("unescapepathx:Parameter tpf: " + str(tpf))

    _tsep, _tpsep, tpf, _tpfn, _apre = gettpf(tpf)

    state = []
    if type(spath) in ISSTR:
        if netpath and spath[0] in ('/', '\\') and spath[1] in ('/', '\\'):
            return spath[0] + PATHSCANNER_UNESC.sub(lambda x: sub_unesc(x, tpf, state, **kargs), spath)
        else:
            return PATHSCANNER_UNESC.sub(lambda x: sub_unesc(x, tpf, state, **kargs), spath)
    elif type(spath) in (list, tuple,):
        ret = []
        for spx in spath:
            if netpath and spath[0] in ('/', '\\') and spath[1] in ('/', '\\'):
                return spath[0] + PATHSCANNER_UNESC.sub(lambda x: sub_unesc(x, tpf, state, **kargs), spx)
            else:
                return PATHSCANNER_UNESC.sub(lambda x: sub_unesc(x, tpf, state, **kargs), spx)
        return ret
    else:
        raise FileSysObjectsError("unescapepathx:requires (str | list | tuple), got: " + str(spath))

def splitpathx_win(p, **kw):
    """Split windows pathnames containing 'literal', 'glob', and 're/regexpr'.
    Serves the source platform windows and alike.
    For the call interface see *splitpathx()*

    Args:
        **p**:
            The path name to split.

        kargs:
            **apppre**:
                Application prefix.

                default := False

            **keepsep**:
                Keeps seprator, in particular the trailing.

                default := False

            **strip**:
                Strip separators, in particular the trailing.

                default := False

            **stripquote**:
                Strips *filesysobjects* triple-quotes.

                default := False

            **tpf**:
                Target platform. Defines some fine-tuning,
                e.g. for the file-URI, see *splitpathx*.

                default := current OS.

    Returns:
        The splitted path, else *[]*.

    Raises:
        pass-through

    """
    parts = []
    _cur = ""

    apppre = kw.get('apppre', False)
    keepsep = kw.get('keepsep', False)
    strip = kw.get('strip', False)
    stripquote = kw.get('stripquote', False)

    try:
        tpf = rte2num[kw.get('tpf', RTE_FILEURI)]
    except KeyError:
        raise FileSysObjectsError("parameter tpf = " + str(kw.get('tpf')))

    # controls updir: /../.. != ../..
    # 0: no history
    # 1: leading chain of RELATIVE up-dirs, keep them all
    # 2: has a leading chain of RELATIVE up-dirs
    state = 0
    inclass = 0

    for it in PATHSCANNER.finditer(p):
        g = it.lastindex  # PATHSCANNER ASCII_SC_CTRL
        _le = it.end(g)
        _isfirst = it.start(g) == 0
        _islast = _le == it.endpos
        _charbefore = it.start(g) - 1

        if it.group(g):
            x = it.group(g)
            c = ASCII_SC_CTRL[g]

            if c in (SC_CHRCLSSTART,):
                inclass = 1

                if not parts:
                    parts.append(x)

                else:
                    parts[-1] += x

            elif c in (SC_CHRCLSEND,):
                inclass = 0

                if not parts:
                    parts.append(x)

                else:
                    parts[-1] += x

            elif inclass and c not in (SC_DQUOTED, SC_SQUOTED,):
                if parts:
                    parts[-1] += x
                else:
                    parts.append(x)
                #continue

            elif c == SC_SLASH:  # 1 * '/'

                if not parts:  # if first - absolute
                    parts.append('')
                    parts.append('')
                    continue
                if strip:
                    if parts and len(parts) > 1 and not parts[-1]:
                        continue
                    elif _islast:
                        continue
                    elif it.endpos > it.end(g) and re.match(
                            r'[.][/\\\\]', it.string[it.end(g):]):
                        if parts[-1]:
                            parts.append('')
                        continue
                    elif re.match(r'^[/\\\\]*$', it.string[_le:]):
                        continue

                parts.append('')

            elif c == SC_SEPP:  # n * '/' - always followed by a shlash
                if strip:
                    continue
                parts.extend(['' for i in range(len(x))])  # @UnusedVariable

            elif c == SC_BSPAIR:  # pairs of '\\'
                if _isfirst:
                    parts.append('')
                    parts.append('')
                    continue

                if strip:
                    if it.string[_charbefore] not in '/\\':
                        parts.append('')

                else:
                    parts.append('')
                    parts.append('')

            elif c == SC_SLASHPREB:
                if strip:
                    continue
                parts.extend(['' for i in range(len(x))])  # @UnusedVariable

            elif c == SC_SEPW:  # 1 * '\\'
                if it.start(g) == 0:
                    parts.append('')
                    if strip and _islast:
                        continue
                    parts.append('')
                    continue

                    # FIXME:
                    if not strip or strip and it.string[_le] not in '/\\':
                        parts.append('')
                    continue

                if strip:
                    if it.string[_charbefore] in '/\\' or _islast:
                        continue
                parts.append('')

            elif c in (SC_PAPP, SC_PDOM, SC_WDOM,
                       SC_FUNC, SC_FNONLOCAL,):  # leading 2 * '' for '\\' or '//'
                if apppre:
                    if SC_FNONLOCAL and tpf in (RTE_FILEURI0, 'fileuri0',):
                        parts.append('file://')
                        continue
                    elif SC_FNONLOCAL and tpf in (RTE_FILEURI4, 'fileuri4',):
                        parts.append('file:///')
                        parts.append('')
                        continue

                    elif SC_FNONLOCAL and tpf in (RTE_FILEURI5, 'fileuri5', RTE_FILEURI, 'fileuri',):
                        parts.append('file:////')
                        parts.append('')
                        continue

                    if SC_FUNC:
                        parts.append('file:///')

            elif c in (SC_FMIN,):
                if apppre:
                    if tpf in (RTE_FILEURI, 'fileuri',):
                        parts.append('file://')
                    elif tpf in (RTE_FILEURI0, 'fileuri0',):
                        parts.append('file:')
                    else:
                        parts.append('file://')

            elif c in (SC_FABS,):
                if apppre:
                    if tpf in (RTE_FILEURI0, 'fileuri0',):
                        parts.append('file:')
                    else:
                        parts.append('file://')

            elif c in (SC_FSHORT,):
                if apppre:
                    parts.append('file://')

            elif c in (SC_DRIVENPSEP, SC_DRIVENWSEP,):  # posix does not have drives
                if strip:  # keep drive-root
                    if not parts:
                        parts.append(x[:2])
                    else:
                        parts[-1] += x[:2]
                    parts.append('')
                else:
                    if not parts:
                        parts.append(x[:2])
                    else:
                        parts[-1] += x[:2]
                    parts.extend(['' for i in range((len(x) - 2))])  # @UnusedVariable

            elif c == SC_DRIVE:
                if not parts:
                    parts.append(x)
                else:
                    parts[-1] += x[:2]

            elif c == SC_NULLDIR:
                continue

            elif c == SC_UPDIR:
                if _isfirst:
                    parts.append('..')
                    parts.append('')
                    state = 1
                    continue
                elif state == 1:
                    parts[-1] += '..'
                    parts.append('')
                    if len(it.string) > _le + 3 and it.string[_le:_le + 3] != '../' or \
                            len(it.string) > _le + 2 and it.string[_le:_le + 2] != '..':
                        state = 2
                    continue

                if parts:
                    if not parts[0] and not parts[1]:  # share/posix-app
                        if len(parts) > 5:
                            if not parts[-1]:
                                parts.pop()
                            parts.pop()
                            parts.append('')
                        elif len(parts) > 4:
                            parts.pop()

                    elif not parts[0]:  # absolute path
                        if len(parts) > 2:
                            if not parts[-1]:
                                parts.pop(-2)
                            else:
                                parts.pop()
                                parts.append('')
                        elif len(parts) > 1:
                            parts.pop()
                            parts.append('')

                    else:  # relative path
                        if not parts[-1]:
                            if len(parts) > 3 and parts[-2] != '..':
                                parts.pop()
                                parts.pop()
                            else:
                                parts.pop()
                                parts.append('..')
                        else:
                            parts.pop()
                        parts.append('')

                continue

            elif c in (SC_DQUOTED, SC_SQUOTED):
                if stripquote:
                    _x = x[3:-3]
                else:
                    _x = x
                if not parts:
                    parts.append(_x)
                else:
                    parts[-1] += _x
                continue

            elif not parts:
                parts.append(x)

            else:
                parts[-1] += x

    if strip and parts and not keepsep:
        while parts and not parts[-1]:
            parts.pop()

    if apppre and parts != [] and not parts[0].startswith('file:'):
        _x = _file_uri_scheme[_get_lead_sep.match(parts[0]).group(0)]
        if _x == 'file':
            if parts[0] == '':
                if tpf in (RTE_FILEURI4, RTE_FILEURI5,) and parts[2] == '':
                    parts[0] = _file_uri_scheme[tpf]
                elif tpf == RTE_FILEURI0:
                    parts[0] = _file_uri_scheme[RTE_FILEURI0]
                else:
                    parts[0] = _file_uri_scheme[RTE_FILEURI]
            else:
                # does not recognize drives
                raise PathError("file-uri requires absolute path, got: " + str(p))

        elif _x == 'netapp':
            if tpf in (RTE_FILEURI4, RTE_FILEURI5,):
                parts[0] = _file_uri_scheme[tpf]
            else:
                parts[0] = _file_uri_scheme[RTE_FILEURI5]
        else:
            parts[0] = _file_uri_scheme[RTE_FILEURI]

    return tuple(parts)


def splitpathx_posix(p, **kw):
    """Split pathnames containing 'literal', 'glob', and 're/regexpr'.
    Serves the source platform POSIX and alike.
    For the call interface see *splitpathx()*

    Args:
        **p**:
            The path name to split.

        kargs:
            **apppre**:
                Application prefix.

                default := False

            **keepsep**:
                Keeps seprator, in particular the trailing.

                default := False

            **strip**:
                Strip separators, in particular the trailing.

                default := False

            **stripquote**:
                Strips *filesysobjects* triple-quotes.

                default := False

            **tpf**:
                Target platform. Defines some fine-tuning,
                e.g. for the file-URI, see *splitpathx*.

                default := current OS.

    Returns:
        The splitted path, else *[]*.

    Raises:
        pass-through

    """
    parts = []
    _cur = ""

    apppre = kw.get('apppre', False)
    keepsep = kw.get('keepsep', False)
    strip = kw.get('strip', False)
    stripquote = kw.get('stripquote', False)

    try:
        tpf = rte2num[kw.get('tpf', RTE_FILEURI)]
    except KeyError:
        raise FileSysObjectsError("parameter tpf = " + str(kw.get('tpf')))

    # controls updir: /../.. != ../..
    # 0: no history
    # 1: leading chain of RELATIVE up-dirs, keep them all
    # 2: has a leading chain of RELATIVE up-dirs
    state = 0
    inclass = 0

    for it in PATHSCANNER.finditer(p):
        g = it.lastindex  # PATHSCANNER ASCII_SC_CTRL
        _le = it.end(g)
        _isfirst = it.start(g) == 0
        _islast = _le == it.endpos
        _charbefore = it.start(g) - 1

        if it.group(g):
            x = it.group(g)
            c = ASCII_SC_CTRL[g]

            if c in (SC_CHRCLSSTART,):
                inclass = 1

                if not parts:
                    parts.append(x)

                else:
                    parts[-1] += x

            elif c in (SC_CHRCLSEND,):
                inclass = 0

                if not parts:
                    parts.append(x)

                else:
                    parts[-1] += x

            elif inclass and c not in (SC_DQUOTED, SC_SQUOTED,):
                if parts:
                    parts[-1] += x
                else:
                    parts.append(x)
                #continue

            elif c == SC_SLASH:  # 1 * '/'

                if not parts:  # if first - absolute
                    parts.append('')
                    parts.append('')
                    continue
                if strip:
                    if parts and len(parts) > 1 and not parts[-1]:
                        continue
                    elif _islast:
                        continue
                    elif it.endpos > it.end(g) and re.match(
                            r'[.]/', it.string[it.end(g):]):
                        if parts[-1]:
                            parts.append('')
                        continue
                    elif re.match(r'^[/\\\\]*$', it.string[_le:]):
                        continue

                parts.append('')

            elif c == SC_SEPP:  # n * '/' - always followed by a shlash
                if strip:
                    continue
                parts.extend(['' for i in range(len(x))])  # @UnusedVariable

            elif c == SC_BSPAIR:  # pairs of '\\'
                if _isfirst:
                    parts.append('')
                    parts.append('')
                    continue

                if strip:
                    if it.string[_charbefore] not in '/\\':
                        parts.append('')

                else:
                    parts.append('')
                    parts.append('')

            elif c == SC_SLASHPREB:
                if strip:
                    continue
                parts.extend(['' for i in range(len(x))])  # @UnusedVariable

            elif c == SC_SEPW:  # 1 * '\\'
                if it.start(g) == 0:
                    parts.append('')
                    if strip and _islast:
                        continue
                    parts.append('')
                    continue

                    # FIXME:
                    if not strip or strip and it.string[_le] not in '/\\':
                        parts.append('')
                    continue

                if strip:
                    if it.string[_charbefore] in '/\\' or _islast:
                        continue
                parts.append('')

            elif c in (SC_PAPP, SC_PDOM, SC_WDOM,
                       SC_FUNC, SC_FNONLOCAL,):  # leading 2 * '' for '\\' or '//'
                if apppre:
                    if SC_FNONLOCAL and tpf in (RTE_FILEURI0, 'fileuri0',):
                        parts.append('file://')
                        continue
                    elif SC_FNONLOCAL and tpf in (RTE_FILEURI4, 'fileuri4',):
                        parts.append('file:///')
                        parts.append('')
                        continue

                    elif SC_FNONLOCAL and tpf in (RTE_FILEURI5, 'fileuri5', RTE_FILEURI, 'fileuri',):
                        parts.append('file:////')
                        parts.append('')
                        continue

                    if SC_FUNC:
                        parts.append('file://')

                else:
                    parts.append('')
                    parts.append('')
                    parts.append('')

            elif c in (SC_FMIN,):
                if apppre:
                    if tpf in (RTE_FILEURI, 'fileuri',):
                        parts.append('file://')
                    elif tpf in (RTE_FILEURI0, 'fileuri0',):
                        parts.append('file:')
                    else:
                        parts.append('file://')

            elif c in (SC_FABS,):
                if apppre:
                    if tpf in (RTE_FILEURI0, 'fileuri0',):
                        parts.append('file:')
                    else:
                        parts.append('file://')

            elif c in (SC_FSHORT,):
                if apppre:
                    parts.append('file://')

            elif c in (SC_DRIVENPSEP, SC_DRIVENWSEP,):  # posix does not have drives
                if not parts:
                    parts.append('')
                if strip:  # keep drive-root
                    parts[-1] += x[:2]
                    parts.append('')
                else:
                    parts[-1] += x[:2]
                    parts.extend(['' for i in range((len(x) - 2))])  # @UnusedVariable

            elif c == SC_DRIVE:
                if not parts:
                    parts.append(x)
                else:
                    parts[-1] += x[:2]

            elif c == SC_NULLDIR:
                continue

            elif c == SC_UPDIR:
                if _isfirst:
                    parts.append('..')
                    parts.append('')
                    state = 1
                    continue
                elif state == 1:
                    parts[-1] += '..'
                    parts.append('')
                    if len(it.string) > _le + 3 and it.string[_le:_le + 3] != '../' or \
                            len(it.string) > _le + 2 and it.string[_le:_le + 2] != '..':
                        state = 2
                    continue

                if parts:
                    if not parts[0] and not parts[1]:  # share/posix-app
                        if len(parts) > 5:
                            if not parts[-1]:
                                parts.pop()
                            parts.pop()
                            parts.append('')
                        elif len(parts) > 4:
                            parts.pop()

                    elif not parts[0]:  # absolute path
                        if len(parts) > 2:
                            if not parts[-1]:
                                parts.pop(-2)
                            else:
                                parts.pop()
                                parts.append('')
                        elif len(parts) > 1:
                            parts.pop()
                            parts.append('')

                    else:  # relative path
                        if not parts[-1]:
                            if len(parts) > 3 and parts[-2] != '..':
                                parts.pop()
                                parts.pop()
                            else:
                                parts.pop()
                                parts.append('..')
                        else:
                            parts.pop()
                        parts.append('')

                continue

            elif c in (SC_DQUOTED, SC_SQUOTED):
                if stripquote:
                    _x = x[3:-3]
                else:
                    _x = x
                if not parts:
                    parts.append(_x)
                else:
                    parts[-1] += _x
                continue

            elif not parts:
                parts.append(x)

            else:
                parts[-1] += x

    if strip and parts and not keepsep:
        while parts and not parts[-1]:
            parts.pop()

    if apppre and parts != [] and not parts[0].startswith('file:'):
        _x = _file_uri_scheme[_get_lead_sep.match(parts[0]).group(0)]
        if _x == 'file':
            if parts[0] == '':
                if tpf in (RTE_FILEURI4, RTE_FILEURI5,) and parts[2] == '':
                    parts[0] = _file_uri_scheme[tpf]
                elif tpf == RTE_FILEURI0:
                    parts[0] = _file_uri_scheme[RTE_FILEURI0]
                else:
                    parts[0] = _file_uri_scheme[RTE_FILEURI]
            else:
                # does not recognize drives
                raise PathError("file-uri requires absolute path, got: " + str(p))

        elif _x == 'netapp':
            if tpf in (RTE_FILEURI4, RTE_FILEURI5,):
                parts[0] = _file_uri_scheme[tpf]
            else:
                parts[0] = _file_uri_scheme[RTE_FILEURI5]
        else:
            parts[0] = _file_uri_scheme[RTE_FILEURI]

    return tuple(parts)


def splitpathx(spath, **kw):
    """Split pathnames into a list/tuple of items for each directory.
    For example ::

       In [15]: filesysobjects.paths.splitpathx("/a/b/c")
       Out[15]: ('', 'a', 'b', 'c')

       In [16]: filesysobjects.paths.splitpathx("x:/a/b/c")
       Out[16]: ('x:', 'a', 'b', 'c')

       In [17]: filesysobjects.paths.splitpathx("x:\\a\\b\\c")
       Out[17]: ('x:', 'a', 'b', 'c')

    For *URI*s and search paths refer to *splitapppathx*.

    Supports directory name types as 'literal', 'glob', and 're/regexpr'.
    Supports the same syntax elements as *normpathx*, while it is prepared
    to simple application of the built-in *join()* with *os.sep*.

    Is not aware of application tags except Network-Shares,
    Posix-Applications, and file-URI.

    **REMARK**:
        The intention is to replace the 'str.split()' method
        for the split of the path parts, thus this is different to the
        method 'os.path.split()'.

    Args:

        **spath**:
            Path to split.

        kw:

            **apppre**:
                Application prefix, when 'True' the scheme is included,
                else dropped. ::

                   apppre=(True|False)

            **keepsep**:
                Modifies the behavior of 'strip' parameter.
                If 'False', the trailing separator is dropped. ::

                   splitpathx('/a/b', keepsep=False)   => ('', 'a', 'b')
                   splitpathx('/a/b/', keepsep=False)  => ('', 'a', 'b')

                for 'True' trailing separators are kept as directory
                marker::

                   splitpathx('/a/b', keepsep=True)    => ('', 'a', 'b')
                   splitpathx('/a/b/', keepsep=True)   => ('', 'a', 'b', '')

            **pathsep**:
                Optional search path separator.

                    posix: ':'

                    win32: ';'

                default := os.pathsep

            **sep**:
                Optional path separator.

                    posix: '/'

                    win32: '\\'

                default := os.path.sep

            **strip**:
                Removes null-entries.

                default := False

            **stripquote**:
                Removes paired triple-quotes of protected/masked
                string sections. ::

                   "/a/'''head:'''/c" => "/a/head:/c"

                default := False

            **spf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to the API in the manual at :ref:`spf <OPTS_SPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.getspf() <paths.html#getspf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.

            **tpf**:
                Target platform. Even though the splitted form of a resource path
                is basically canonical, some details of the specifications for
                slightly variations requires the granular fine-tuning. Thus defines
                in case of ambiguity the *scheme* for *apppre=True*. Accepts the
                following values only. ::

                   tpf := (
                        RTE_FILEURI0 | 'fileuri0'  # RFC8089 - minimal
                      | RTE_FILEURI4 | 'fileuri4'  # RFC8089 - 4-slash UNC/POSIX-app
                      | RTE_FILEURI5 | 'fileuri5'  # RFC8089 - 5-slash UNC/POSIX-app
                      | RTE_FILEURI  | 'fileuri'   # RFC8089 - canonical
                   )

    Returns:
        A list containing the path split into it's components. The list
        is prepared to be concatenated by *join()*.

        The interface is aware of the *os.path.sep* character, but a
        present regular expression may span multiple path components,
        which have to be handled dynamically when applying the path
        pattern e.g. by *findpattern*.

    Raises:
        pass-through

    """
    try:
        spf = rte2num[kw.get('spf', RTE_FILEURI)]
    except KeyError:
        raise FileSysObjectsError("parameter error: spf =" + str(kw.get('spf')))

    if spf & RTE_WIN32:
        return splitpathx_win(spath, **kw)

    return splitpathx_posix(spath, **kw)


def normpathx(spath, **kargs):
    """Normalize paths, similar to 'os.path.normpath()' - with
    optional extensions paths with basic application schemes
    and search paths, dos-drives, and the split of paths into
    directories. The various representations could be converted
    on-the-fly. ::

        smb, cifs, file, http/https, UNC, POSIX-network apps

    For advanced processing of application schemes refer to
    *normapppathx()* and 'splitapppathx()'. The path could
    include regular expressions *re* and *glob*, literals
    and masked parts.

    * regular expressions

      The supported regular expressions are native Python regular
      expressions as supported by 're' with support of expressions
      spanning multiple directories.

    * globs

      Standard module *glob*.

    * literals:

      Any literal path.

    Regular expressions and globs could be masked as quoted strings,
    which are kept unchanged.

    The *normpathx* provides the features as simple interface for the
    normalization across multiple platforms. The companion interface
    provide various features, e.g. the *escapepathx* and *unescapepathx*
    of path names including *re* and *glob*.


    Args:
        **spath**:
            A single path entry - no valid 'os.pathsep'. In case of
            required search path including semantic 'os.pathsep'
            use 'splitapppathx()'.

        kargs:

            **apppre**:
                Application prefix.

                default:=False

            **keepsep**:
                Keeps significant seperators, in particular
                the trailing path separator 'sep', and the
                trailing search path 'pathseparator'.

            **strip**:
                Strips redundancies from path names, ::

                "a/.//./b/c/../" => "a/b"

                see related 'keepsep' ::

                "a/.//./b/c/../" => "a/b/"

                default:=True

            **stripquote**:
                Removes paired triple-quotes of protected/masked
                string sections. ::

                   "/a/'''head:'''/c" => "/a/head:/c"

                default := False

            **spf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.getspf() <paths.html#getspf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.

            **tpf**:
                Target platform, defines the output syntax domain.
                For the syntax refer to the API in the manual at :ref:`tpf <OPTS_TPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.gettpf() <paths.html#gettpf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.

            **pathsep**:
                Changes path separator for the source platform. ::

                   pathsep := (
                         (: | ;)         # replaces by ':' or ';'
                       | <keyword>
                       | <#enum>
                   )


    Returns:
        Normalized path.

    Raises:
        PathError

        pass-through

    """

    strip = kargs.get('strip', True)
    tpf = kargs.get('tpf', False)
    apppre = kargs.get('apppre', False)

    #
    # target platform
    #
    # use system interfaces
    if tpf in ('local', RTE_LOCAL,):
        return os.path.normpath(spath)
    elif tpf in ('cnp', RTE_CNP,):
        return posixpath.normpath(spath)
    elif tpf in ('cnw', RTE_CNW,):
        return ntpath.normpath(spath)

    _tsep, _tpsep, tpf, _tpfn, _apre = gettpf(tpf, apppre=apppre)

    #
    # sourceplatform
    #
    # recognized pathsep, empty is no replacement
    spf = kargs.get('spf', False)

    _sep, _psep, spf, _spfn = getspf(spf)

    # recognized pathsep, empty or False is no replacement
    _p = kargs.get('pathsep')
    if _p:
        try:
            _psep = rte_map[_p][1]
        except KeyError:
            raise PathError("unknown pathseparator: " + str(kargs.get('pathsep')))

    try:
        cb = sub_path_calls[tpf]
    except KeyError:
        raise PathError("Platform callback: " + str(tpf))

    kw = {}
    kw['apppre'] = apppre
    kw['keepsep'] = kargs.get('keepsep', False)
    kw['stripquote'] = kargs.get('stripquote', False)

    state = ([], [],)
    if strip:
        try:
            _m = _NULLDIRS.match(spath)
        except TypeError:
            _m = _NULLDIRS.match(escapepathx(spath, force=True))
#         except sre_constants.error:
#             _m = _NULLDIRS.match(escapepathx(spath, force=True))

        if _m:
            state = []
            kw['tpf'] = _tpfn
            kw['pathsep'] = _psep
            kw['sep'] = _sep
            kw['strip'] = strip
            return _tsep.join(splitpathx(spath, **kw))
        else:
            return PATHSCANNER.sub(
                lambda x: cb(x, _spfn, strip, _psep, state, **kw), spath)

    else:
        if _psep is False:
            return PATHSCANNER.sub(lambda x: cb(x, _spfn, strip, state, **kw), spath)
        else:
            return PATHSCANNER.sub(lambda x: cb(x, _spfn, strip, _psep, state, **kw), spath)

