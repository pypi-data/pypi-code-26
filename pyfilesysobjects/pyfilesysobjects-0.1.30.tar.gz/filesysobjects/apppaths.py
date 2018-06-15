# -*- coding: utf-8 -*-
"""The 'filesysobjects.apppaths' module provides operations on static application resource paths.
"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys

import re
import glob

from pysourceinfo.fileinfo import getcaller_pathname, getcaller_filepathname
from pysourceinfo.helper import getpythonpath_rel

from filesysobjects import FileSysObjectsError, AppPathError, PathError, ISSTR, \
    RTE, RTE_POSIX, RTE_WIN32, RTE_GENERIC, \
    RTE_SMB, RTE_CNW, RTE_CNP, RTE_LOCAL, \
    RTE_URI, RTE_HTTP, RTE_HTTPS, RTE_FILEURI, RTE_FILEURI0, RTE_FILEURI4, RTE_FILEURI5, \
    num2rte
from filesysobjects.paths import normpathx, escapepathx, unescapepathx, gettpf, getspf

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez" \
                "@Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.20'
__uuid__ = "4135ab0f-fbb8-45a2-a6b1-80d96c164b72"

__docformat__ = "restructuredtext en"

#
# for test and development
_mydebug = False

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

#
# prohibited characters for optional validation - see strict options
#

#: windows: ::
#:
#:    r'[:<>*?]'
INVALIDCHARSWIN = re.compile(r'[:<>*?]')

#: posix: ::
#:
#:    r'\0'
INVALIDCHARSPOSIX = re.compile(r'\0')

#: posix + windows: ::
#:
#:    r'[:<>*?\0]'
INVALIDCHARS = re.compile(r'[:<>*?\0]')  #: super position of both: r'[:<>*?\0]'

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

#: Dummy for same group count for processing.
_DUMMY = """(()|())"""

#: The tail of a path atom including possible escaped os.pathsep as ordinary character
_NOSEP_COL = """(
    (["]{3}.*?["]{3}|[']{3}.*?[']{3}|[^:"']+|['"])+
   |(["]{3}.*?["]{3}|[']{3}.*?[']{3}|[^:"']+|['"])+
   )"""

#: The tail of a path atom including possible escaped os.pathsep as ordinary character
_NOSEP_SEM = """(
    (["]{3}.*?["]{3}|[']{3}.*?[']{3}|[^;"']+|['"])+
   |(["]{3}.*?["]{3}|[']{3}.*?[']{3}|[^;"']+|['"])+
   )"""


# [MS-DTYP] - 2.2.57 - UNC definitions
# pchar = %x20-21 / %x23-29 / %x2D-2E / %x30-39 / %x40-5A / %x5E-7B / %x7D-FF
# pchar = r'[\x20-\x21\x23-\x29\x2D-\x2E\x30-\x39\x40-\x5A\x5E-\x7B\x7D-\xFF]'
# pchar="""[^\x00-\x1f\x22\x2a-\x2c\x2f\x3a-\x3f\x5b-\x5d\x7c]"""


#: Scanner/Parser for colon based search path separator: ::
#:
#:    os.pathsep == ':'
#:
#: The applied rules are: ::
#:
#:     4: ('file://[/]' +2SEP | unc://)  +(host)  +1SEP  +(share)  +(object)  # [MS-DTYP] 2.2.57
#:    12: ('file://')                    +()      +()    +(drive)  +(path)    # RFC8089 -
#:    20: ('file://')                    +(auth)  +()    +()       +(path)    # RFC8089 - non-local files
#:    28: ('file://|file:')              +()      +()    +()       +(path)    # RFC8089 - traditional
#:    36: ('smb://'|'cifs://')  +(host)  +1SEP  +(share)  +(path)             # RFC-SMB
#:    44: (2SEP)                +(host)  +1SEP  +(share)  +(path)             # [MS-DTYP] 2.2.57 - a share present
#:    52: (scheme '://')           +(auth)  +1SEP  +(path)   +"?" +(query-fragment)  # RFC3869
#:    60: ()                    +()      +()    +(drive)  +(path)             # MS-DOS / WIN
#:    68: ()                    +()      +()    +(drive)  +(path)             # MS-DOS / WIN
#:    76: ()                    +()      +()    +(drive)  +()                 # MS-DOS / WIN
#:    84: ()                    +()      +()    +()       +(path)             # general filesystems
#:    92: ()                    +()       +()   +()       +()
#:    94 os.pathsep
APPPATHSCANNER_COL = re.compile(
r"""((
     ((file://[/]{0,1}[/\\\\]{2}|unc://)(.{0,1}[^/\\\\]+)[/\\\\]([^/\\\\]+)[/\\\\]*([/\\\\]""" + _NOSEP_COL + """)) #  4
    |((file:///{0,1}|file:)()([a-zA-Z]:)[/\\\\]*?([/\\\\]{0,1}""" + _NOSEP_COL + """))                               # 12
    |((file://)([^/\\\\]+)()(""" + _NOSEP_COL + """))                                                                # 20
    |((file://|file:)()()(""" + _NOSEP_COL + """))                                                                   # 28
    |((smb://|cifs://)([^/]{0,1}[^/\\\\]*)[/\\\\]+([^/\\\\]+)[/\\\\]*([/\\\\]""" + _NOSEP_COL + """))                # 36
    |(([\\\\]{2}|[/]{2})(?![:])([^/\\\\]+)[/\\\\]([^/\\\\]+)[/\\\\]*([/\\\\]""" + _NOSEP_COL + """))                 # 44
    |(([^:/?#]{2,}://)([^/]{0,1}[^/\\\\]*)[/\\\\]*?([/]{0,1}[^?:;]+)([?]""" + _NOSEP_COL + """){0,1})                # 52
    |(()()([a-zA-Z]:)([/\\\\]+?""" + _NOSEP_COL + """))                                                              # 60
    |(()()([a-zA-Z]:)(""" + _NOSEP_COL + """))                                                                       # 68
    |(()()([a-zA-Z]:)(""" + _DUMMY + """))                                                                           # 76
    |(()()()""" + _NOSEP_COL + """())                                                                                # 84
    |(()()()()""" + _DUMMY + """(?=[:]))                                                                             # 92
)[:]?)                                                                                                               # 94
""", re.X)  # @UndefinedVariable

#: Scanner/Parser for semicolon based search path separator. ::
#:
#:    os.pathsep == ';'
#:
#: The applied rules are corresponding to *APPPATHSCANNER_COL*.
APPPATHSCANNER_SEM = re.compile(
r"""((
     ((file://[/]{0,1}[/\\\\]{2}|unc://)(.{0,1}[^/\\\\]+)[/\\\\]([^/\\\\]+)[/\\\\]*([/\\\\]""" + _NOSEP_SEM + """)) #  4
    |((file:///{0,1}|file:)()([a-zA-Z]:)[/\\\\]*?([/\\\\]{0,1}""" + _NOSEP_SEM + """))                               # 12
    |((file://)([^/\\\\]+)()(""" + _NOSEP_SEM + """))                                                                # 20
    |((file://|file:)()()(""" + _NOSEP_SEM + """))                                                                   # 28
    |((smb://|cifs://)([^/]{0,1}[^/\\\\]*)[/\\\\]+([^/\\\\]+)[/\\\\]*([/\\\\]""" + _NOSEP_SEM + """))                # 36
    |(([\\\\]{2}|[/]{2})(?![:])([^/\\\\]+)[/\\\\]([^/\\\\]+)[/\\\\]*([/\\\\]""" + _NOSEP_SEM + """))                 # 44
    |(([^;/?#]{2,}://)([^/]{0,1}[^/\\\\]*)[/\\\\]*?([/]{0,1}[^?:;]+)([?]""" + _NOSEP_SEM + """){0,1})                # 52
    |(()()([a-zA-Z]:)([/\\\\]+?""" + _NOSEP_SEM + """))                                                              # 60
    |(()()([a-zA-Z]:)(""" + _NOSEP_SEM + """))                                                                       # 68
    |(()()([a-zA-Z]:)(""" + _DUMMY + """))                                                                           # 76
    |(()()()""" + _NOSEP_SEM + """())                                                                                # 84
    |(()()()()""" + _DUMMY + """(?=[;]))                                                                             # 92
)[;]?)                                                                                                    # 94
""", re.X)  # @UndefinedVariable


#: Helper with group indexes pointing onto the supported syntax terms of *APPPATHSCANNER*.
APPPATHINDEX = (
    4,
    12,
    20,
    28,
    36,
    44,
    52,
    60,
    68,
    76,
    84,
    92, )

#: Helper with human readable enums for types of path variable elements of *APPPATHINDEX*.
APPTYPES = (
    'share',
    'ldsys',
    'rfsys',
    'lfsys',
    'smb',
    'share',
    'uri',
    'ldsys',
    'ldsys',
    'ldsys',
    'lfsys',
    'lfsys', )

#: Helper with human readable enums for secondary level-2 types of *APPTYPES*.
APPTYPES_L2 = {
    'http://': ('http',),
    'https://': ('https',),
    'smb://': ('smb',),
    'cifs://': ('smb',),  # non-standard
    'unc://': ('share',),  # non-standard
    '\\\\': ('share',),
    '//': ('share',),
}

#
# *** splits environment variables ***
#
if RTE & RTE_WIN32:
    _ENV_SPLIT = re.compile(  #: Split-out environment variables for substitution.
       r"""
       (
           (([^%]*?)([%][a-zA-Z0-9_]+[%]))           # 2: defined without brace
         | (([^%]*?)([%][a-zA-Z0-9_]+[^%]?))         # 5: ERROR:
         | ((.*)())                                  # 8: any
       )
       """, re.X)  # @UndefinedVariable

    _ENV_SPLITg = [  #: Entry points into sub strings environment variables and literals.
        2,
        5,
        8,
    ]
else:
    _ENV_SPLIT = re.compile(  #: Split-out environment variables for substitution.
       r"""
       (
           (([^$]*?)([$][{][a-zA-Z0-9_]+[}]))        # 2: defined with brace
         | (([^$]*?)([$][a-zA-Z0-9_]+[;]?))          # 5: defined without brace
         | (([^$]*?)([$][{][a-zA-Z0-9_]+[^}]?))      # 8: ERROR:
         | ((.*)())                                  # 11: any
       )
       """, re.X)  # @UndefinedVariable

    _ENV_SPLITg = [  #: Entry points into sub strings environment variables and literals.
        2,
        5,
        8,
        11,
    ]

# pylint: enable-msg=W0105
_tpf_num = {
    'default': RTE,
    'uri': RTE_URI,  # TODO: replace by RTE_URI virtual platform bit
    'http': RTE_HTTP,  # TODO: replace by RTE_URI virtual platform bit
    'https': RTE_HTTPS,  # TODO: replace by RTE_URI virtual platform bit
    'posix': RTE_POSIX,
    'win': RTE_WIN32,
    'win32': RTE_WIN32,
    'local': RTE,
}


def addpath_to_searchpath(spath, plist=None, **kargs):
    """Adds a path to 'plist'.

    In case of relative path searches in provided
    'plist', or 'kargs[searchplist]'a hook, when found
    verifies the existence within file system, in case
    of success adds the completed path to 'plist' the list.

    In case of 'glob' adds all entries.

    Args:
        **spath**:
            A path to be added to 'plist'.
            See common options for details.
            Valid scope types:

                * literal : X
                * re      : -
                * blob    : -

            default := caller-file-position.

        **plist**:

            List to for the storage, and by default
            search list too.
            See common options for details.

            default := sys.path

        kargs:
            **append**:
                Append, this is equal to
                pos=len(plist).

            **checkreal**:
                Checks redundancy by resolving real path,
                else literally.

            **exist**:
                Checks whether exists, else nothing is done.

            **pos**:
                A specific position for insertion
                within range(0,len(plist)). ::

                  pos := #pos

            **prepend**:
                Prepend, this is equal to
                pos=0.

            **redundant**:
                Add relative, allow redundant when
                same is already present.

            **relative**:
                Add relative sub path to
                provided base. ::

                   relative := <base>:

            **searchplist**:
                Alternative list to search for checks.

            **spf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.getspf() <paths.html#getspf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.

            **tpf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to the API in the manual at :ref:`tpf <OPTS_TPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.gettpf() <paths.html#gettpf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.

    Returns:
        When successful returns insertion position, else a 'value<0'.
        The insertion position in case of multiple items is the position
        of the last.

    Raises:
        AppPathError
        passed through exceptions
    """
    if plist == None:
        plist = sys.path

    _spf = kargs.get('spf', False)
    _tpf = kargs.get('tpf', False)

    _splist = kargs.get('searchplist', plist)

    pos = 0
    relative = None
    _exist = False
    _red = False
    _chkr = False
    for k, v in kargs.items():
        if k == 'prepend':
            pos = 0
        elif k == 'append':
            pos = -1
        elif k == 'pos':
            if not type(v) is int:
                raise AppPathError("Digits required for 'pos'*" + str(pos)
                                       + ")")
            pos = v
        elif k == 'relative':
            relative = v.split(os.pathsep)
        elif k == 'exists':
            _exist = v
        elif k == 'redundant':
            _red = v
        elif k == 'checkreal':
            _chkr = v

    def _add(s):
        if relative:
            s = getpythonpath_rel(s, relative)
        if not _red:
            if _chkr:
                for sx in map(lambda x: os.path.realpath(x), plist):
                    if os.path.realpath(s) == sx:
                        return
            else:
                if s in plist:
                    return

        if pos == -1:
            plist.append(s)
            return len(plist) - 1
        else:
            plist.insert(pos, s)
            return pos

    # normalize
    _start_elems = splitapppathx(spath, appsplit=True, **kargs)[0]
    spath = splitapppathx_getlocalpath(_start_elems, tpf=_tpf)

    if _exist:
        if os.path.isabs(spath) and os.path.exists(spath):
            return _add(spath)
        elif os.path.exists(os.path.curdir + os.sep + spath):
            return _add(os.path.normpath(os.path.curdir + os.sep + spath))
        else:
            for s in _splist[:]:
                if os.path.exists(s + os.sep + spath):
                    pos = _add(s + os.sep + spath)
    else:
        if os.path.isabs(spath):
            return _add(spath)
        elif os.path.exists(os.path.curdir + os.sep + spath):
            return _add(os.path.normpath(os.path.curdir + os.sep + spath))
        else:
            for s in _splist[:]:
                if os.path.exists(s + os.sep + spath):
                    pos = _add(s + os.sep + spath)
    return pos


def delpath_from_searchpath(dellist, plist=None, **kargs):
    """Deletes a list of paths from 'plist'.

    Args:
        **dellist**:
            A list of paths to be deleted
            from 'plist'. Valid scope types:

                * literal : X
                * re      : X
                * glob    : X

            see kargs[regexpr|glob].

            default := None

        **plist**:
            List of search paths.

            default := sys.path

        kargs:
            The following keys are additional before
            comparison, on 'dellist' only when no
            match pattern is provided:

                **case**:
                    Calls on both: os.path.normcase

                **esc**:
                    Calls on both: escapepathx/unescapepathx

                **exist**:
                    Calls on both: os.path.exists

                **noexist**:
                    Calls on both: not os.path.exists

                **norm**:
                    Calls on both: normpathx

                **norm**:
                    Calls on both: os.path.normpath

                **real**:
                    Calls on both: os.path.realpath

            **regexpr|glob**:
                Input is a list of

                **regexpr**:
                    regular expressions,
                    just processed by
                        're.match(dl,pl)'

                **glob**:
                    process glob, and check
                    containment in set

    Returns:
        When successful returns True, else False.

    Raises:
        passed through exceptions

    """
    if plist == None:
        plist = sys.path
    if not dellist:
        return True
    _exists = False
    _rg = False
    _raw = kargs.get('raw', False)
    _real = kargs.get('real', False)
    _norm = kargs.get('norm', False)
    _case = kargs.get('case', False)

    for k, v in kargs.items():  # @UnusedVariable

        if k == 'exist':
            _exist = True
            _exists = True

        elif k == 'noexist':
            _exist = False
            _exists = True

        elif k == 'regexpr':
            _reg = True
            _glob = False
            __rg = True

        elif k == 'glob':
            _reg = False
            _glob = True
            __rg = True

    # seems to be sure
    if type(dellist) == str:
        dellist = [dellist]

    for dl in dellist:

        for pl in reversed(plist):

            if not _raw:
                if dl and len(dl) > 6 and dl[0:7] == 'file://':
                    dl = os.sep + dl[7:].lstrip(os.sep)
                if pl and len(pl) > 6 and pl[0:7] == 'file://':
                    pl = os.sep + pl[7:].lstrip(os.sep)

            if _real:
                if not _rg:
                    dl = os.path.realpath(dl)
                pl = os.path.realpath(pl)

            if _norm:
                if not _rg:
                    dl = os.path.normpath(dl)
                pl = os.path.normpath(pl)

            if _case:
                if not _rg:
                    dl = os.path.normcase(dl)
                pl = os.path.normcase(pl)

            if _exists:
                if _exist:
                    if not _rg:
                        if not os.path.exists(pl) or not os.path.exists(dl):
                            continue
                    elif os.path.exists(pl):
                        continue

            if _rg:
                if _reg:
                    if re.match(dl, pl):
                        plist.pop(plist.index(pl))
                elif _glob:
                    if pl in glob.glob(dl):
                        plist.pop(plist.index(pl))
            else:
                if dl == pl:
                    plist.pop(plist.index(pl))

    return True


def join_apppathx_entry(entry, **kw):
    """Assembles the components of an application path entry.

    Known standard applications are: ::

      cifs , file, ftp, http, https, smb, unc, uri
      <unc-file-path>, <posix-app-file-path>

    The path entry is not normalized again, thus
    has to be in the appropriate platform syntax.

    Args:

        **entry**:
            Application entry as provided by *splitapppathx()*.


        kw:
            **apppre**:
                Add application prefix.

            **tpf**:
                Target platform.

    Returns:

        Entry as a single stings.

    Raises:
        pass-through

    """
    res = ''
    apppre = kw.get('apppre', True)

    _tpf = kw.get('tpf', None)
    if _tpf == None:
        # use the entry is not tpf provided
        _tpf = re.sub(r':.*$', '', entry[0])
    elif type(_tpf) is int:
        if _tpf & RTE_URI:
            apppre = True
    elif _tpf.lower() == 'uri':
        # use the entry is not tpf provided
        _tpf = re.sub(r':.*$', '', entry[0])
        if _tpf in ('rfsys', 'lfsys', 'ldsys',):
            _tpf = 'fileuri'
        apppre = True
    elif _tpf.lower() == 'rfsys':
        if apppre:
            _tpf = 'fileuri'
        else:
            _tpf = 'share'

    tsep, pathsep, tpf, rte, _apre = gettpf(_tpf, apppre=apppre)  # @UnusedVariable

    if apppre:  # URI scheme allways uses a slash
        tsep = '/'

    if entry[0]:  # URI/URL
        if tpf == 'posix':
            if apppre:
                res = 'file://'
            else:
                res += ''
            tsep = '/'
            if entry[1]:
                if not res:
                    res = '//'
                res += entry[1]
            if entry[2]:
                if entry[0] == 'ldsys' and not apppre:
                    res += entry[2]
                else:
                    res += tsep + entry[2]
            if entry[3]:
                res += entry[3]

        elif tpf in ('win'):
            if apppre:
                res = 'file://'
                tsep = '/'
            else:
                res += ''
            if entry[1]:
                if not res:
                    res = '\\\\'
                res += entry[1]
            if entry[2]:
                if entry[0] == 'ldsys' and not apppre:
                    res += entry[2]
                else:
                    res += tsep + entry[2]
            if entry[3]:
                res += entry[3]

        elif tpf == 'unc':
            if apppre:
                res = 'file://///'
                tsep = '/'
            else:
                res += 2 * tsep
            if entry[1]:
                res += entry[1]
            if entry[2]:
                res += tsep + entry[2]
            if entry[3]:
                res += entry[3]

        elif rte == RTE_SMB:
            res = r'smb://'
            tsep = '/'
            if entry[1]:
                res += entry[1]
            if entry[2]:
                res += tsep + entry[2]
            if entry[3]:
                res += entry[3]

        elif tpf == 'cifs':
            res = r'cifs://'
            tsep = '/'
            if entry[1]:
                res += entry[1]
            if entry[2]:
                res += tsep + entry[2]
            if entry[3]:
                res += entry[3]

        elif tpf in ('https', 'http',):
            res = tpf + '://'
            tsep = '/'
            if entry[1]:
                res += entry[1]
            # entry 2 is share padding for path position comaptibility
            if entry[3]:
                res += entry[3]
            try:
                if entry[4]:
                    if entry[4][0] == '?':
                        res += entry[4]
                    else:
                        res += '?' + entry[4]
            except IndexError:
                pass

        elif tpf == 'ftp':
            res = 'ftp://'
            tsep = '/'
            if entry[1]:
                res += entry[1]
            if entry[2]:
                if entry[2][0] is not '/':
                    res += '/' + entry[2]
                else:
                    res += entry[2]
            if entry[3]:
                res += '?' + entry[3]

        elif rte in (RTE_FILEURI4, RTE_FILEURI5,):
            if rte == RTE_FILEURI4:
                res = 'file:////'
            elif rte == RTE_FILEURI5:
                res = 'file://///'

            tsep = '/'
            if entry[1]:
                res += entry[1]
            if entry[2]:
                res += tsep + entry[2]
            if entry[3]:
                res += entry[3]

        elif rte == RTE_FILEURI0:
            res = 'file:'
            tsep = '/'
            if entry[1]:
                raise PathError(
                    "minimal representation does not support remote files systems"
                    + str(entry[1])
                    )
            if entry[2]:
                if not re.match(r'[a-zA-Z]:', entry[2]):
                    raise PathError(
                        "minimal representation does not shares: "
                        + str(entry[2])
                        )
            if entry[3]:
                res += entry[3]

        elif tpf == 'file':
            res = 'file://'
            tsep = '/'

            if entry[1]:
                res += entry[1]
            if entry[2]:
                res += tsep + entry[2]
            if entry[3]:
                res += entry[3]


        elif tpf == 'share':
            if apppre:
                if (rte & 255 | RTE_URI) == RTE_FILEURI0:
                    res = 'file://'  # minimal
                elif (rte & 255 | RTE_URI) == RTE_FILEURI4:
                    res = 'file:////'  # traditional
                #elif rte & 255 == RTE_FILEURI5 or rte & 255 == RTE_FILEURI:
                else:
                    res = 'file://///'  # extra slash

                tsep = '/'
            else:
                res = 2 * tsep
            if entry[1]:
                res += entry[1]
            if entry[2]:
                res += tsep + entry[2]
            if entry[3]:
                res += entry[3]

        elif tpf == 'rfsys':
            if apppre:
                res = r'file://'
            else:
                if tpf == 'win':
                    res = '\\\\'
                else:
                    res = '//'

            if entry[1]:
                res += entry[1]
            if entry[3]:
                res += entry[3]

        elif tpf == 'ldsys':
            if apppre:
                # RFC8089.E.2: URIs of the form "file:///c:/path/to/file" are already
                # supported by the "path-absolute" rule.
                res = 'file:///'
            res += entry[2] + entry[3]

        elif tpf == 'lfsys':
            if apppre:
                res = 'file://'
                tsep = '/'
            res += entry[3]

        elif entry[0].lower() == 'lfsys':
            if apppre:
                res = 'file://'
                tsep = '/'
            else:
                res = ''
            tsep = os.sep
            if entry[1] or entry[2]:
                raise PathError("local posix path requested: " + str(entry))
            res += entry[3]

        elif entry[0].lower() == 'ldsys':
            if apppre:
                # RFC8089.E.2: URIs of the form "file:///c:/path/to/file" are already
                # supported by the "path-absolute" rule.
                res = 'file:///'
            res += entry[2] + entry[3]

        elif entry[0].lower() == 'share':
            if apppre:
                if (rte & 255 | RTE_URI) == RTE_FILEURI0:
                    res = 'file://'  # minimal
                elif (rte & 255 | RTE_URI) == RTE_FILEURI4:
                    res = 'file:////'  # traditional
                #elif rte & 255 == RTE_FILEURI5 or rte & 255 == RTE_FILEURI:
                else:
                    res = 'file://///'  # extra slash

                tsep = '/'
            else:
                res = 2 * tsep
            if entry[1]:
                res += entry[1]
            if entry[2]:
                res += tsep + entry[2]
            if entry[3]:
                res += entry[3]

        elif entry[0].lower() == 'rfsys':
            if apppre:
                res = r'file://'
            else:
                if tpf == 'win':
                    res = '\\\\'
                else:
                    res = '//'

            if entry[1]:
                res += entry[1]
            if entry[3]:
                res += entry[3]

        else:  # generic URI/URL
            tsep = gettpf(tpf)[0]
            ret = ''
            ret += entry[0] + "://"
            if entry[1]:
                ret += entry[1]
            if entry[3]:
                if entry[3][0] == '/':
                    ret += entry[3]
                else:
                    ret += "/" + entry[3]
            if entry[4]:
                if entry[4][0] == '?':
                    ret += entry[4]
                else:
                    ret += "?" + entry[4]
            return ret

    else:  # s.th. else - generic local path
        if entry[2]:
            res += 2 * tsep + entry[2]
        if entry[3]:
            res += entry[3]

    return res


def normapppathx(spath, **kargs):
    """Generic extention of *normpathx()* by application schemes and search path syntax.

    Args:
        **spath**:
            Accepts path, or search-path.

        kargs:
            Supports the parameters of :ref:`splitapppathx() <def_splitapppathx>`

            **apppre**:
                Application scheme.

            **appsplit**:
                Split into scheme and components of an application path.

            **spf**:
                Source platform.

            **tpf**:
                Target platform.

    Returns:
        Normalized path or search-path.

    Raises:
        pass-through: see :ref:`splitapppathx() <def_splitapppathx>`

    """
    kargs['raw'] = False
    # is default: kargs['normpathx'] = True
    apppre = kargs.get('apppre')

    if kargs.get('appsplit'):
        return splitapppathx(spath, **kargs)

    res = []

    for apx in splitapppathx(spath, **kargs):
        if type(apx) in ISSTR:
            res.append(apx)
        else:
            res.append(join_apppathx_entry(apx, **kargs))


    _tpf = kargs.get('tpf')
    if _tpf:
        _tsep, _tpsep, _tpf, _t, _apre = gettpf(_tpf, apppre=apppre)
    else:
        _tsep, _tpsep, _tpf, _t, _apre = gettpf(_tpf, apppre=apppre)
    return _tpsep.join(res)

def set_uppertree_searchpath(start=None, top=None, plist=None, **kargs):
    """Prepends each directory path from from 'start' on upward to 'top'
    in-place into *plist*. For example: ::

       start :=  /my/top/a/b/c
       top   :=  /my/top

    results in: ::

       plist := [
          '/my/top/a/b/c',
          '/my/top/a/b',
          '/my/top/a',
          '/my/top',
       ]

    Args:
        **start**:
            Start components of a path string.
            See common options for details.
            Valid scope types:

                * literal : X
                * re      : -
                * blob    : -

            default := caller-file-position.

        **top**:
            End component of a path string.
            The node 'top' is included.
            Valid scope types:

                * literal : X
                * re      : -
                * blob    : -

            default := <same-as-start>

        **plist**:
            List to for the storage.
            See common options for details.

            default := sys.path

        kargs:
            **append**:
                Appends the set of search paths.

            **matchidx**:
                Ignore matches '< #idx',
                adds match '== #idx' and returns.

                   matchidx := #idx

                default := 0 # all

            **matchcnt**:
                The maximal number of matches
                returned when multiple occur. ::

                   matchcnt=#num:

            **matchlvl**:
                Increment of match for top node when
                multiple are in the path. ::

                   matchlvl := #num:

                See common options for details.

            **matchlvlbackward**:
                Increment of match for top node when
                multiple are in the path. ::

                   matchlvlbackward := #num:

                See common options for details.

            **noTypeCheck**:
                Suppress required identical types of 'top' and
                'start'. As a rule of thumb for current
                version, the search component has to be less
                restrictive typed than the searched.
                The default applicable type matches are::

                     top    ¦ start
                    --------+---------------------
                     lfsys  ¦ lfsys, ldsys, share
                            | smb, cifs,
                     ldsys  ¦ ldsys
                     share  ¦ share
                     smb    ¦ smb
                     cifs   ¦ cifs
                     http   ¦ http, https
                     https  ¦ https, http

                See common options for details.

            **prepend**:
                Prepends the set of search paths.
                This is default.

            **raw**:
                Suppress normalization by call of
                'os.path.normpath'.

            **relonly**:
                The paths are inserted relative to the
                top node only. This is mainly for test
                purposes. The intermix of relative and
                absolute path entries is not verified.

            **reverse**:
                This reverses the resulting search order
                 from bottom-up to top-down.

            **unique**:
                Insert non-present only, else present
                entries are not checked, thus the search order
                is changed in general for 'prepend', while
                for 'append' the present still covers the new
                entry.

    Returns:
        When successful returns 'True', else returns either 'False',
        or raises an exception.

    Raises:
        AppPathError

        pass-through
    """
    if plist == None:
        plist = sys.path

    _relo = False
    _matchcnt = 0
    _matchidx = 0

    set_uppertree_searchpath._matchcnt = 0
    set_uppertree_searchpath._matchidx = 0

    matchlvl = 0
    matchlvlbackward = -1
    reverse = False
    unique = False
    prepend = True
    _tchk = True
    _raw = False
    _split = False
    _sitem = False

    for k, v in kargs.items():
        if k == 'relonly':
            _relo = True
        elif k == 'matchcnt':
            if not type(v) is int:
                raise AppPathError("Digits only matchcnt:" + str(v))
            _matchcnt = v
        elif k == 'matchidx':
            if not type(v) is int:
                raise AppPathError("Digits only matchidx:" + str(v))
            _matchidx = v
        elif k == 'matchlvl':
            if not type(v) is int:
                raise AppPathError("Digits only matchlvl:" + str(v))
            matchlvl = v
        elif k == 'matchlvlbackward':
            if not type(v) is int:
                raise AppPathError("Digits only matchlvlbackward:" + str(v))
            matchlvlbackward = v
        elif k == 'reverse':
            reverse = True
        elif k == 'unique':
            unique = True
        elif k == 'append':
            prepend = False
        elif k == 'prepend':
            prepend = True
        elif k == 'raw':
            _raw = True
        elif k == 'splitItems':
            _split = True
        elif k == 'singleitem':
            _sitem = True
        elif k == 'noTypeCheck':
            _tchk = False

    if matchlvl > 0:
        matchlvlbackward = -1

    # Prepare search path list
    # if decided to normalize, and whether to ignore leading '//'
    if _raw:  # match basically literally
        _plst = []
        for i in plist:
            # normalize
            _elems = splitapppathx(i, appsplit=True, **kargs)[0]
            _plst.append(splitapppathx_getlocalpath(_elems))

    else:  # normalize for safer match conditions
        _plst = []
        for i in plist:
            # normalize
            _elems = splitapppathx(i, appsplit=True, **kargs)[0]
            _plst.append(splitapppathx_getlocalpath(_elems))

    # 0. prep start dir
    if start == '':
        raise AppPathError("Empty start:''")
    elif start == None:
        start = getcaller_filepathname(2)  # caller file
    # normalize
    _start_elems = splitapppathx(start, appsplit=True, **kargs)[0]
    start = splitapppathx_getlocalpath(_start_elems)
    # try a literal
    if not os.path.isabs(start):
        start = getcaller_pathname(2) + os.sep + start
    if os.path.isfile(start):
        start = os.path.dirname(start)  # we need dir
    if not os.path.exists(start):
        raise AppPathError("Missing start:" + str(start))

    # 1. prep top dir

    # normalize
    if top == '':
        raise AppPathError("Empty top:''")
    elif top == None:
        top = getcaller_pathname(2)  # caller file

    # normalize
    _top_elems = list(splitapppathx(top, appsplit=True, **kargs)[0])

    # ptype
    if _tchk:
        if _top_elems and _start_elems:
            if _top_elems[0] != _start_elems[0]:

                # TODO: still to enhance..
                if _top_elems[0] in ('lfsys', ):
                    if os.path.realpath(_top_elems[3]):
                        pass
                    elif _start_elems[0] in (
                            'ldsys',
                            'lfsys', ):
                        pass
                    else:
                        raise AppPathError(
                            "'lfsys' combined with " + str(_start_elems[0]) +
                            " requires relative pathname for 'lfsys', given: "
                            + str(_top_elems[3]))
                    pass
                else:
                    raise AppPathError(
                        "This version requires compatible types: start(" +
                        str(_start_elems[0]) + ") =! top(" +
                        str(_top_elems[0]) + ")")

    top = splitapppathx_getlocalpath(_top_elems)

    # if absolute
    if os.path.isabs(top):
        if not os.path.exists(top):
            raise AppPathError("Top does not exist:" + str(top))

    def _addsub(x, pl=plist):
        """...same for all."""
        # >3: nonlocal _matchcnt
        if _matchcnt != 0 and _matchcnt <= set_uppertree_searchpath._matchcnt:
            return
        if _matchidx != 0 and _matchidx != set_uppertree_searchpath._matchidx:
            return

        if unique and x in pl or x in plist:
            return False
        if reverse:
            pl.append(x)
        else:
            pl.insert(0, x)
        set_uppertree_searchpath._matchcnt += 1
        pass

    # find top
    if top:
        if top == '.':
            top = os.path.abspath(top)

        # for now works with literal only
        stop = top
        if stop[0] != os.sep and stop[0] != start[0]:
            stop = os.sep + stop
        if stop[-1] != os.sep and stop[-1] != start[-1]:
            stop = stop + os.sep

        a = start.split(stop)

        if len(a) == 1 and top != start:
            raise AppPathError(
                "Top-node is not in search path:\n  top   = %s\n  start = %s" %
                (str(top), str(start)))

        if matchlvl >= len(a):  # check valid range
            raise AppPathError("Match count out of range:" + str(matchlvl)
                                   + ">" + str(len(a)))
        # check valid range
        elif matchlvlbackward > 0 and matchlvlbackward >= len(a):
            raise AppPathError("Match count out of range:" +
                                   str(matchlvlbackward) + ">" + str(len(a)))

    else:
        if matchlvl > 0:
            raise AppPathError("Match count out of range:" + str(matchlvl)
                                   + "> 0")
        if matchlvlbackward > 0:
            raise AppPathError("Match count out of range:" +
                                   str(matchlvlbackward) + "> 0")
        _addsub(start)
        return True

    #
    # so we have actually at least one top within valid range and a remaining sub-path - let us start
    #

    if a == ['', '']:  # top == start
        if matchlvl > 0:
            raise AppPathError("Match count out of range:" + str(matchlvl)
                                   + "> 0")
        if matchlvlbackward > 0:
            raise AppPathError("Match count out of range:" + str(matchlvl)
                                   + "> 0")
        _addsub(start)
        return True

    elif a[0] == '':  # top is prefix
        _tpath = top

        if matchlvlbackward >= 0:
            mcnt = len(a) - 1 - matchlvlbackward
        else:
            mcnt = matchlvl

        _spath = top.join(a[mcnt + 1:])  # sub-path for search recursion

    else:

        # get index for requested number of ignored/contained matches
        if matchlvlbackward >= 0:
            mcnt = len(a) - 1 - matchlvlbackward
        else:
            mcnt = matchlvl + 1

        # set matched prefix and postfix
        if os.path.isabs(top):
            _tpath = top
            # sub-path for search recursion
            _spath = (os.sep + top + os.sep).join(a[mcnt:])
        elif not a[mcnt - 1]:  # tail
            _tpath = (os.sep + top + os.sep).join(a[:mcnt])
            _spath = ''
        else:
            # top path as search hook
            _tpath = (os.sep + top + os.sep).join(a[:mcnt]) + os.sep + top
            # sub-path for search recursion
            _spath = (os.sep + top + os.sep).join(a[mcnt:])

    _tpath = os.path.normpath(_tpath)
    _spath = os.path.normpath(_spath)
    if not os.path.isabs(top) and os.path.isabs(_spath):
        _spath = _spath[1:]

    if _relo:  # relative paths, mainly for test
        curp = ''
    else:
        curp = os.path.normpath(_tpath)
        if curp not in plist:  # insert top itself
            _addsub(curp)

    a = _spath.split(os.sep)
    if prepend:
        for p in a:
            if not p:
                continue
            curp = os.path.join(curp, p)
            _addsub(curp)
    else:
        _buf = []
        for p in a:
            if not p:
                continue
            curp = os.path.join(curp, p)
            _addsub(curp, _buf)
        plist.extend(_buf)

    return True


def splitapppathx(spath, **kargs):
    """Splits PATH variables which may include URI type prefixes into
    a list of single path entries. The default behavior is to split
    a search path into a list of contained path entries. E.g::

       p = 'file:///a/b/c:/d/e::x/y:smb://host/share/q/w:http://host/a/b/:https://host/a?xy#123'

    Is split into: ::

            px = [
                'file:///a/b/c',
                'file://host/a/b/c',
                'file://///host/share/a/b/c',
                '/d/e',
                '',
                'x/y',
                'smb://host/share/q/w',
                '//host/share/q/w',
                'http://a/b/',
                'https://host/a?xy#123',
            ]

    With parameter '*appsplit*' set the paths entries are sub-split into their schemes
    and type specific items ::

            px = [
                ('lfsys',   '',      '',       '/a/b/c'),
                ('rfsys',   'host',  '',       '/a/b/c'),
                ('unc',     'host',  'share',  '/a/b/c'),
                ('lfsys',   '',      '',       '/d/e'),
                ('lfsys',   '',      '',       ''),
                ('lfsys',   '',      '',       'x/y'),
                ('smb',     'host',  'share',  'q/w'),
                ('share',   'host',  'share',  'q/w'),
                ('share',   'host',  'share',  'q/w'),

                ('http',    'host',   '',      '/a/b/',   ''),
                ('https',   'host',   '',      '/a',      'xy#123'),
            ]

    For reserved prefix keywords as parts of the name, these
    should be escaped.

    Args:
        **spath**:
            The search path to be split.

        kargs:
            The provided key-options are also transparently passed
            through to 'normpathx()' `[see] <paths.html#normpathx>`_ - if not 'raw'.

            **apppre**:
                Adds application prefix. ::

                    appsplit = (True|False)

                default := False

            **appsplit**:
                Splits into tuples of application entries. ::

                    appsplit = (True|False)

                default := False

                For example: ::

                   file:///my/path/a

                results for *True* in: ::

                   (lfsys, '', '', '/my/path/a')

            **delnulpsep**:
                Delete empty search paths.

                default := True

            **escape**:
                Escapes backslash.

                default := False

            **keepsep**:
                Modifies the behavior of 'strip' parameter.
                If 'False', the trailing separator is dropped. ::

                   splitapppathx('/a/b', keepsep=False)   => ('', 'a', 'b')
                   splitapppathx('/a/b/', keepsep=False)  => ('', 'a', 'b')

                for 'True' trailing separators are kept as directory
                marker::

                   splitapppathx('/a/b', keepsep=True)    => ('', 'a', 'b')
                   splitapppathx('/a/b/', keepsep=True)   => ('', 'a', 'b', '')

                default := False # for URIs except file://, smb://
                default := True  # for file path names

            **normpathx**:
                Calls *normapthx()* on path-part. ::

                   normpathx := (
                        True   # call normpathx
                      | False  # do not normalize
                   )

                default := True


            **pathsep**:
                Replaces path separator set by the *spf*, e.g. for a URI
                pathlist from an alternate platform. The resulting path
                separator selects the type of the scanner *APPPATHSCANNER*. ::

                    pathsep := (';' | ':')

            **raw**:
                Displays a list of unaltered split path items, superposes 'rpath'
                and 'rtype'. ::

                    raw = (True|False)

                default := False

            **rpath**:
                Displays the path as provided raw sub string.

                For further details refer to 'splitapppathx'
                `[see] <#split-appprefix>`_. ::

                    rpath = (True|False)

            **rtype**:
                Displays the type prefix as provided raw sub string.

                For further details refer to 'splitapppathx'
                `[see] <#split-appprefix>`_. ::

                    rtype = (True|False)

            **spf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.getspf() <paths.html#getspf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.

            **strict**:
                Validates for the target OS/FS, throws exception when invalid
                characters are contained.

            **strip**:
                Strips null-entries.

                default := True

            **tpf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to the API in the manual at :ref:`tpf <OPTS_TPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.gettpf() <paths.html#gettpf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.

            **unescape**:
                Unescapes backslash.

                default := False

    Returns:
        When split successful returns a list of tuples: ::

            appsplit == False

                [
                    <pathvar-item>,
                    ...
                ]

            appsplit == True

                [
                    (TYPE, host-name, share-name, pathname),
                    ...
                ]

        The tuple contains: ::

            (TYPE, host-name, share-name, pathname)

              TYPE := (raw|cifs|smb|share|http|https|lfsys|rfsys|ldsys)
                 raw := (<raw-pathvar-item>)
                 cifs := ('cifs://')
                 smb := ('smb://')
                 share := ('file:///'+2SEP|'file://'+2SEP|2SEP)
                 rfsys := ('file://')
                 lfsys := ('file://'|'')
                 ldsys := [a-z]':'

                 http := ('http://')
                 https := ('http://')

              host-name := (host-name|'')
              share-name := (valid-share-name|'')
              valid-share-name := (
                 smb-share-name
                 | cifs-share-name
                 | win-drive-share-name
                 | win-drive-os
                 | win-special-share-name
              )
              pathname := "pathname on target"

            specials:

               raw := ('raw', '', '', raw-pathvar-item)
               rpath := (TYPE, host-name, share-name, raw-pathname)
               rtype := (raw-type, host-name, share-name, pathname)
               rtype + rpath := (raw-type, host-name, share-name, raw-pathname)

        For compatibility the URI for http/https adds one item
        'query+fragment', while the share remains empty. ::

           ('http' | 'https') := (TYPE, host-name, '', pathname, query+fragment)

        else: ::

           ('lfsys', '', '', apstr)

        **REMARK**:
            The hostname may contain in current release
            any suboption, but is not tested with options at all.

    Raises:
        PathError

        passed-through

    """
    _delnulpsep = kargs.get('delnulpsep', True)  #: remove resulting empty entries
    _normpathx = kargs.get('normpathx', True)  # : calls normapthx() on path-part
    apppre = kargs.get('apppre', False)
    appsplit = kargs.get('appsplit', False)  # : control application tuples, else ordinary path
    raw = kargs.get('raw', False)  # : control raw
    rpath = kargs.get('rpath', False)  # : control RAW-PATH
    rtype = kargs.get('rtype', False)  # : control RAW-TYPE
    strict = kargs.get('strict', False)  # : validate and raise if not valid

    # platform path types

    #
    # the source platform - selects the type of the scanner - APPPATHSCANNER,
    # thus has to be defined here - independent from the actual input data
    # the inpur of platform independent types is handled correctly on each platform anyway, e.g. URI
    spf = kargs.get('spf', '')  # : control input domain - has precedence for apppathx parser selection
    ssep, pathsep, _spf, _input = getspf(spf)  # @UnusedVariable
    pathsep = kargs.get('pathsep', pathsep)  # alter when provided

    #
    # the target platform - delayed for the default to keep the tpe of platform


    _tpf_each = False  #: set tpf for each in mixed search path


    #
    # set parser for apppathx - the pathsep is actually the only difference
    #
    if pathsep[0] is ':':
        _appparser = APPPATHSCANNER_COL

    elif pathsep[0] is ';':
        _appparser = APPPATHSCANNER_SEM

    else:
        # should never occur - for now going ahead...
        if RTE & RTE_WIN32:
            _appparser = APPPATHSCANNER_SEM
        else:
            _appparser = APPPATHSCANNER_COL

    ret = []  # : collect result
    g = 0  # : preserve for final analysis outside the loop

    def getraw(i, g):
        """Get raw string.

        Args:
            i: iterator
            g: current group

        Returns:
            (s,e): for sub string
        """
        # get start string position without APP-PREFIX
        s = i.start(g + 1)
        if s == -1:
            s = i.start(g + 2)
            if s == -1:
                s = i.start(g + 3)

        # get end string position
        e = i.end(g + 3)
        if e == -1:
            e = i.end(g + 2)
            if e == -1:
                e = i.end(g + 1)

        return (
            s,
            e, )

    def _validate(plst):
        for x in plst:
            if _output & RTE_POSIX:
                if INVALIDCHARSPOSIX.search(x):
                    raise PathError(
                        """rte=%s - target-platform:RTE_POSIX(%s) - invalid tpf char(\\0) = '%s'""" % (
                            str(num2rte.get(RTE)),
                            str(num2rte.get(_output, _output)),
                            str(x))
                        )
            elif _output & RTE_WIN32:
                if INVALIDCHARSWIN.search(x):
                    raise PathError(
                        """rte=%s - target-platform:RTE_WIN32(%s) - invalid tpf char(:<>*?) = '%s'""" % (
                            str(num2rte.get(RTE)),
                            str(num2rte.get(_output, _output)),
                            str(x))
                        )
            elif _output & RTE_GENERIC and INVALIDCHARS.search(x):
                raise PathError(
                    """rte=%s - target-platform:RTE_GENERIC(%s) - invalid tpf char(:<>*?\\0) = '%s'""" % (
                        str(num2rte.get(RTE)),
                        str(num2rte.get(_output, _output)),
                        str(x))
                    )

            # else: let the OS decide...

    if not spath:  # shortcut for empty _input - None and 0/length-string
        if not appsplit:
            return []
        if raw:
            return [('raw', '', '', '')]
        if rtype or (rpath and rtype):
            return [('', '', '', '')]
        else:
            return [('lfsys', '', '', '')]

    # APPPATHSCANNER_COL APPPATHSCANNER_SEM
    for i in _appparser.finditer(spath):
        for g in APPPATHINDEX:  # do this for getting the syntax term
            _cur = None

            if i.start(g) == -1:  # if there is a match at all
                continue

            if g == 92:  # EMPTY: shortcut for empty group == empty path entry
                if raw:  # raw prio higher
                    _cur = ('raw', '', '', '')
                elif rtype or (rpath and rtype):
                    _cur = ('', '', '', '')
                # elif rpath:
                else:
                    _cur = ('lfsys', '', '', '')

                ret.append(_cur)
                break

            elif i.group(g + 3) or i.group(g):  # 4:local file system / 0:uri or IEEE/UNC/SMB
                if raw:
                    # _cur = ('raw', '', '', pathvar[i.start(g):i.end(g + 3)])
                    ret.append(('raw', '', '',
                                spath[i.start(g):i.end(g + 3)]))
                    break
                elif rtype and rpath or rtype:

                    if g is 52:
                        # **uri**

                        _cur = [i.group(g), i.group(g + 1), '', i.group(g + 2),
                            i.group(g + 3)]

                        #check registered
                        try:
                            _cur[0] = APPTYPES_L2[i.group(g)][0]
                        except KeyError:
                            # non-registered
                            raise FileSysObjectsError("URI not supported: " + str(i.group(g)))

                        if not _cur[-1]:
                            _cur[-1] = ''

                    else:
                        _cur = (i.group(g), i.group(g + 1), i.group(g + 2),
                            i.group(g + 3))

                # elif rpath:
                else:
                    _cur = ['', i.group(g + 1), i.group(g + 2), i.group(g + 3)]

                    if g is 36:
                        # **smb**

                        _cur[0] = APPTYPES_L2.get(
                            i.group(g), APPTYPES[int((g - 4) / 8)])[0]

                    elif g is 52:
                        # **uri**

                        #check registered
                        try:
                            _cur[0] = APPTYPES_L2[i.group(g)][0]
                        except KeyError:
                            # non-registered
                            raise FileSysObjectsError("URI not supported: " + str(i.group(g)))

                        #_cur[0] = re.sub(r':/*', '', i.group(g))

                        _cur.insert(2, '')  # dummy-share for compatibility of path position, extends 1 field

                        if not _cur[-1]:
                            _cur[-1] = ''
                    else:
                        _cur[0] = APPTYPES[int((g - 4) / 8)]

                    _cur = tuple(_cur)

            elif i.group(g + 2):  # 2:DOS-SC_DRIVE - only
                if raw:
                    # _cur = ('raw', '', '', pathvar[i.start(g):i.start(g + 3)])
                    ret.append(('raw', '', '',
                                spath[i.start(g):i.start(g + 3)]))
                    break
                elif rtype and rpath or rtype:
                    _cur = (i.group(g), i.group(g + 1), i.group(g + 2), '')
                else:
                    if g is 36:
                        # **smb**
                        _a = APPTYPES_L2.get(i.group(g), APPTYPES[int((g - 4) / 8)])
                    else:
                        _a = APPTYPES[int((g - 4) / 8)]
                    _cur = (_a, i.group(g + 1), i.group(g + 2), '')

            elif not i.group(g + 1):  # here: 0,1,2,3 => empty group
                _cur = ('lfsys', '', '', '')

            else:
                continue  # should not occur, anyhow...

            #
            # post processing on prepared match - includes the processing of the path
            #
            if _cur:
                gsepback = ''
                if i.start(g) > 0:  # look back
                    gsepback = i.string[i.start(g) - 1]

                if _input & RTE_POSIX and not _input & RTE_WIN32 \
                        and g in (60, 68, 76):  # DOSDRIVE
                    # Posix: ignore drives and uses 'colon' as separator

                    if raw:
                        ret.append(('raw', '', '', _cur[2] + _cur[3]))
                    elif pathsep == ";":
                        # selected by option 'pathsep'
                        # anyhow, posix does not know anything about drives
                        ret.append(('lfsys', '', '', _cur[2] + _cur[3]))
                    else:
                        # treat drive as path
                        ret.append(('lfsys', '', '', _cur[-2][0]))
                        # treat path on drive still as path
                        ret.append(('lfsys', '', '', _cur[-1]))

                elif _input & (RTE_POSIX | RTE_WIN32) == (RTE_POSIX
                                                          | RTE_WIN32):
                    # both: Posix and Win, reserved sep and pathsep for both,
                    # app-tags are still valid
                    ret.append(_cur)

                elif _input & RTE_GENERIC:
                    # simple character split, but keeps app-URIs

                    if g in (60, 68, 76):  # DOSDRIVE - ignores DOS drives
                        if not gsepback or gsepback in pathsep:  # first or prefix-sep
                            ret.append(('lfsys', '', '', _cur[-2][0]))

                        elif gsepback not in pathsep:  # have s.th. to concat
                            ret[-1] = list(ret[-1])
                            ret[-1][-1] += gsepback + _cur[-2][0]
                            ret[-1] = tuple(list(ret[-1]))

                        if ':' not in pathsep:
                            # append path too

                            # TODO: speedup
                            ret[-1] = list(ret[-1])
                            ret[-1][-1] += ':' + _cur[-1]
                            ret[-1] = tuple(list(ret[-1]))

                        else:  # treat path on drive still as path
                            ret.append(('lfsys', '', '', _cur[-1]))
                    else:
                        ret.append(_cur)

                elif gsepback:
                    if gsepback in pathsep:
                        ret.append(_cur)
                    else:
                        if _cur[3]:
                            ret[-1] = list(ret[-1])
                            kargs['apppre'] = apppre
                            ret[-1][-1] += gsepback + \
                                join_apppathx_entry(
                                    _cur, **kargs)
                            ret[-1] = tuple(list(ret[-1]))
                else:
                    ret.append(_cur)

                if ret:

                    #
                    # the target platform - delayed for the default to keep the tpe of platform
                    tpf = kargs.get('tpf', False)
                    if not tpf or _tpf_each:
                        _tpf_each = True
                        # if none provided, just keep the final input platform
                        tpf = re.sub(r':.*$', '', ret[-1][0])
                    tsep, tpsep, _tpf, _output, _apre = gettpf(tpf, apppre=apppre)  # @UnusedVariable
                    kargs['tpf'] = _output

                    if g == 52:
                        #
                        # *** URI
                        #
                        if not os.path.isabs(ret[-1][3]):
                            raise FileSysObjectsError("requires absolute path, got: " + str(ret[-1][3]))

                        kargs['apppre'] = False
                        kargs['keepsep'] = kargs.get('keepsep', True)
                        if kargs.get('strip', True):
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2], normpathx(
                                ret[-1][3], **kargs), ret[-1][4])

                        if kargs.get('escape'):
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2], escapepathx(
                                ret[-1][3], **kargs), ret[-1][4])
                        elif kargs.get('unescape'):
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2], unescapepathx(
                                ret[-1][3], **kargs), ret[-1][4])

                        if strict:  # validate
                            # app should be inherently by re
                            _validate(_cur[-2])

                    elif g in (
                            4, 12, 20, 28,   #: file-URI,
                            ):
                        #
                        #*** file-URI
                        #

                        # now correct the temporary spf assignment
                        # supports by default FILEURI5 and FILEURI,
                        # when required else the parameters 'spf'
                        # and 'tpf' has to be used
                        if not kargs.get('spf'):
                            if g == 4:
                                spf = RTE_FILEURI5
                                ssep, pathsep, _spf, _input = getspf(spf)  # @UnusedVariable
                            else:
                                spf = RTE_FILEURI
                                ssep, pathsep, _spf, _input = getspf(spf)  # @UnusedVariable

                        if kargs.get('apppre'):
                            # create applicationscheme, thus uri with shlashes only
                            _tpf_old = kargs.get('tpf')
                            if _output & RTE_URI:
                                # concrete type of file-uri
                                kargs['tpf'] = _output
                                kargs['apppre'] = False
                            else:
                                # generic standard URI
                                kargs['tpf'] = RTE_URI
                                kargs['apppre'] = False

                        elif kargs.get('tpf'):
                            # a tpf provided
                            _tpf_old = None
                            pass

                        else:
                            # no tpf provided
                            _tpf_old = None
                            kargs['tpf'] = RTE

                        if _normpathx:
                            if ret[-1][3][:2] in (
                                    '//',
                                    '\\\\', ) and (ret[-1][1] or ret[-1][2]):
                                _np = normpathx(ret[-1][3][1:], **kargs)

                            else:
                                _np = normpathx(ret[-1][3], **kargs)
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2], _np)

                        if kargs.get('escape'):
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2],
                                       escapepathx(ret[-1][3], **kargs))
                        elif kargs.get('unescape'):
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2],
                                       unescapepathx(ret[-1][3], **kargs))

                        if strict:  # validate
                            # app should be inherently by re
                            _validate(_cur[-1])

                        if _tpf_old:
                            kargs['tpf'] = _tpf_old

                    elif g in (
                            36,              #: TODO: implement complete spec. SMB/CIFS
                            ):
                        #
                        #*** file-URI, SMB/CIFS
                        #
                        if kargs.get('apppre'):
                            # create applicationscheme, thus uri with shlashes only
                            _tpf_old = kargs.get('tpf')
                            kargs['tpf'] = 'uri'
                            kargs['apppre'] = False

                        elif kargs.get('tpf'):
                            # a tpf provided
                            _tpf_old = kargs['tpf']
                            kargs['tpf'] = 'uri'
                            pass

                        else:
                            # no tpf provided
                            _tpf_old = None
                            kargs['tpf'] = RTE

                        if _normpathx:
                            if ret[-1][3][:2] in (
                                    '//',
                                    '\\\\', ) and (ret[-1][1] or ret[-1][2]):
                                _np = normpathx(ret[-1][3][1:], **kargs)

                            else:
                                _np = normpathx(ret[-1][3], **kargs)
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2], _np)

                        if kargs.get('escape'):
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2],
                                       escapepathx(ret[-1][3], **kargs))
                        elif kargs.get('unescape'):
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2],
                                       unescapepathx(ret[-1][3], **kargs))

                        if strict:  # validate
                            # app should be inherently by re
                            _validate(_cur[-1])

                        if _tpf_old:
                            kargs['tpf'] = _tpf_old
                    else:
                        if _normpathx:
                            if ret[-1][3][:2] in (
                                    '//',
                                    '\\\\', ) and (ret[-1][1] or ret[-1][2]):
                                # network share UNC/POSIX-app
                                _np = normpathx(ret[-1][3][1:], **kargs)
                            else:
                                # source is ordinary local file
                                _np = normpathx(ret[-1][3], **kargs)

                            # simpler than genric check and query for drive+path
                            if (
                                    kargs['tpf'] in (RTE_CNW, RTE_CNP, RTE_LOCAL)
                                    and _np == '.'
                                    and ret[-1][2]
                                ):
                                _np = ''

                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2], _np)

                        if kargs.get('escape'):
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2],
                                       escapepathx(ret[-1][3], **kargs))
                        elif kargs.get('unescape'):
                            ret[-1] = (ret[-1][0], ret[-1][1], ret[-1][2],
                                       unescapepathx(ret[-1][3], **kargs))

                        if strict:  # validate
                            # app should be inherently by re
                            _validate(_cur[-1])

                break

        if apppre and ret[-1][3][0] not in ('/', '\\'):
            raise PathError("requires absolute path, got: " + str(ret[-1][3]))

        if _delnulpsep and ret:
            for l in reversed(ret):
                if l[-1] or l[-2]:
                    break
                ret.pop()

    #* the case empty group regexpr at the end of the search path else complicates the regexpr at all
    # empty group at the end of string
    if not _delnulpsep and i.end(g - 1) < len(
            i.string) and i.string[-1] in pathsep:
        if raw:
            ret.append(('raw', '', '', ''))
        elif rtype:
            ret.append(('', '', '', ''))
        else:
            ret.append(('lfsys', '', '', ''))

    if not _tpf_each:
        _tpfin = kargs.get('tpf', False)
        if _tpfin:
            tsep, tpsep, _tpf, _output, _apre = gettpf(_tpfin, apppre=apppre)  # @UnusedVariable

    if not appsplit:  # ordinary pathsplit
        _ret = []
        if raw:
            _ret = map(lambda x: x[3], ret)
        else:  # expects 'rtype', and valid entries
            for r in ret:
                if not os.path.abspath(r[3]):
                    raise FileSysObjectsError("requires absolute path, got: " + str(r[3]))

                if _tpf_each:
                    tsep, tpsep, _tpf, _output, _apre = gettpf(r[0], apppre=apppre)  # @UnusedVariable
                _ret.append(join_apppathx_entry(r, tpf=_output, apppre=apppre))
        return _ret

    return ret


def splitapppathx_getlocalpath(elems, **kargs):
    """Joins application elements to a path for local access.

    Args:
        **elems**:
            Elements as provided by 'splitapppathx'

        kargs:
            **tpf**:
                Target platform for the file pathname, for details refer to
                :ref:`normpathx() <def_normpathx>`.

    Returns:
        When successful the local access path, else None.

    Raises:
        AppPathError
        passed through exceptions
    """
    _tpf = kargs.get('tpf', False)
    if _tpf in (
            'Windows',
            'win', ):
        s = '\\'
    elif _tpf == 'posix':
        s = '/'
    else:
        s = os.sep

    ret = ''

    if not elems or type(elems) not in (
            tuple,
            list, ) or len(elems) < 4:
        raise FileSysObjectsError('Incompatible input:' + str(elems))

    if elems[1]:
        if not elems[2]:
            if RTE & RTE_WIN32 and elems[0].upper() not in ('smb', 'share'):
                raise AppPathError("Missing share name for start=" +
                                       str(elems))
        ret += 2 * s + elems[1]

    if elems and len(elems) > 1:
        if elems[1]:
            ret += s + elems[2]
        else:
            ret += elems[2]

    if elems and ret:
        if (elems[1] or elems[2]) and elems[3][0] not in ('/', '\\', os.sep):
            ret += s + elems[3]
        else:
            ret += elems[3]
    elif elems:
        ret += elems[3]

    return ret


def gettop_from_pathstring(spath, plist=None, **kargs):
    """Searches for a partial path *spath* in a list of
    search paths *plist*. The current version supports for
    pure in-memory evaluation of literals and regexpr.

    The following example of input with default parameters ::

       spath := 'a/b/c'
       plist := [
          '/my/path/a/c/x/y/a/b/x/d/e/r',
          '/my/path/a/c/x/y/a/b/c/d/e/r',
       ]

    results in the first match: ::

       result := '/my/path/a/c/x/y/a/b/c'
       #
       # shortes top-match: '/my/path/a/c/x/y/' + 'a/b/c'
       #

    Same for a regular expression: ::

       spath := 'a/.*/[cxy]/[def]{1}'

    results again in: ::

       result := '/my/path/a/c/x/y/a/b/c'

    The match is performed by the re module based on *re.split*
    spanning multiple directories in case of reguar expressions.
    Thus the expressions require some caution when constraints
    are required. The function itself serves as a framework
    providing parameterization of the match criteria.

    Args:
        **spath**:
            A path to be appended to an item from 'plist'.

        **plist**:
            List of search strings to be extended
            by the subpath *spath*.

            default := sys.path

        kargs:
            **hook**:
                Returns the insertion point of *spath* without
                the *spath* itself.

            **keepsep**:
                Keeps significant separators, e.g. a trailing 'os.sep'.

                default := True

            **matchidx**:
                Use the n-th match of the resulting path component only.
                The path component excludes the authority and share for
                network paths. ::

                   matchidx := #idx:

                   0 <= idx   ; first match

                * Ignore matches for '*< #idx*'
                * return match for '*== #idx*', and stop search

                default := 0 # first match

                Depends on *reverse*.

            **pathsep**:
                Replaces the path separator set by the *spf*. ::

                    pathsep := (';' | ':')

            **pattern**:
                Sets and activates scope and type of match pattern.
                The pattern is matched node-by-node for each
                corresponding directory level: ::

                   pattern := (literal | regexpr)

                * *literal*:

                  Match literally. Pattern are treated as characters.

                * *regexpr*:

                  Match regular expression for individual nodes,
                  implies no contained reserved characters of the
                  current file system, so 'os.sep' and no 'os.pathsep'.

                default := literal

            **raw**:
                Suppress normalization by call of
                'os.path.normpath'.

            **reverse**:
                This reverses the resulting search order
                from bottom-up to top-down. Takes effect on
                'redundant' only.

            **split**:
                Returns the path prefix matched on the search list,
                and the relative sub path outside the search list
                as a tuple. ::

                   split := (True | False)

                For example the input: ::

                   spath := 'a/b/c'
                   plist := [
                      '/my/path/a/c/x/y/a/b/x/d/e/r',
                      '/my/path/a/c/x/y/a/b/c/d/e/r',
                   ]

                results in: ::

                   result := ('/my/path/a/c/x/y', 'a/b/c')

            **spf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.getspf() <paths.html#getspf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.

            **strip**:
                Strips null-entries.

                default := True

            **tpf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to the API in the manual at :ref:`tpf <OPTS_TPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.gettpf() <paths.html#gettpf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.


    Returns:
        When successful returns by default the expanded pathname, else None.
        The return value in case of success depends on the parameters:

        * if *split == True*: returns a *tuple* ::

             result = (result[0], result[1],)

          result[0]: The matched path including the resolved searched sub-path *spath*.

          result[1]: The remainder.

        * if *split == True* and *hook == True*: returns a *tuple* ::

             result = (result[0], result[1], result[2],)

          result[0]: The matched path excluding the sub-path *spath*.

          result[1]: The resolved searched sub-path *spath*.

          result[2]: The remainder.

        * else: returns an *str* ::

             result = <str>

          * if *hook == True*:

            The matched path excluding the sub-path *spath* and an
            evtl. present remainder.

          * else:

            A string of the matched path including the resolved
            searched sub-path *spath*, excluding an evtl. present
            remainder.

    Raises:
        AppPathError

        FileSysObjectsError

        passed-through

    """
    if plist == None:
        plist = sys.path
    elif type(plist) != list:
        raise AppPathError("Requires list argument:" + str(plist))

    try:
        _hook = kargs.pop('hook')
    except KeyError:
        _hook = False
    try:
        _rev = kargs.pop('reverse')
    except KeyError:
        _rev = False
    try:
        _split = kargs.pop('split')
    except KeyError:
        _split = False
    try:
        _strip = kargs['strip']
    except KeyError:
        _strip = False

    try:
        matchidx = kargs.pop('matchidx')
        if not type(matchidx) is int or matchidx < 0:
            raise AppPathError("Requires int>0 matchidx=" + str(matchidx))
    except KeyError:
        matchidx = 1

    try:
        _pat = kargs.pop('pattern')
        if _pat == 'regexpr':
            _pat = 1
        #
        # reminder: glob not supported for current release, requires an offline interpreter
        # elif v == 'glob':
        #     _pat = 2
        elif _pat == 'literal':
            _pat = 0
        else:
            raise FileSysObjectsError("gettop_from_pathstring:parameter not supported: pattern = " + str(_pat))
    except KeyError:
        _pat = 0

    raw = kargs.get('raw', False)
    _keepsep = kargs.get('keepsep', True)

    #
    # get spf
    #
    _spf = kargs.get('spf', False)
    ssep, spsep, _spf, _input = getspf(_spf)  # @UnusedVariable
    # pathsep = kargs.get('pathsep', spsep)

    #
    # get tpf
    #
    _tpf = kargs.get('tpf', False)
    tsep, tpsep, _tpf, _output, _apre = gettpf(_tpf)  # @UnusedVariable


    def _comp(p, b):
        """match regexpr
        p: regexpr
        b: item plist[i][j]
        """
        if _pat == 1: # regexpr
            if p == '*':  # assume a glob expression, thus terminate 're' processing now
                return
            pc = re.compile(r'^' + p + r'$')
            px = pc.match(b)
            if px:
                return px.string[px.start():px.end()]

        elif _pat == 0:  # literal
            if p == b:
                return b

    # define processed portion, save prefix for later prepend on result
    if not raw:
        # For *spath*, is relative thus cannot be http/https
        #
        #   _rtype   type
        #   _host:   host
        #   _share:  share
        #   sp:      local path
        #
        _rtype, _host, _share, sp = splitapppathx(
            spath, appsplit=True, spf=_spf, tpf=_tpf, rtype=True,
            keepsep=_keepsep, strip=_strip)[0]
        _app_prefix = _rtype + _host
        if _share:
            if _app_prefix:
                _app_prefix += ssep + _share
            else:
                _app_prefix = _share

    else:
        _app_prefix, sp = '', spath

    # normalize search path
    #
    # For *spath*
    #
    #   _sp_elems[0]   type
    #   _sp_elems[1]:  host
    #   _sp_elems[2]:  share
    #   _sp_elems[3]:  local path
    #
    kargs['keepsep'] =  _keepsep
    _sp_elems = splitapppathx(sp, appsplit=True, **kargs)[0]
    sp = splitapppathx_getlocalpath(_sp_elems, tpf=_tpf)
    sp_tmp = sp


    sp = sp.split(ssep)
    if sp and sp[-1] == '':
        sp = sp[:-1]

    # TODO:
    if sp and sp[0] == '':  # is @root
        if len(sp) > 1:
            _contained = False
            for cx in plist:  # initially check anchor
                _cxe = splitapppathx_getlocalpath(_sp_elems, tpf=_tpf)
                if _cxe.startswith(ssep + sp[1]):
                    _contained = True
            if not _contained:
                return None
            sp = sp[1:]

    _maxmatch = 0  # the maximum length of match that actually occured
    _currentmatch = []  # stack of current last list

    si0 = -1
    if _rev:
        _pl = reversed(plist[:])
    else:
        _pl = plist

    for sl in _pl:
        # scan each path of pathlist(plist) for sp(spath) item-by-item
        si0 += 1
        _matchidx = matchidx  # count the present matches for each search path from plist

        if not sl:
            continue

        # prepare prefix - host and/or share
        if not raw:  # canonical
            # manage app paths - current network only
            _elements = splitapppathx(
                sl, appsplit=True, spf=_spf, tpf=_tpf, rtype=True)[0]
            try:
                _prtype, _phost, _pshare, sl, _qufrag = _elements  # for http/https
            except Exception:
                _prtype, _phost, _pshare, sl = _elements  # for file systems

            _prefix = _prtype + _phost

            if _pshare:
                if _prefix:
                    _prefix += tsep + _pshare
                else:
                    _prefix = _pshare

            if _app_prefix:
                if _app_prefix != _prefix:
                    continue

        else:
            _prefix = ''

        # apply a regexpr pattern as splitter
        _prefix = escapepathx(_prefix, force=True)
        sl_esc = escapepathx(sl, force=True)

        # the pattern needs twice
        regpattern = escapepathx(sp_tmp, _spf, force=True)
        regpattern = escapepathx(regpattern, _spf, force=True)
        s = re.split(regpattern, sl_esc)
        if len(s) < 2 or len(s) -1 < matchidx:
            # no match
            continue

        # length of resulting top-pattern
        lx = int((len(sl_esc) - len(''.join(s))) / (len(s) -1))

        # the resolved re
        sp_resolved = sl_esc[len(s[0]):len(s[0]) + lx]

        # prepare join
        if sp_resolved[-1] not in ('/', '\\'):
            for x in range(len(s)):
                if s[x] and s[x][0] not in ('/', '\\'):
                    s[x] = tsep + s[x]
        _r = _prefix

        # join as much as requested by matchidx, else the topmost only
        if _rev:
            lx = len(s) - matchidx #- (s[-1] == '')
            if lx <= 0 or lx > len(s):
                return None
            _j = sp_resolved.join(s[:lx])

        else:
            if matchidx < 1 or matchidx > len(s):
                FileSysObjectsError("out of valid range: matchidx = " + str(matchidx))
                # return None

            if matchidx == len(s):
                # the full string
                lx = matchidx - (s[-1] == '')
            else:
                # proceed as eventually expected
                lx = matchidx

            if lx == 0:
                # simply the first
                _j = s[0]
            else:
                # join the resolved re-split-pattern
                _j = sp_resolved.join(s[:lx])

        if not _hook:
            _j += sp_resolved

        remainder = ''
        if _split:
            if _rev:
                remainder = sp_resolved.join(s[len(s) - matchidx:])
            else:
                remainder = sp_resolved.join(s[matchidx:])
            if remainder[0] in ('/', '\\'):
                remainder = remainder[1:]
            if remainder[-1] in ('/', '\\'):
                remainder = remainder[:-1]

        if _j:
            if _r.startswith('file:'):
                if os.path.isabs(sl):
                    # RFC 8089
                    # add prefix and absolute path
                    _r += _j
                else:
                    raise FileSysObjectsError("RFC8089 Requires absolute path, got: " + str(sl))

            elif _r.startswith('http:'):
                if os.path.isabs(sl):
                    # RFC 3986
                    # add prefix and absolute path
                    _r += _j
                else:
                    raise FileSysObjectsError("RFC3986 Requires absolute path, got: " + str(sl))

            elif _sp_elems[0] is not 'lfsys':
                join_apppathx_entry((_prtype, _phost, _pshare, sl))

            else:
                _r += _j

        if _r[-1] in ('/', '\\'):
            _r = _r[:-1]
        _r = unescapepathx(_r, force=True)
        if not _split:
            return _r

        else:
            if _hook:
                return (_r, sp_resolved, remainder)
            else:
                return (_r, remainder)

    return None

def gettop_from_pathstring_partial_old(spath, plist=None, **kargs):
    """Searches for a partial path *spath* in a list of
    search paths *plist*. The current version supports for
    pure in-memory evaluation of literals and regexpr.

    The following example of input with default parameters ::

       spath := 'a/b/c'
       plist := [
          '/my/path/a/c/x/y/a/b/x/d/e/r',
          '/my/path/a/c/x/y/a/b/c/d/e/r',
       ]

    results in the first match: ::

       result := '/my/path/a/c/x/y/a/b/c'
       #
       # shortes top-match: '/my/path/a/c/x/y/' + 'a/b/c'
       #

    Same for a regular expression: ::

       spath := 'a/.*/[cxy]/[def]{1}'

    results again in: ::

       result := '/my/path/a/c/x/y/a/b/c'

    The match is performed by the re module based on *re.split*
    spanning multiple directories in case of reguar expressions.
    Thus the expressions require some caution when constraints
    are required. The function itself serves as a framework
    providing parameterization of the match criteria.

    Args:
        **spath**:
            A path to be appended to an item from 'plist'.

        **plist**:
            List of search strings to be extended
            by the subpath *spath*.

            default := sys.path

        kargs:
            **hook**:
                Returns the insertion point of *spath* without
                the *spath* itself.

            **keepsep**:
                Keeps significant separators, e.g. a trailing 'os.sep'.

                default := True

            **matchidx**:
                Use the n-th match only. ::

                   matchidx := #idx:

                   0 <= idx   ; first match

                * Ignore matches for '*< #idx*'
                * return match for '*== #idx*', and stop search

                default := 0 # first match

                Depends on *reverse*.

            **pathsep**:
                Replaces the path separator set by the *spf*. ::

                    pathsep := (';' | ':')

            **pattern**:
                Sets and activates scope and type of match pattern.
                The pattern is matched node-by-node for each
                corresponding directory level: ::

                   pattern := (literal | regexpr)

                * *literal*:

                  Match literally. Pattern are treated as characters.

                * *regexpr*:

                  Match regular expression for individual nodes,
                  implies no contained reserved characters of the
                  current file system, so 'os.sep' and no 'os.pathsep'.

                default := literal

            **raw**:
                Suppress normalization by call of
                'os.path.normpath'.

            **reverse**:
                This reverses the resulting search order
                from bottom-up to top-down. Takes effect on
                'redundant' only.

            **split**:
                Returns the path prefix matched on the search list,
                and the relative sub path outside the search list
                as a tuple. ::

                   split := (True | False)

                For example the input: ::

                   spath := 'a/b/c'
                   plist := [
                      '/my/path/a/c/x/y/a/b/x/d/e/r',
                      '/my/path/a/c/x/y/a/b/c/d/e/r',
                   ]

                results in: ::

                   result := ('/my/path/a/c/x/y', 'a/b/c')

            **spf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.getspf() <paths.html#getspf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.

            **strip***:
                Strips null-entries.

                default := True

            **tpf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to the API in the manual at :ref:`tpf <OPTS_TPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.gettpf() <paths.html#gettpf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.


    Returns:
        When successful returns by default the expanded pathname, else None.
        The return value in case of success depends on the parameters:

        * if *split == True*: returns a *tuple* ::

             result = (result[0], result[1],)

          result[0]: The matched path including the resolved searched sub-path *spath*.

          result[1]: The remainder.

        * if *split == True* and *hook == True*: returns a *tuple* ::

             result = (result[0], result[1], result[2],)

          result[0]: The matched path excluding the sub-path *spath*.

          result[1]: The resolved searched sub-path *spath*.

          result[2]: The remainder.

        * else: returns an *str* ::

             result = <str>

          * if *hook == True*:

            The matched path excluding the sub-path *spath* and an
            evtl. present remainder.

          * else:

            A string of the matched path including the resolved
            searched sub-path *spath*, excluding an evtl. present
            remainder.

    Raises:
        AppPathError

        passed-through

    """
    if plist == None:
        plist = sys.path
    elif type(plist) != list:
        raise AppPathError("Requires list argument:" + str(plist))

    try:
        _hook = kargs.pop('hook')
    except KeyError:
        _hook = False
    try:
        _rev = kargs.pop('reverse')
    except KeyError:
        _rev = False
    try:
        _split = kargs.pop('split')
    except KeyError:
        _split = False
    try:
        _strip = kargs['strip']
    except KeyError:
        _strip = False

    try:
        matchidx = kargs.pop('matchidx')
        if not type(matchidx) is int or matchidx < 0:
            raise AppPathError("Requires int>0 matchidx=" + str(matchidx))
    except KeyError:
        matchidx = 1

    try:
        _pat = kargs.pop('pattern')
        if _pat == 'regexpr':
            _pat = 1
        #
        # reminder: glob not supported for current release, requires an offline interpreter
        # elif v == 'glob':
        #     _pat = 2
        elif _pat == 'literal':
            _pat = 0
        else:
            raise FileSysObjectsError("gettop_from_pathstring:parameter not supported: pattern = " + str(_pat))
    except KeyError:
        _pat = 0

    raw = kargs.get('raw', False)
    _keepsep = kargs.get('keepsep', True)

    #
    # get spf
    #
    _spf = kargs.get('spf', False)
    ssep, spsep, _spf, _input = getspf(_spf)  # @UnusedVariable
    pathsep = kargs.get('pathsep', spsep)

    #
    # get tpf
    #
    _tpf = kargs.get('tpf', False)
    tsep, tpsep, _tpf, _output, _apre = gettpf(_tpf)  # @UnusedVariable


    def _comp(p, b):
        """match regexpr
        p: regexpr
        b: item plist[i][j]
        """
        if _pat == 1: # regexpr
            if p == '*':  # assume a glob expression, thus terminate 're' processing now
                return
            pc = re.compile(r'^' + p + r'$')
            px = pc.match(b)
            if px:
                return px.string[px.start():px.end()]

        elif _pat == 0:  # literal
            if p == b:
                return b

    # define processed portion, save prefix for later prepend on result
    if not raw:
        # For *spath*, is relative thus cannot be http/https
        #
        #   _rtype   type
        #   _host:   host
        #   _share:  share
        #   sp:      local path
        #
        _rtype, _host, _share, sp = splitapppathx(
            spath, appsplit=True, spf=_spf, tpf=_tpf, rtype=True,
            keepsep=_keepsep, strip=_strip)[0]
        _app_prefix = _rtype + _host
        if _share:
            if _app_prefix:
                _app_prefix += ssep + _share
            else:
                _app_prefix = _share

    else:
        _app_prefix, sp = '', spath

    # normalize search path
    #
    # For *spath*
    #
    #   _sp_elems[0]   type
    #   _sp_elems[1]:  host
    #   _sp_elems[2]:  share
    #   _sp_elems[3]:  local path
    #
    kargs['keepsep'] =  _keepsep
    _sp_elems = splitapppathx(sp, appsplit=True, **kargs)[0]
    sp = splitapppathx_getlocalpath(_sp_elems, tpf=_tpf)
    sp_tmp = sp


    sp = sp.split(ssep)
    if sp and sp[-1] == '':
        sp = sp[:-1]

    if sp and sp[0] == '':  # is @root
        if len(sp) > 1:
            _contained = False
            for cx in plist:  # initially check anchor
                _cxe = splitapppathx_getlocalpath(_sp_elems, tpf=_tpf)
                if _cxe.startswith(ssep + sp[1]):
                    _contained = True
            if not _contained:
                return None
            sp = sp[1:]

    _maxmatch = 0  # the maximum length of match that actually occured
    _currentmatch = []  # stack of current last list

    si0 = -1
    if _rev:
        _pl = reversed(plist[:])
    else:
        _pl = plist

    for sl in _pl:
        # scan each path of pathlist(plist) for sp(spath) item-by-item
        si0 += 1
        _matchidx = matchidx  # count the present matches for each search path from plist

        if not sl:
            continue

        if not raw:  # canonical
            # manage app paths - current network only
            _elements = splitapppathx(
                sl, appsplit=True, spf=_spf, tpf=_tpf, rtype=True)[0]
            try:
                _prtype, _phost, _pshare, sl, _qufrag = _elements  # for http/https
            except Exception:
                _prtype, _phost, _pshare, sl = _elements  # for file systems

            _prefix = _prtype + _phost

            if _pshare:
                if _prefix:
                    _prefix += tsep + _pshare
                else:
                    _prefix = _pshare

            if _app_prefix:
                if _app_prefix != _prefix:
                    continue

        else:
            _prefix = ''


        # split the pattern
        sl_esc = escapepathx(sl, force=True)

        s = re.split(escapepathx(sp_tmp, _spf, force=True), sl_esc)
        if len(s) < 2 or len(s) -1 < matchidx:
            # no match
            continue
            # return None

        lx = int((len(sl_esc) - len(''.join(s))) / (len(s) -1))
        sp_resolved = sl_esc[len(s[0]):len(s[0])+lx]

        if sp_resolved[-1] not in ('/', '\\'):
            for x in range(1,len(s)):
                if s[x] and s[x][0] not in ('/', '\\'):
                    s[x] = tsep + s[x]
        _r = _prefix

        # join as much as requested by matchidx
        if _rev:
            lx = len(s) - matchidx #- (s[-1] == '')
            if lx <= 0 or lx > len(s):
                return None
            _j = sp_resolved.join(s[:lx])

        else:
            if matchidx < 1 or matchidx > len(s):
                return None
            if matchidx == len(s):
                lx = matchidx - (s[-1] == '')
            else:
                lx = matchidx
            if lx == 0:
                _j = s[0]
            else:
                _j = sp_resolved.join(s[:lx])

        if not _hook:
            _j += sp_resolved

        remainder = ''
        if _split:
            if _rev:
                remainder = sp_resolved.join(s[len(s) - matchidx:])
            else:
                remainder = sp_resolved.join(s[matchidx:])
            if remainder[0] in ('/', '\\'):
                remainder = remainder[1:]
            if remainder[-1] in ('/', '\\'):
                remainder = remainder[:-1]

        if _j:
            if _r.startswith('file:'):
                if os.path.isabs(sl):
                    # RFC 8089
                    # add prefix and absolute path
                    _r += _j
                else:
                    raise FileSysObjectsError("RFC8089 Requires absolute path, got: " + str(sl))

            elif _r.startswith('http:'):
                if os.path.isabs(sl):
                    # RFC 3986
                    # add prefix and absolute path
                    _r += _j
                else:
                    raise FileSysObjectsError("RFC3986 Requires absolute path, got: " + str(sl))

            elif _sp_elems[0] is not 'lfsys':
                join_apppathx_entry((_prtype, _phost, _pshare, sl))

            else:
                _r += _j

        if _r[-1] in ('/', '\\'):
            _r = _r[:-1]

        if not _split:
            return _r

        else:
            if _hook:
                return (_r, sp_resolved, remainder)
            else:
                return (_r, remainder)

    return None

def gettop_from_pathstring_iter(spath, plist=None, **kargs):
    """Iterates all matches in plist,see gettop_from_pathstring.
    """
    if plist == None:
        plist = sys.path

    for pl in plist:
        r = gettop_from_pathstring(spath, [pl], **kargs)
        if r:
            yield r

