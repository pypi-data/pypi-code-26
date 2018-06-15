# -*- coding: utf-8 -*-
"""The filesysobjects.pathstools module provides operations
for address paths of file system based resources.

.. note::

   Current version supports local accessible file systems only.

"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import re, sre_constants
import glob
import itertools
from filesysobjects.plugins.smb import normapppathx


from filesysobjects import V3K

try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk  # @UnusedImport

from pysourceinfo.helper import getpythonpath_rel

import filesysobjects
from filesysobjects import ISSTR, PathError, \
    RTE, RTE_WIN32, RTE_POSIX, \
    FileSysObjectsError, PathToolsError, \
    W_LITERAL_QUOTED, \
    OF_LIST_STR, OF_LIST_OID, OF_LIST_RAW, \
    L_TDOWN_WALK, \
    M_ALL, M_FILTPAR, \
    T_ALL, T_DIR, T_FILE, T_SYML, T_MNT, T_HARDL, T_DEV, \
    Q_ALL_TRIPLE, Q_DOUBLE_TRIPLE, Q_SINGLE_TRIPLE, \
    W_GLOB, W_RE, \
    rte2num, \
    _debug

from filesysobjects.paths import normpathx, escapepathx
from filesysobjects.apppaths import splitapppathx

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez" \
                "@Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.20'
__uuid__ = "4135ab0f-fbb8-45a2-a6b1-80d96c164b72"

__docformat__ = "restructuredtext en"


rebaseflags = re.X  # @UndefinedVariable
if V3K:
    rebaseflags |= re.ASCII  # @UndefinedVariable

if V3K:
    pathflags = rebaseflags | re.M | re.ASCII  # @UndefinedVariable
else:
    pathflags = rebaseflags | re.M  # @UndefinedVariable

#: First stage regexpr scanner for 'normpathx', also used in 'escapepathx'.
QUOTESCANNER = re.compile(r"""
    (["]{3}[\x01-\xFF]*?["]{3})       # 1  quoted string by 3 double quotes(") - similar to Python
    |([']{3}[\x01-\xFF]*?[']{3})      # 2  quoted string by 3 single quotes(') - similar to Python
    |(.*?)(?=["]{3}|[']{3})
    |(.*)
    """, pathflags)


def findrelpath_in_searchpath(spath, plist=None, **kargs):
    """Search for subdirectory trees *spath* of the paths
    contained in *plist*. ::

       MATCH :  plist[x]/spath

    supports *glob*.

    Args:
        **spath**:
            A path to be hooked into 'plist[]' when present.
            Could be either a literal, or a glob as an relative
            or absolute path. Valid *spath* wildcard types:

            +---------+----+
            | literal | X  |
            +---------+----+
            | re      | -- |
            +---------+----+
            | glob    | X  |
            +---------+----+

            See common options for details. ::

               spath := (literal|glob):


        **plist**:
            List of potential hooks for 'spath'.
            The following formats are provided:

                1. list of single paths - used literally
                2. list of search path strings - each search path is split
                3. string with search path - split into it's components
                4. string with a single path - used literally

            The default behavior is:

                * first: (1.)
                * second: (3.), this contains (4.)

            The case (2.) has to be forced by the key-option: 'subsplit',
            or to be prepared by the call 'clearpath(split=True,)'.

            Due to performance the case #1 should be preferred in order
            to save repetitive automatic conversion.

            See common options for further details.


            default := sys.path

        kargs:
            **isDir**:
                Is a directory.

            **isFile**:
                Is a file.

            **isLink**:
                Is a symbolic link.

            **isPathByLink**:
                Has a symbolic link in path.

            **matchidx**:
                Ignore matches '< #idx',
                return match '== #idx'. Depends on
                'reverse' ::

                   matchidx := #idx:

                default := 0 # first match

            **noglob**:
                Suppress application of 'glob'.

            **not**:
                Inverts to does not matched defined
                criteria.

            **raw**:
                Suppress normalization by call of
                'os.path.normpath'.

            **reverse**:
                Reversed search order.

            **subsplit**:
                Splits each item part of a 'plist' option.

    Returns:
        When successful returns the absolute pathname,
        else 'None'. For a list refer to iterator.

    Raises:
        PathToolsError
        passed through exceptions

    """
    if not spath:
        return

    if type(plist) is list:
        pass
    elif plist is None:
        plist = sys.path
    elif type(plist) in ISSTR:
        plist = splitapppathx(plist, apppre=False)
    else:
        raise PathToolsError("Unknown type:" + str(plist))

    if os.path.isabs(spath):
        if os.path.exists(spath):
            return spath
        return None

    raw = False
    _rgx = False
    _rev = False
    matchidx = 0

    _chkT = False
    _isL = False
    _isD = False
    _isF = False
    _isPL = False

    _not = False
    _ng = False

    _ssplit = False

    for k, v in kargs.items():
        if k == 'matchidx':
            if not type(v) is int or v < 0:
                raise PathToolsError("Requires int>0 matchidx=" + str(v))
            matchidx = v
        elif k == 'not':
            _not = v
        elif k == 'raw':
            raw = v
        elif k == 'reverse':
            _rev = v
        elif k == 'noglob':
            _ng = v
        elif k == 'isLink':
            _chkT = True
            _isL = v
        elif k == 'isDir':
            _chkT = True
            _isD = v
        elif k == 'isFile':
            _chkT = True
            _isF = v
        elif k == 'isPathByLink':
            _chkT = True
        elif k == 'subsplit':
            _ssplit = True
        else:
            raise PathToolsError("Unknown param: " + str(k) + ":" + str(v))

    if _ssplit:  # split sub paths, but do not alter the callers source
        plist = plist[:]
        clearpath(plist, split=True)

    # use canonical copy
    if not raw:
        _sp = normpathx(spath, keepsep=True, apppre=False)
    else:
        _sp = spath[:]

    def _checkit(p):
        _b = True

        if _chkT:
            if _isF and not os.path.isfile(p):
                _b = False
            elif _isD and not os.path.isdir(p):
                _b = False
            elif _isL and not os.path.islink(p):
                _b = False
            elif _isPL and not os.path.isfile(p):
                _b = False
        return _b

    # short it up for absolute input of existing paths, thus is a literal too!
    if os.path.isabs(_sp) and os.path.exists(_sp):  # exists as absolute
        _b = _checkit(_sp)
        for p in plist:
            if not p:
                continue
            if p.startswith(_sp):
                _b &= True
                if _b and matchidx != 0:
                    _b = False
                    matchidx -= 1
                return normpathx(_sp)

        if _b and not _not:
            return _sp

        return None

    if _rev:  #: reverse => bottom up for sorted
        _pl = reversed(plist)
    else:
        _pl = plist

    # now look for hooks of relative paths in plist
    for p in _pl:
        if not p:
            continue
        _b = True

        if os.path.isabs(_sp):
            _px = normpathx(_sp)
        else:
            _px = normpathx(os.path.abspath(p + os.sep + _sp), stripquote=True)

        if os.path.exists(_px):
            _b = _checkit(_px)

            if _b and matchidx != 0:
                _b = False
                matchidx -= 1

            if _b and not _not:
                return _px

            continue

        if not _ng:
            # try a glob
            for gm in glob.glob(_px):
                _b = _checkit(gm)

                if _b and matchidx != 0:
                    _b = False
                    matchidx -= 1

                if _b and not _not:
                    return gm

                continue

    return None


def findrelpath_in_searchpath_iter(spath, plist=None, **kargs):
    """Iterates all matches in plist, see *findrelpath_in_searchpath*.
    """

    if plist == None:
        plist = sys.path
    elif type(plist) in ISSTR:
        plist = [plist]

    for pl in plist:

        # TODO:
        matchidx = 0
        kargs['matchidx'] = matchidx
        while True:
            r = findrelpath_in_searchpath(spath, [pl], **kargs)
            if r:
                yield r
                kargs['matchidx'] += 1
            else:
                break


def findrelpath_in_uppertree(spath, plist=None, **kargs):
    """Iterates all matches in plist, see findrelpath_in_searchpath.
    """
    return None


def findrelpath_in_uppertree_iter(spath, plist=None, **kargs):
    """Iterates all matches in plist, see *findrelpath_in_uppertree*.
    """
    if plist == None:
        plist = sys.path

    for pl in plist:

        # TODO:
        matchidx = 0
        kargs['matchidx'] = matchidx
        while True:
            r = findrelpath_in_searchpath(spath, [pl], **kargs)
            if r:
                yield r
                kargs['matchidx'] += 1
            else:
                break


def findpattern(*srcdirs, **kargs):
    """Executes on each *srcdirs* a tree search with match and drop patterns.
    The interface is basically similar to 'find' with enhanced match options.

    The search operation relies for Python3.5+ on *os.scandir()* - for
    Python2.7 on *scandir.scandir()*. The interface extends the lower layer
    API by lists of filters with support for 'literal', 'glob' and/or
    'regexpr' pattern.

    The search algorithm is performed as:

    0.  If *srcdirs* is provided use each as starting file path,
        else initialize based on current working directory.

    1.  Set behavior attributes, see options:

        0. *listorder*
        1. *followlinks*
        2. *matchbehavior*
        3. *matchcnt*

        .
    2.  If no filter parameters are present return afterwards.

        Else apply filter parameters. Each non-matching condition
        continues with next filter cycle by default. When no match
        the result is accepted, see options:

        0.  check *level*
        1.  check *blacklist*
        2.  check *whitelist*
        3.  check *dropdirs*
        4.  check *type*

        .
    3.  Apply string manipulation, see options

        a. check-cut *topcutlist*

        .

    The general behavior for the parameters is additive, this means
    e.g. when provided *wildcards*, *globs*, *regexpr*, and *filter*
    these are applied subsequently. Each match is added by default
    to the result list. The drop parameters instantly remove the match
    from the result list.

    Args:

        **srcdirs**:
            List of top level paths for search. Supports *literal*,
            *re*, and *glob*.

            default := *[<current-workdir>,]*

        kargs:
            Additional control:

            **abs**:
                Defines the type of returned path value,
                when present. ::

                   abs := (
                         True    # Force absolute paths.
                       | False   # Force relative paths.
                   )

                default := "depends on type of input"

            **blacklist**:
                File system nodes to be dropped from the result.
                Supports Python *re* expressions,
                See `Variants of Pathname Parameters - Literals, RegExpr, and Glob <path_syntax.html#variants-of-pathname-parameters-literals-regexpr-and-glob>`_

                default := None

            **whitelist**:
                File system nodes to be added to the result.
                Supports Python *re* expressions,
                See `Variants of Pathname Parameters - Literals, RegExpr, and Glob <path_syntax.html#variants-of-pathname-parameters-literals-regexpr-and-glob>`_

                default := *\**

            **followlinks**:
                Follow symbolic links.

                default := *False*

            **gid**:
                Group ID.

            **level**:
                Depth of search. The values are: ::

                   None: Search the subtree unlimited.
                   0:    Current directory only, basically
                         the same as *os.listdir()*.
                   >0:   Sub-directories of given level.

                default := *None*

            **matchcnt**:
                Defines the selection of matches:

                * *n<0*: the last *n*, last := *-1*.
                * *n=0*: all
                * *n>0*: the first *n*, first := *1*.

                default := 0

            **nopostfix**:
                Deletes for files the postfix.

            **output**:
                Output format. Current available formats are: ::

                   output := (
                       OF_LIST_STR,   # list of file system path names
                       OF_LIST_OID,   # list of dotted object notation
                       OF_RAW         # list of raw entries *DirEntry*, see scandir
                   )

            **topcutlist**:
                Cut listed topmost path elements from
                found list elements, resulting in relative
                pathnames.

                default := *['.' + os.sep]*

            **topdown**:
                Defines the order or the resulting list, same as
                *os.walk*. ::

                   topdown := (True | False)

                default := True

            **types**:
                Search and list selected types only.
                The value is a bit-array. ::

                    T_ALL, T_DEV, T_FILE, T_DIR, T_HARDL,
                    T_EXP, T_LOCAL, T_MNT, T_NODES,
                    T_SYML

                default := *T_ALL*

            **uid**:
                User ID.

    Returns:
        Results in an list of found entries. When none,
        an empty list.

    Raises:

        ffs.

    """
    ret = []  # resolved result
    i0 = 0  # reusable index - handle with care
    i1 = 0  # reusable index - handle with care
    i2 = 0  # reusable index - handle with care

    if not srcdirs:
        srcdirs = ('.')

    _blacklist = None
    _followlinks = False
    _gid = []
    _lvl = None
    _matchbehavior = M_ALL | M_FILTPAR
    _matchcnt = 0
    _nopostfix = False
    _output = OF_LIST_STR
    _srcdirs = srcdirs
    _topcutlist = ['.' + os.sep]
    _topdown = L_TDOWN_WALK
    _types = T_ALL
    _uid = []
    _whitelist = None

    for k, v in kargs.items():
        if k == 'types':
            _types = v
        elif k == 'level':
            if v == None:
                _lvl = -1
            elif v >= 0:
                _lvl = v
            else:
                raise FileSysObjectsError("supported values for %s: None, x>=0, got: %s" % (str(k), str(v)))
        elif k == 'listorder':
            _topdown = v
        elif k == 'followlinks':
            _followlinks = v
        elif k == 'matchbehavior':
            _matchbehavior = v
        elif k == 'matchcnt':
            _matchcnt = v
        elif k == 'nopostfix':
            _nopostfix = v
        elif k == 'topcutlist':
            if type(v) in ISSTR:
                _topcutlist = [v]
            elif isinstance(v, (list, tuple)):
                _topcutlist = v
        elif k == 'blacklist':
            if type(v) in ISSTR:
                _blacklist = v
            elif isinstance(v, (list, tuple)):
                _blacklist = v
            else:
                raise FileSysObjectsError("'%s' requires (str|list|tuple), got: %s" % (k, str(v)))
        elif k == 'whitelist':
            if type(v) in ISSTR:
                _whitelist = v
            elif isinstance(v, (list, tuple)):
                _whitelist = v
            else:
                raise FileSysObjectsError("'%s' requires (str|list|tuple), got: %s" % (k, str(v)))
        elif k == 'gid':
            _gid = v
        elif k == 'uid':
            _uid = v
        elif k == 'output':
            _output = v

        else:
            raise PathToolsError("Unknown parameter:" + str(k) + ":" +
                                     str(v))

    # monitor thresholds
    _clvl = 0  # current level
    _cmatch = 0  # current match count

    #
    # cache for resolved source paths
    #
    _srccache = []
    for i0 in _srcdirs:  # workout source dirs

        # TODO:

        i1 = expandpath(i0, wildcards=W_GLOB | W_RE)
        if i1:
            _srccache.extend(i1)

    #
    # whitelist
    #
    _wcache = None
    if _whitelist:
        try:
            # give it a try
            _wcache = re.compile(normpathx(escapepathx(_whitelist), stripquote=True))
        except TypeError:
            try:
                _wcache = []
                for x in _whitelist:
                    # pattern needs twice
                    _pat = normpathx(escapepathx(x), force=True, stripquote=True)
                    _pat = escapepathx(_pat, force=True)
                    _wcache.append(re.compile(_pat))

            except IndexError as e:
                    raise PathError(str(e) + '\n' + "requires (str | list | tuple), got: " + str(_whitelist))
        except sre_constants.error as e:
            if e.pattern is not None and e.pos is not None:
                e.msg += '\n"re" compile-error:\n in: %s\n     %s^\n  => %s' % (
                    str(escapepathx(e.pattern)),
                    ' ' * (e.pos),
                    str(escapepathx(e.pattern)[:e.pos+1])
                )
                raise PathError(str(e) + '\n' + e.msg)

    #
    # blacklist
    #
    _bcache = None
    if _blacklist:
        try:
            try:
                _bcache = re.compile(normapppathx(escapepathx(_blacklist), stripquote=True))
            except TypeError:
                try:
                    _bcache = []
                    for x in _blacklist:
                        _bcache.append(re.compile(normapppathx(escapepathx(x), stripquote=True)))
                except IndexError as e:
                        raise PathError(str(e) + '\n' + "requires (str | list | tuple), got: " + str(_blacklist))
        except sre_constants.error as e:
            if e.pattern is not None and e.pos is not None:
                e.msg += '\n"re" compile-error:\n in: %s\n     %s^\n  => %s' % (
                    str(escapepathx(e.pattern)),
                    ' ' * (e.pos),
                    str(escapepathx(e.pattern)[:e.pos+1])
                )
                raise PathError(str(e) + '\n' + e.msg)

    def checknode(nx, **kargs):
        """Check a single node by prepared filter.

        Args:

            **nx**:
                Directory entry: ::

                   Python2.7:  *scandir.DirEntry*.
                   Python3.5+: *os.DirEntry*.

        Returns:

            MATCH: paths
            ELSE:  None

        Raises:

        """
        ret = True

        #
        # blacklist
        #
        if _bcache:
            try:
                if _bcache.match(nx.path):
                    return False

            except AttributeError:
                ret = True
                for spx in _bcache:
                    if spx.match(nx.path):
                        return False

        #
        # whitelist
        #
        if _wcache:
            try:
                if not _wcache.match(nx.path):
                    ret = False

            except AttributeError:
                ret = False
                for spx in _wcache:
                    if spx.match(nx.path):
                        ret = True
                        break
            if not ret:
                return False

        # check type
        if _types ^ T_ALL:
            ret = False
            if _types & T_DIR and nx.is_dir(follow_symlinks=_followlinks):
                ret = True
            if _types & T_FILE and nx.is_file(follow_symlinks=_followlinks):
                ret = True
            if _types & T_SYML and nx.is_symlink():
                ret = True
            if _types & T_MNT and os.path.ismount(nx.path):
                ret = True

            si = nx.stat(follow_symlinks=_followlinks)
            if _types & T_HARDL and si.st_nlink != 1:
                ret = True
            elif _types & T_DEV and si.st_dev:
                ret = True

            # elif  _types & T_EXP and os.path.isfile(nx):
            #    res.append(nx)
            # elif  _types & T_LOCAL and os.path.isfile(nx):
            #    res.append(nx)
            # elif  _types & T_NODES and os.path.isfile(nx):
            #    res.append(nx)
        elif _uid or _gid:
            si = nx.stat(follow_symlinks=_followlinks)
            if _uid and si.st_uid in (_uid):
                ret = True
            if _gid and si.st_gid in (_gid):
                ret = True

        return ret

    def fetchnode(start, lvl=0):
        if _lvl != None and lvl > _lvl:
            return

        _opwd = None
        if abs:
            # force absolute
            start = os.path.abspath(start)
        elif abs == False and start[0] == os.sep:
            _opwd = os.path.curdir
            os.path.curdir = start


        for sx in scandir(start):
            if checknode(sx):
                if _output in (OF_LIST_STR, OF_LIST_OID):
                    # a. check-cut postfix
                    if _nopostfix and sx.is_dir():
                        px = os.path.splitext(sx.path)[0]
                    else:
                        px = sx.path

                    # b. check-cut topcutlist
                    if _topcutlist:
                        for i2 in _topcutlist:
                            if px.startswith(i2):
                                px = px[len(i2):]
                                break

                    if _output == OF_LIST_OID:
                        ret.append('.'.join(px.split(os.sep)))
                    else:
                        ret.append(px)

                elif _output == OF_LIST_RAW:
                    ret.append(sx)


            if sx.is_dir():
                fetchnode(sx.path, lvl+1)

        if _opwd:
            os.path.curdir = _opwd

        return

    for s in _srccache:  # workout top-root-list
        fetchnode(s)

    return ret


#
# Pre-Reduce the result by glob for literal prefix of re.
# Match on the longest sub-part applicable as prefix for a glob
#
_glob_prefix = re.compile(r"""
     (^[a-zA-Z]:)                       # 1  - DOS drive
    |(\[[\^][^\]]*\][*]*)               # 2  - [^...]  it is a re
    |(\[[^/\]]*\][*]*)                  # 3  - [...]   a char class without separator
    |(\[[!][^/\]]*[/][^\]]*\][*]*)      # 4  - [!.../...]   a non-def char class with separator
    |(\[[/]*\][*]*)                     # 5  - [/]   a char class with posix-separator ONLY
    |(\[[^/\[\]]*[/][^/\[]*\][*]*)      # 6  - [.../...]   a char class with posix-separator
    |(\[[\\\\]*\][*]*)                  # 7  - [\\\\]   a char class with nt-separator ONLY
    |(\[[^\\\\]*[\\\\][^\\\\]*\][*]*)   # 8  - [...\\\\...]   a char class with nt-separator
    |(\([^)]*\))                        # 9  - (......)   a re-group
    |([/]+)                             # 10  - '/'     class-less n * posix-separator
    |([\\\\]+)                          # 11 - '\\'    class-less n * nt-separator
    |([^/\\\\\[\]]*[.][*][^/\\\\\[\]]*)(?=/|$)
                                        # 12 - a string containing '.*' and optional additional chars
    |([*])                              # 13 - a wildcard character
    |([^/\\\\\[\]]+)(?=/|$)             # 14 - any character until next shlash - separator for posix
    |([^/\\\\\[\]]+)(?=[\\\\]|$)        # 15 - any character until next back-slash - separator for win
    |(\[)                               # 16 - likely to be a syntax error, but could be literal too
    |(\])                               # 17 - likely to be a syntax error, but could be literal too
    |(.)                                # 18 - any literal character
    |($)                                # 19 - end of string
    """, re.X)  # @UndefinedVariable

def stripquotes(path, scope=Q_ALL_TRIPLE):
    """Strips quotes.

    Args:
        **path**:
            Path to strip off of quotes.

        **scope**:
            Scope to be applied. ::

               scope := (
                    Q_ALL_TRIPLE     # " * 3 and ' * 3
                  | Q_DOUBLE_TRIPLE  # " * 3
                  | Q_SINGLE_TRIPLE  # ' * 3
               )

    Returns:
        Path without selected triple-quotes.

    Raises:
        pass-through

    """
    parts = ''
    for it in QUOTESCANNER.finditer(path):
        g = it.lastindex  # PATHSCANNER ASCII_SC_CTRL
        if it.group(g):
            x = it.group(g)
            if g == 1 and scope & Q_DOUBLE_TRIPLE:
                _x = x[3:-3]
                if not parts:
                    parts += _x
                else:
                    parts += _x
                continue

            elif g == 2 and scope & Q_SINGLE_TRIPLE:
                # ignore SonarLint here
                _x = x[3:-3]
                if not parts:
                    parts += _x
                else:
                    parts += _x
                continue

            else:
                parts += x

    return parts

def split_re_glob(expr, **kargs):
    """Splits a mixed path expression into the *glob* + *literal*
    prefix and the regular expression *re* postfix. The cut for the
    expression is done by grouping the expressions at the edge of
    paths by matched free characters of path separators. The
    detection of the first *re* is done by detecting an unambiguously
    non-glob expression. These are considered as *re* expressions: ::

       [^...]     a exclusive character class
       (...)      a group
       \[ or \]   escaped square brackets

    Due to the various permitted character ranges,
    where e.g. POSIX allows almost any character these
    maz still be valid characters. In this case they have
    to be either escaped, or to be applied within character
    classes.

    The type resolution could in addition controlled by
    the option *typeprio*, which redfines some compilation
    priorities.

    See manual for further details.

    Args:
        **expr**:
            expression to be split

        kargs:
            **spf**:
                Source platform, defines the separator for path items.

                default := None

            **typeprio**:
                The priority type in case of ambiguity. ::

                   typeprio := (
                        W_GLOB     # interprets as *glob*
                      | W_RE       # interprets as *re*
                   )

                default := W_RE

    Returns:
        A list of two elements,
        'L[0]- glob' and 'L[1]- re'

    Raises:
        pass-through

    """
    _res = [[],[]]
    _buf = ['']
    _state = 0  # has changed from *glob* to *re*

    spf = kargs.get('spf')
    if not spf:
        spf = RTE
    else:
        try:
            spf = rte2num[spf]
        except KeyError:
            raise FileSysObjectsError("Unknown source platform: " + str(spf))

    typeprio = kargs.get('typeprio', W_RE)

    for it in _glob_prefix.finditer(expr):
        g = it.lastindex

        # glob-prefix
        if g in (
                3,  # class no sep
                13,  # wildcard char
            ):
            _buf[-1] += it.group(g)

        if g in (
                12,  # any-wildcard
            ):
            _buf[-1] += it.group(g)
            if typeprio & W_RE:
                _state = 1

        # any character until next shlash - separator for posix
        elif g in (
                14, # any char until next shlash
                18, # 17 - any literal character
            ):
            # is a path-item separator in any case - I am likely to ignore that POSIX allows slash as part of node name
            _buf[-1] += it.group(g)

        # any character before next back-slash - separator for win
        elif g in (
                15, # any char before next back-slash
            ):
            if spf == RTE_WIN32:
                # is a path-item separator for win
                _buf[-1] += it.group(g)
            else:
                # is a common character for path-item names
                _buf[-1] += it.group(g)

        # non-glob
        elif g in (
                2,  # [^...]
                4,  # [^/]
                16, # \[  basically a syntax error, but could be literal
                17, # \]  basically a syntax error, but could be literal
                9,  # (...) group
            ):
            if not _state:
                _res[0].extend(_buf[:-1])
                _buf = _buf[-1:]
                _state = 1
            _buf[-1] += it.group(g)

        # free separators
        elif g in (
               10,  # free n*posix-sep
            ):
            if not _state:
                if _buf[-1] != '':
                    _res[0].extend(_buf)
                    _buf = ['']
            elif _buf[-1] != '':
                _buf.append('')

        # free separators
        elif g in (
                11,  # free n*nt-sep
            ):
            if spf & RTE_WIN32:
                if _buf[-1] != '':
                    _buf.append('')
            else:
                _buf[-1] += it.group(g)

        # separators in classes
        elif g in (
                5,  # class with posix-sep [/]
            ):
            # is a common character for path-item names
            _buf[-1] += it.group(g)

        # separators in classes
        elif g in (
                8,  # class with nt-sep
            ):
#             if spf == RTE_WIN32:
#                 # is a path-item separator for win
#                 _buf.append('')
#             else:
#                 # is a common character for path-item names
#                 _buf[-1] += it.group(g)
            _buf[-1] += it.group(g)

        # dos drive
        elif g in (
                1,  # DOS drive
            ):
            _buf[-1] = it.group(g)

    if len(_buf) > 1 and _buf[-1] == '':
        _buf = _buf[:-1]

    if _state:
        # has re
        _res[1] = _buf
    else:
        # assumably did not match any re
        _res[0].extend(_buf)

    return _res


def get_subpath_product(dirs, subpaths):
    """Creates the textual cartesian product of directories and relative sub-paths.
    Addditional checks sould be applied by *clearpath()* and *expandpath()*.

    The calls for the specific platforms notations: ::

       cprod_posix = get_subpath_product(('/path/0', '/path/1'), ('suba', 'subb'))
       cprod_win32 = get_subpath_product(('c:\path\0', 'd:\path\1'), ('suba', 'subb'))

    results in: ::

       cprod_posix == [
           '/path/0/suba', '/path/0/subb',
           '/path/1/suba'  '/path/1/subb'
        ]
       cprod_win32 == [
           'c:\path\0\suba', 'c:\path\0\subb',
           'd:\path\1\suba'  'd:\path\1\subb'
        ]

    Args:
        **dirs**:
            Base directories for the provided subdirectories.

        **subpaths**:
            Sub-paths, each to be located within each of the
            directories *dirs*.

    Returns:
        The list of path names resulting from the literal textual
        cartesian product.

    Raises:
        pass-through

    """
    res = []
    for x in itertools.product(dirs, subpaths):
        if os.path.isabs(x[1]):
            raise FileSysObjectsError("subpath is absolute:" + str(x))
        res.append(os.sep.join(x))
    return res


#: The scanner for the glob to re compiler.
_glob_to_re = re.compile(r"""
    (["]{3}[\x01-\xFF]*?["]{3})         # 1  quoted string by 3 double quotes(") - similar to Python
    |([']{3}[\x01-\xFF]*?[']{3})        # 2  quoted string by 3 single quotes(') - similar to Python

    |(\[[!][^/\]]*[/][^\]]*\])          # 3  - [!.../...]
    |(\[[!][^\]]*[^\]]*\])              # 4  - [!...]
    |(\[[!][^/\]]*[*][^\]]*\])          # 5  - [!...*...]
    |(\[[!][^/\]]*[.][^\]]*\])          # 6  - [!...'.'...]
    |(\[[!][^/\]]*[?][^\]]*\])          # 7  - [!...'?'...]
    |(\[[^/\]]*[/][^\]]*\])             # 8  - [.../...] - don't touch it
    |(\[[^/\]]*[*][^\]]*\])             # 9  - [...*...] - don't touch it
    |(\[[^/\]]*[.][^\]]*\])             # 10 - [...'.'...] - don't touch it
    |(\[[^/\]]*[?][^\]]*\])             # 11 - [...'?'...] - don't touch it
    |([\\\\][\\\\])                     # 12 - escaped backslash
    |([\\\\][*])                        # 13 - escaped wildcard character
    |([*])                              # 14 - wildcard character
    |([.])                              # 15 - dot - for glob a literal dot
    |([?])                              # 16 - question mark - for glob any char
    |(.)                                # 17 - any literal char
    |($)                                # 18 - end of string
    """, re.X)  # @UndefinedVariable

def glob_to_re(expr, **kargs):
    """Compiles a *glob* to the corresponding *re*.
    The following mapping is implemented:

    +-------+-------+
    | glob  | re    |
    +=======+=======+
    | \*    | .*    |
    +-------+-------+
    | [!x]  | [^x]  |
    +-------+-------+
    | .     | [.]   |
    +-------+-------+
    | ?     |  .    |
    +-------+-------+

    Args:
        **expr**:
            A *glob* expression. The function relies on
            the caller and 'blindly' assumes to process
            a glob.

        kargs:
            **spf**:
                The platform defining the syntax domain
                of *expr*.

    Returns:
        The converted expression.

    Raises:
        pass-through

    """
    res = ''

    spf = kargs.get('spf', RTE)

    for it in _glob_to_re.finditer(expr):
        g = it.lastindex
        if g in (1, 2):  # quotes
            res += it.group(g)

        if g in (3, 4, 5, 6, 7,):  # exclusive classes
            res += '[^' + it.group(g)[2:]

        elif g in (8, 9, 10, 11,):  # classes
            res += it.group(g)

        elif g in (12,):  # '\\'
            res += it.group(g)

        elif g in (13,):  # '\*'
            if spf == RTE_WIN32:
                res += '\.*'
            else:
                # requires escaping when not wanted
                res += it.group(g)

        elif g == 14:  # '*'
            res += '.*'

        elif g == 15:  # '.'
            res += '[.]'

        elif g == 16:  # '?'
            res += '.'

        elif g == 17:  # <any-char>
            res += it.group(g)

        elif g == 18:  # '$'
            res += it.group(g)

    return res


def splitre_separator(expr):
    """Splits a literal and/or wildcard expressions into it's
    directory items. This provides for intermediate file sets
    evaluated by directory-wise *glob* and *re*.

    Args:
        **expr**:
            expression to be split

    Returns:
        A list of partial wildcard expressions

    Raises:
        pass-through

    """
    res = ['']

    for it in _glob_prefix.finditer(expr):
        g = it.lastindex
        if g in (
                1,   # 1  - DOS drive
                2,   # class no sep
                3,   # class no sep
                4,   # [^/]
                9,   # group
                12,  # wildcard char with '.*'
                13,  # wildcard char
                14,  # any character until next back-slash - separator for posix
                15,  # any character until next back-slash - separator for win
                16,  # \[  basically a syntax error, but could be literal
                17,  # \]  basically a syntax error, but could be literal
                18,  # 17 - any literal character
                19,
            ):
            res[-1] += it.group(g)

        elif g in (
                10,  # free n*posix-sep
                11,  # free n*nt-sep
            ):
            res.append('')

        elif g in (
                5,  # class with posix-sep [/]
                6,  # class with posix-sep [/] only
                7,  # class with nt-sep only
                8,  # class with nt-sep
            ):
            res[-1] += it.group(g)

    if len(res) > 1 and res[-1] == '':
        return res[:-1]
    return res


def clearpath(plist=None, **kargs):
    """Clears, splits and joins a list of path variables by various criteria.

    Args:
        **plist**:
            List of paths to be cleared.
            See common options for details.

            default := sys.path

        kargs:
            **abs**:
                Converts all entries into absolute pathnames.
                This implies the activation of the options
                *shellvars* and *uservars*.

                default := False

            **existent**:
                Removes all existing items. For test
                and verification.

                default := False

            **nonexistent**:
                Removes all items which do not exist.

                default := False

            **nonredundant**:
                Removes all items which are not redundant.
                Results e.g. in multiple incarnations of the same
                file/path type.

                default := False

            **normpath**:
                Calls 'os.path.normpath' on each result.

                default := False

            **redundant**:
                Clears all items from redundancies.

                default := True

            **rel**:
                Converts all entries into relative pathnames.

                default := False

            **reverse**:
                This reverses the resulting search order
                from bottom-up to top-down. Takes effect on
                'redundant' only.

                default := False

            **shellvars**:
                Replaces shell variables within pathnames. ::

                  $VAR, ${VAR}
                  %VAR%

                default := False

            **uservars**:
                Replaces special user variables as
                path-prefix. Currently support: ::

                  ~ (tilde)
                  $HOME, ${HOME}
                  %HOME%

                default := False

            **shrink**:
                Drops resulting empty items.

                default := True

            **split**:
                Forces split of multiple paths items within
                one item into separate item entries.

                default := True

            **stripquote**:
                Removes paired triple-quotes of protected/masked
                string sections. ::

                   "/a/'''head:'''/c" => "/a/head:/c"

                default := False

            **withinItemOnly**:
                Performs any action for each
                item of 'plist' only.

                default := False

    Returns:
        When successful returns 'True', else returns either 'False',
        or raises an exception.

    Raises:
        passed through exceptions:
    """
    if plist == None:
        plist = sys.path

    # _links = kargs.get('links', False)

    _abs = kargs.get('abs', False)
    _existent = kargs.get('existent', False)
    _ne = kargs.get('nonexistent', False)
    _normpath = kargs.get('normpath', False)
    _nr = kargs.get('nonredundant', False)
    _redundant = kargs.get('redundant', True)
    _rel = kargs.get('rel', False)
    _reverse = kargs.get('reverse', False)
    _shrink = kargs.get('shrink', True)
    _split = kargs.get('split', True)
    _user = kargs.get('uservars', False)
    _vars = kargs.get('shellvars', False)
    _wio = kargs.get('withinItemOnly', False)
    _stripquote = kargs.get('stripquote', True)


    def clearIt(px, ref=None):
        """the actual workhorse

        px:  patch to process
        ref: reference path
        """
        if _abs:
            px = os.path.abspath(px)
        if _existent and os.path.exists(px):
            return
        if _ne and not os.path.exists(px):
            return
        if _normpath:
            px = os.path.normpath(px)
        if _rel:
            px = getpythonpath_rel(px, plist)
        return px

    def clrred(x):
        """clear redundancies"""
        if x in clearpath._clearlst:
            return
        clearpath._clearlst.append(x)
        return x

    #
    # --------------------------------------------
    #
    if not _wio:
        clearpath._clearlst = []
    pn = plist[:]  # input list

    if _reverse:  # revese input list
        pn.reverse()
    for p in range(len(plist)):
        plist.pop()  # clear source for new items - in place of caller

    #
    # split items into sub items as separate new items
    if _split:
        _pn = []
        for p in pn:
            if p:
                for px in splitapppathx(p):
                    _pn.append(px)
        pn = _pn

    #
    # work out items
    for p in pn:  # each item

        # within item only
        if _wio:
            clearpath._clearlst = []
        pn = ''

        # reverse order
        if _reverse:
            plx = splitapppathx(p, stripquote=_stripquote)
            plx.reverse()
        else:
            plx = splitapppathx(p, stripquote=_stripquote)

        # clear redundancies
        for p1 in plx:
            if _vars or _abs:
                p1 = os.path.expandvars(p1)

            if _user or _abs:
                p1 = os.path.expanduser(p1)

            if _redundant:
                px = clrred(clearIt(p1))
            else:
                px = clearIt(p1)
            if _shrink:
                if px:
                    pn += os.pathsep + px
            else:
                if px:
                    pn += os.pathsep + px
                else:
                    pn += os.pathsep

        if pn:
            pn = pn[1:]
        if _reverse and pn:

            # plx = pn.split(os.pathsep)
            plx = splitapppathx(pn, stripquote=_stripquote)
            plx.reverse()
            pn = os.pathsep.join(plx)

        # shrink
        if _shrink:
            if pn:
                plist.append(pn)
        else:
            plist.append(pn)

    if _reverse:
        plist.reverse()


def expandpath(*paths, **kargs):
    """Splits, expands and normalizes a list of paths and search paths.

    **REMINDER**: Non-existent path entries are dropped.

    The input list '*\*paths*' may contain mixed entries of:

    * search paths - combined by *os.pathsep*
    * wildcards-paths containing '*literal*', '*glob*', and '*regexpr*' parts
    * inserted user directory
    * inserted environment variables
    * file and directory paths

    The resulting normalized *list* contains in case of matches
    one path in each entry by the following algorithm.

    .. code-block:: text

       Expand contained:

       1. expand environment variables
       2. expand user directory
       3. check and use if exists, else continue

       If wildcards are selected continue with

       4. split and resolve paths and remove quotes - *stripquote*
       5. expand *literals* and *globs*
       6. expand *literals* and *regexpr*

    Args:

        **paths**:
            A list of paths and search paths to be expanded. For
            supported pattern of following table refer to parameter
            *wildcards*.

            +---------+--------------+-----------+---------+-----------+
            | type    | *W_LITERAL*  | *W_GLOB*  | *W_RE*  | *W_FULL*  |
            +=========+==============+===========+=========+===========+
            | literal | X            | X         | X       | X         |
            +---------+--------------+-----------+---------+-----------+
            | glob    |              | X         |         | X         |
            +---------+--------------+-----------+---------+-----------+
            | re      |              |           | X       | X         |
            +---------+--------------+-----------+---------+-----------+

            default := *W_RE*  # see parameter **wildcards**

        kargs:

            **dironly**:
                Contained file name paths are cut to their *dirname*. ::

                   expandvars := (True | False)

                default := *False*

            **expandvars**:
                Expand embedded environment variables. ::

                   expandvars := (True | False)

                default := True

            **expanduser**:
                Expand embedded user directories. ::

                   expandvars := (True | False)

                default := True

            **isDir**:
                Returns directories only.

                default := all

            **isFile**:
                Returns files only.

                default := all

            **nestclear**:
                Clear nested subdirectories ::

                   expandvars := (True | False)

                when *True*, e.g. ::

                   /a/b:/a/b/c::/a/b/c => /a/b

                default := *False*

            **regexprspandir**:
                Controls whether regexpr may span multiple
                directories, thus handling os.path.sep as
                ordinary chars.

                This in particular controls the technical
                implementation of the iterative path
                resolution for  paths by intermixed
                wildcards.

                * True:

                  The treatment of path seperators within
                  regexpr has to be assured by the caller.

                * False:

                  The regular experessions are resolved
                  in chunks seperated by the path seperator.
                  Thus each chunk is technically wrapped by
                  the re-module:
                  ::

                    '<regexpr>' + os.path.sep+'$'

            **strip**:
                Reduces by dropping redundancies. The strip parameter
                influences the match of regular expressions, which just
                do a pattern match, thus hit null-separator directories too.
                The strip of these prevents from unwanted matches on separator
                characters. ::

                   strip := (
                        True      # clear null-separators
                      | False     # no strip at all
                      | all       # clear any redundancy
                      | contain   # contained sub directories
                      | multiple  # multiple occurance
                   )

                default := True

            **spf**:
                Source platform, defines the input syntax domain.
                For the syntax refer to API in the manual at :ref:`spf <OPTS_SPF>`.

                For additi0onal details refer to
                :ref:`tpf and spf <TPF_AND_SPF>`,
                `paths.getspf() <paths.html#getspf>`_,
                :ref:`normapppathx() <def_normapppathx>`,
                `normpathx() <paths.html#normpathx>`_.

            **wildcards**:
                Controls the type of path evaluation.
                Supported *paths* values types are: ::

                    wildcards := (
                        W_LITERAL      # literal existence check
                        | W_GLOB       # globs, contains W_LITERAL
                        | W_RE         # re, contains W_GLOB
                        | W_FULL       # re
                    )

                Expects mixed path names with *literals*, *globs*, and *regexpr*.

                default := *W_RE*

    Returns:
        In case of success a list with directory entries with
        splitted search paths. An empty list when no results.

    Raises:
        PathToolsError

        pass-through
    """
    res = []

    _dironly = kargs.get('dironly')
    _escape = kargs.get('escape', False)
    _expanduser = kargs.get('expanduser', True)
    _expandvars = kargs.get('expandvars', True)
    _isdir = kargs.get('isDir', None)
    _isfile = kargs.get('isFile', None)
    _nestclear = kargs.get('nestclear')
    _spf = kargs.get('spf')
    _splitglobregexpr = kargs.get('splitglobregexpr')
    _tpf = kargs.get('tpf')
    _wildcards = kargs.get('wildcards', W_RE)

    _tsep, _tpsep, tpf, _tpfn, _apre = filesysobjects.paths.gettpf(_tpf)

    # TODO:
    _strip = kargs.get('strip', True)
    if _strip not in (True, False, 'all', 'contain', 'multiple'):
        raise PathToolsError("ERROR:Unknow param: strip=" + str(_strip))

    _pl = list(paths)
    clearpath(_pl, stripquote=False)
    if _escape:
        _pl = [escapepathx(x) for x in _pl]

    # split search lists of contained multiple paths
    _pl = []
    for _plx in paths:
        _plx = splitapppathx(_plx, stripquote=False, spf=_spf, tpf=_tpf)
        _pl.extend(_plx)

    clearpath(_pl, stripquote=False)
    if _escape:
        _pl = [escapepathx(x) for x in _pl]

    for pi in _pl:  # list of paths
        #
        # *** 1. expand environment variables
        #
        if _expandvars:
            pi = os.path.expandvars(pi)

        #
        # *** 2. expand user directory
        #
        if _expanduser:
            pi = os.path.expanduser(pi)

        #
        # 3. *** check and use if exists, else continue
        #
        if os.path.exists(pi):
            # no need for search
            res.append(pi)
            continue

        if _wildcards == W_LITERAL_QUOTED:  # literal with quotes
            lppath = normapppathx(
                    pi, stripquote=True, strip=False, spf=_spf, tpf=_tpf,
                    delnulpsep=False
                )
            if os.path.exists(lppath):
                res.append(lppath)

        elif _wildcards:  # requires recursive file system evaluation -> performance degradation

            #
            # *** 4. split, strip and unquote
            #
            lppath = list(splitapppathx(pi, stripquote=True, spf=_spf, tpf=_tpf))

            for i in reversed(lppath):
                _gr = split_re_glob(i)
                _ix = []

                if _gr[1]:
                    # the non-glob-part for '*-globbing' and post-filtering
                    _ix.extend(_gr[1])

                if len(i) > 1:
                    _ind = lppath.index(i)
                    lppath.pop(_ind)
                    for _ixx in reversed(_ix):
                        lppath.insert(_ind, _ixx)
                elif i == '':
                    if _strip:
                        _ind = lppath.index(i)
                        if _ind:
                            # first is root-slash
                            lppath.pop(_ind)

            _idx = _lenppath = len(lppath)  # abort endless recursion

            #
            # ** now we have the non-quoted effective path expression
            #

            #
            # *** 5. expand literals and globs
            #
            pparts = ''  #: largest-glob
            gparts = ''

            globtore = False

            if lppath:
                # re present
                if _gr[0]:
                    # the glob part for explicit 'globbing'
                    if RTE & RTE_WIN32:
                        pparts = _tsep.join(_gr[0])
                    else:
                        pparts = _tsep + _tsep.join(_gr[0])

                gparts = pparts

            elif _gr[0]:
                # glob only
                if _gr[0] != '':
                    if RTE & RTE_WIN32:
                        lppath = [_tsep.join(_gr[0])]
                    else:
                        lppath = [_tsep + _tsep.join(_gr[0])]
                else:
                    lppath = [_tsep.join(_gr[0])]

            #
            pparts = glob_to_re(pparts)


            _search_set_next = []
            for px in lppath:  # 3. expand literals and *globs* - walk the path top-down
                _idx -= 1

                # includes Posix-netapp and MS-shares
                if px == '' and _idx > 0 and _strip:
                    continue
                elif pparts == _tsep and px != '':
                    _p = pparts + px
                else:
                    if RTE & RTE_WIN32:
                        try:
                            if px[1] == ':':
                                _p = px
                            else:
                                _p = pparts + _tsep + px
                        except IndexError:
                            _p = pparts + _tsep + px
                    elif pparts:
                        _p = pparts + _tsep + px
                    else:
                        _p = px

                if _idx > 0:
                    # make match criteria a bit stronger
                    _p += _tsep

                if _wildcards & W_RE:
                    # try to resolve ambiguity between DSL, of e.g. [^x] and [!x]
                    # priority on W_RE here
                    _subre = split_re_glob(_p)

                    if _debug > 3:
                        print("DBG:subre = " + str(_subre))

                    if not _subre[1]:
                        # glob/literal only
                        try:
                            # check match by glob for current path-part
                            _lglob = glob.iglob(_p)  # check only for a match
                            _pi = next(_lglob)  # test a match
                            pparts = _p
                            gparts = _p
                        except StopIteration:
                            gparts += _tsep + '***'
                            _pi = None  # found first segment that did not match

                    else:
                        # has *re*
                        _head = False
                        _lpre = len(_tsep.join(_subre[0]))
                        for chk  in _subre[1]:
                            _lpre += len(_tsep + chk)
                            if chk and chk[0] in ('*',):
                                if not _head:
                                    _head = True
                                    sys.stderr.write(
                                        'WARNING:Leading wildcard without char for re:\n'
                                        )

                                sys.stderr.write(
                                    '  -> %s\n'
                                    %(
                                        str(_p)
                                    )
                                )
                                sys.stderr.write(' ' * _lpre + '^\n')

                        # has a non-glob/non-literal postfix, so search and filter
                        gparts += _tsep + '***'
                        _pi = None  # found first segment that did not match

                    pparts += _tsep + px

                    if _pi:  # current segment is literal part of the path
                        if _idx <= 0:  # if current set are leafs
                            res.append(_pi)  # add checked leaf
                            for _lg in _lglob:  # collect remaining leafs
                                res.append(_lg)

                else:
                    try:  # check match by glob for current path-part
                        _lglob = glob.iglob(_p)  # check only for a match
                        _pi = next(_lglob)  # test a match
                        pparts = _p

                        gparts = _p
                    except StopIteration:
                        gparts += _tsep + '***'
                        _pi = None  # found first segment that did not match

                    if _pi:  # current segment is literal part of the path
                        if _idx <= 0:  # if current set are leafs
                            res.append(_pi)  # add checked leaf
                            for _lg in _lglob:  # collect remaining leafs
                                res.append(_lg)

                if _wildcards & W_RE:  # current level is possibly matched by expansion
                    # entering next level of expansion

                    #
                    # *** 6. expand regexpr
                    #
                    _s = _search_set_next[:] # use search set from previous - if there
                    try:
                        _sext = glob.glob(gparts)  # expand globs for post matching of re
                        _s.extend(_sext)  # current roundexpanded
                    except StopIteration:
                        pass

                    if gparts.endswith('***') and (px.startswith('.') or px.startswith('[.]')):  # is shifted glob for re
                        try:
                            _sext = glob.glob(os.path.dirname(gparts) + _tsep + '.*')
                            _s.extend(_sext)  # current round expanded
                        except StopIteration:
                            pass


                    _search_set_next = []  # prepare next round
                    matched = False
                    for z in _s:

                        if not _tpfn & RTE:
                            z = normpathx(z, tpf=_tpfn)

                        if pparts[-1] != r'$':
                            a = escapepathx(pparts + r'$', force=True)
                        else:
                            a = escapepathx(pparts, force=True)
                        a = escapepathx(a, force=True)
                        b = escapepathx(z, force=True)
                        if not re.match(a, b):
                            if _debug > 3:
                                print("DBG:current-raw = " + str(z))
                                print("DBG:current-esc = " + str(b))
                                print("DBG:regexpr     = " + str(a))

                            continue
                        else:
                            if _debug > 3:
                                print("DBG:current-raw = " + str(z))
                                print("DBG:matched by  = " + str(pparts))

                        _search_set = glob.glob(z)  # pick up first search subset
                        while _search_set:
                            p0 = _search_set.pop(0)  # next item from search list
                            p0d = os.path.dirname(p0)  # parent node for appending re
                            if os.path.isfile(p0):  # nothing more to traverse
                                # it is a potential regexpr
                                # try to search for paths matching the LHS-part of
                                # the maximum of the remaining path by regexpr
                                try:
                                    _pat = escapepathx(p0d + _tsep + px + r'$', force=True)
                                    _pat = escapepathx(_pat, force=True, charback=True)

                                    if not _idx > 0 and re.match(_pat, escapepathx(p0, force=True)):

                                        if _debug > 3:
                                            print("DBG:res[i] = " + str(p0))

                                        res.append(p0)
                                        matched = True

                                except sre_constants.error as e:
                                    if e.pattern is not None and e.pos is not None:
                                        e.msg += '\ncompile-error:\n in: %s\n     %s^\n  => %s' % (
                                            str(escapepathx(p0d + _tsep + px + r'$')),
                                            ' ' * (e.pos+1),
                                            str(escapepathx(p0d + _tsep + px + r'$')[:e.pos+1])
                                        )
                                        raise PathError(str(e) + '\n' + e.msg)
                                continue

                            try:
                                _pat = escapepathx(p0d + _tsep + px + r'$', force=True)
                                _pat = escapepathx(_pat, force=True, charback=True)
                                if re.match(_pat, escapepathx(p0, force=True)):  # check re match
                                    if _idx <= 0:  # it's a leaf
                                        res.append(p0)
                                        matched = True
                                    else:  # intermediate branch, set it for next round
                                        _search_set_next.append(p0)

                            except sre_constants.error as e:
                                if e.pattern is not None and e.pos is not None:
                                    e.msg += '\ncompile-error:\n in: %s\n     %s^\n  => %s' % (
                                        str(escapepathx(p0d + _tsep + px + r'$')),
                                        ' ' * (e.pos+1),
                                        str(escapepathx(p0d + _tsep + px + r'$')[:e.pos+1])
                                    )
                                    raise PathError(str(e) + '\n' + e.msg)

                    if not matched and not _search_set_next:
                        break

        else:
            # literal W_LITERAL
            if os.path.exists(pi):
                res.append(pi)

    # normalize the result
    res = [filesysobjects.apppaths.normpathx(x, tpf=_tpf,) for x in res]

    # TODO: add app and glob/re-support
    if _dironly:
        _tpfn = filesysobjects.paths.gettpf(_tpf)[3]
        if _tpfn & RTE_WIN32:
            import ntpath
            for rx in range(len(res)):
                if not _tsep.isdir(res[rx]):
                    res[rx] = ntpath.dirname(res[rx], _tpf, **kargs)
                if not res[rx]:
                    res.pop(rx)
        elif _tpfn & RTE_POSIX:
            import posixpath
            for rx in range(len(res)):
                if not os.path.isdir(res[rx]):
                    res[rx] = posixpath.dirname(res[rx])
                if not res[rx]:
                    res.pop(rx)
        else:
            for rx in range(len(res)):
                if not os.path.isdir(res[rx]):
                    res[rx] = posixpath.dirname(res[rx])
                res[rx] = os.path.dirname(res[rx])
                if not res[rx]:
                    res.pop(rx)

    # TODO: integrate into the algorithm
    if _isdir or _isfile:
        _res = []
        for r in res:
            if _isdir and os.path.isdir(r):
                _res.append(r)
            elif _isfile and os.path.isfile(r):
                _res.append(r)
        res = _res

    return res
