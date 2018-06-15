# -*- coding: utf-8 -*-
"""Platform independent path names for configuration files.
"""
from __future__ import absolute_import
import os
import re

import pysourceinfo.fileinfo

from filesysobjects import W_FULL, W_GLOB, W_LITERAL, W_LITERAL_QUOTED, W_RE
from filesysobjects.userdata import getdir_userhome, getdir_userconfigdata
from filesysobjects.osdata import getdir_osconfigdata, getdir_osappconfigdata
from filesysobjects.pathtools import findrelpath_in_searchpath, expandpath,findrelpath_in_searchpath_iter

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez" \
                " @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.20'
__uuid__ = "4135ab0f-fbb8-45a2-a6b1-80d96c164b72"

__docformat__ = "restructuredtext en"


class ConfigPath(object):
    """A small class that manages the search for configuration files
    located at standard paths.
    """
    def __init__(self, **kargs):
        """Initializes the search paths.

        Args:
            kargs:

                **append**:
                    A list of search paths to be added to the standard search.

                **filext**:
                    A list of default file extensions to be used in search
                    operations. Default ::

                       filext := [ini', 'conf', 'json', 'xml']

                **prepend**:
                    A list of search paths to be checked at the beginning of
                    the standard search.

                **replace**:
                    A list of search paths to replace the standard search.

        Returns:
            object/None
        Raises:
            pass-through
        """
        self.replace = kargs.get('replace')
        self.prepend = kargs.get('prepend')
        self.append = kargs.get('append')

        self.fext = kargs.get('filext', ['.ini', '.conf', '.json', '.xml', '.yaml'])

    def __repr__(self):
        """Returns the current list of search path names. """
        return repr(self.get_config_path_list())

    def __str__(self):
        """Returns the formatted list of current search path names. """
        ret = "[\n"
        for l in self.get_config_path_list():
            ret += ' ' * 4 + '"' + str(l) + '",\n'
        ret += "]"
        return ret

    def get_config_filepath(self, conf):
        """Returns the first matched configuration file.

        The standard search hierarchy is:

        0. absolute file path: <conf>
        1. relative to current workdir: <conf>

        2. USER context by: getdir_userconfigdata()/<conf>
        3. HOME of user: getdir_userhome()/<conf>
        4. Application config: getdir_osappconfigdata()/<conf>
        5. OS config: getdir_osappconfigdata()/<conf>

        6. the final default from distribution:
            pysourceinfo.fileinfo.getcaller_package_filepathname()/<conf>
        7. the final default from module:
            pysourceinfo.fileinfo.getcaller_pathname()/<conf>

        The priorities 6 + 7 are the last, because the caller itself could be
        a library sub call, so is not necessarily closely related to the
        calling application.

        This could be altered by the parameters *replace*, *prepend*, and *append*. ::

           if replace:
              replace standard by list
           if prepend:
              prepend any list(standard/replace)
           if append:
              append to any list(standard/replace)


        Args:
            **conf**:
                Configuration file name including suffix.
                Valid *conf* file name wildcard types are:

                +---------+----+
                | literal | X  |
                +---------+----+
                | re      | -- |
                +---------+----+
                | glob    | X  |
                +---------+----+

        Returns:
            The first file path name matched by *conf*,
            else None.

        Raises:
            pass-through
        """
        return findrelpath_in_searchpath(conf, self.get_config_path_list(), isFile=True)

    def get_config_filepath_list_old(self, conf=None):
        """Returns a list of matched configuration files.

        Args:
            **conf**:
                Search expression for configuration file names.
                Valid *conf* file name wildcard types are:

                +---------+----+
                | literal | X  |
                +---------+----+
                | re      | -- |
                +---------+----+
                | glob    | X  |
                +---------+----+

        Returns:
            A list of file path names matched by 'conf'.

        Raises:
            pass-through
        """
        if os.path.isabs(conf):  # absolute
            if os.path.exists(conf):
                if os.path.isfile(conf):
                    return [conf]
                ret = []
                for e in self.fext:
                    f = expandpath(conf + os.sep + '*' + e, isFile=True)
                    if f:
                        ret.extend(list(f))
                return ret
            return expandpath(conf, isFile=True)
        else:
            sp = self.get_config_path_list()
            if os.path.splitext(conf) in self.fext:
#                return list(findrelpath_in_searchpath_iter(conf, sp, isFile=True))
                return list(expandpath(conf, isFile=True))

            elif not conf or conf == '*':
                ret = []
                for e in self.fext:
 #                   f = findrelpath_in_searchpath_iter('*' + e, sp, isFile=True)
                    f = findrelpath_in_searchpath_iter('*' + e, sp, isFile=True)
                    if f:
                        ret.extend(list(f))
                return ret

            else:
                ret = []

  #              f = findrelpath_in_searchpath_iter(conf, sp, isFile=True)
                f = findrelpath_in_searchpath_iter(conf, sp, isFile=True)
                if f:
                    return list(f)

                for e in self.fext:
#                    f = findrelpath_in_searchpath_iter(conf + e, sp, isFile=True)
                    f = findrelpath_in_searchpath_iter(conf + e, sp, isFile=True)
                    if f:
                        ret.extend(list(f))
                return ret

    def get_config_filepath_list(self, conf=None, **kargs):
        """Returns a list of matched configuration files.

        Args:
            **conf**:
                Search expression for configuration file names.
                Valid *conf* file name wildcard types are:

                +---------+----+
                | literal | X  |
                +---------+----+
                | re      | -- |
                +---------+----+
                | glob    | X  |
                +---------+----+

            kargs:
                **isDir**:
                    Include directories.

                    default := False

                **isFile**:
                    Include files.

                    default := True

        Returns:
            A list of file path names matched by 'conf'.

        Raises:
            pass-through
        """
        _isfile = kargs.get('isFile', True)
        _isdir = kargs.get('isDir', False)
#        _wildcards = kargs.get('wildcards', W_FULL)
        _wildcards = kargs.get('wildcards', W_LITERAL_QUOTED|W_GLOB|W_RE)

        ret = []
        if os.path.isabs(conf):  # absolute
            if os.path.exists(conf):
                if os.path.isfile(conf):
                    return [conf]
                for e in self.fext:
                    f = expandpath(
                        conf + os.sep + '*' + e,
                        isFile=_isfile,
                        isDir=_isdir,
                        wildcards=_wildcards,
                        )
                    if f:
                        ret.extend(list(f))
                return ret
            return expandpath(
                conf,
                isFile=_isfile,
                isDir=_isdir,
                wildcards=_wildcards,
                )
        else:
            sp = self.get_config_path_list()
            if os.path.splitext(conf)[1] in self.fext:
#                return list(findrelpath_in_searchpath_iter(conf, sp, isFile=True))

#                 f = expandpath(
#                     conf,
#                     isFile=_isfile,
#                     isDir=_isdir,
#                     wildcards=_wildcards,
#                     )
#                 if f:
#                     ret.extend(list(f))
#                 return ret

                for s in sp:
                    f = expandpath(
                        s + os.sep + conf,
                        isFile=_isfile,
                        isDir=_isdir,
                        wildcards=_wildcards,
                        )
                    if f:
                        ret.extend(list(f))
                return ret

#                     f = expandpath(s + os.sep + '*' + e, isFile=True)
#                     if f:
#                         ret.extend(list(f))

#             elif not conf or conf == '*':
#                 for e in self.fext:
#  #                   f = findrelpath_in_searchpath_iter('*' + e, sp, isFile=True)
#                     for s in sp:
#                         f = expandpath(s + os.sep + '*' + e, isFile=True)
#                         if f:
#                             ret.extend(list(f))
#                 return ret

            else:
                ret = []

#              f = findrelpath_in_searchpath_iter(conf, sp, isFile=True)
                for s in sp:
                    f = expandpath(
                        s + os.sep + conf,
                        isFile=_isfile,
                        isDir=_isdir,
                        wildcards=_wildcards,
                        )
                    if f:
                        ret.extend(list(f))
                if ret:
                    return ret

                for e in self.fext:
#                    f = findrelpath_in_searchpath_iter(conf + e, sp, isFile=True)
                    for s in sp:
                        f = expandpath(
                            s + os.sep + conf + e,
                            isFile=_isfile,
                            isDir=_isdir,
                            wildcards=_wildcards,
                            )
                        if f:
                            ret.extend(list(f))

#                     f = findrelpath_in_searchpath_iter(conf + e, sp, isFile=True)
#                     if f:
#                         ret.extend(list(f))
                return ret

    def get_config_path_list(self):
        """Returns the list of current search path entries for configuration files.

        Args:
            None

        Returns:
            The list of current search paths.

        Raises:
            pass-through
        """
        sp = ap = pre = None
        res = []

        if self.replace:
            if type(self.replace) is list:
                sp = expandpath(*self.replace)
            else:
                sp = expandpath(self.replace)
        if self.prepend:
            if type(self.prepend) is list:
                pre = expandpath(*self.prepend)
            else:
                pre = expandpath(self.prepend)
        if self.append:
            if type(self.append) is list:
                ap = expandpath(*self.append)
            else:
                ap = expandpath(self.append)

        if self.replace:
            if pre:
                if type(pre) is list:
                    res = pre
                else:
                    res.append(pre)
            if sp:
                if type(sp) is list:
                    res.extend(sp)
                else:
                    res.append(sp)
            if ap:
                if type(ap) is list:
                    res.extend(ap)
                else:
                    res.append(ap)

        else:
            if pre:
                if type(pre) is list:
                    res = pre
                else:
                    res.append(pre)

            res.append(getdir_userconfigdata())
            res.append(getdir_userhome())
            res.append(getdir_osappconfigdata())
            res.append(getdir_osconfigdata())
            res.append(pysourceinfo.fileinfo.getcaller_package_filepathname())
            res.append(pysourceinfo.fileinfo.getcaller_pathname())

            if ap:
                if type(ap) is list:
                    res.extend(ap)
                else:
                    res.append(ap)

        return res

    def get_filepathname_by_ext(self, fnam, fext=[]):
        """Gets the file path name by specified list of
        extensions. Searches the defined path list by
        *self*, returns the first match.

        Args:
            **fnam**:
                File name. Valid types are ::

                   fnam := (
                        <absolute-file-path-name>
                      | <relative-file-path-name>
                      | <filename-with-suffix>
                      | <filename-without-suffix>
                   )

                Matches of file path name without additional suffix
                are returned immediately.

                Valid *fnam* file name wildcard types are:

                +---------+----+
                | literal | X  |
                +---------+----+
                | re      | -- |
                +---------+----+
                | glob    | X  |
                +---------+----+

            **fext**:
                File extension list. Each will be returned in the
                order of the provided extensions, grouped in the
                order of the provided search paths.

        Returns:
            The first found absolute file path name.

        Raises:
            pass-through
        """
        if not fext:  # use defaults
            fext = self.fext

        # try absolute match
        if os.path.exists(fnam):
            return os.path.abspath(fnam)

        _suf = re.sub(r'^.*?[^.]*', '', fnam)
        if _suf:

            # check whether has a known extension already, than use only this
            _f = self.get_config_filepath(fnam)
            if _f:
                return _f

        else:
            # search in standard locations + added custom
            for p in self.get_config_path_list():
                for e in fext:  # for each extension
                    _f = self.get_config_filepath(p + os.sep + fnam + e)
                    if _f and os.path.exists(_f):
                        return _f

            # search in standard locations + added custom
            for p in self.get_config_path_list():
                _f = self.get_config_filepath(p + os.sep + fnam)
                if _f and os.path.exists(_f):
                    return _f

        # try simple expansion - be careful with wildcards
        _f = self.get_config_filepath(fnam)
        try:
            if  _f and os.path.exists(_f):
                return _f
        except Exception:
            pass

