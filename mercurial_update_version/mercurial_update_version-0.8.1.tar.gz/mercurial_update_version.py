# -*- coding: utf-8 -*-
#
# update_version: automatically fix version numbers while tagging
#
# Copyright (c) 2015 Marcin Kasperski <Marcin.Kasperski@mekk.waw.pl>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# See README.txt for more details.

"""Let 'hg tag' automatically update version numbers in your code.

Manually maintaining various VERSION variables is both painful and
mistake-prone.  This extension automatically updates those values
whenever you tag a new release.

For example, write in your repository ``.hg/hgrc``::

    [update_version]
    active = true
    language = python
    tagfmt = dotted

and whenever you type::

    hg tag 0.3.7

files like setup.py, __init__.py, and version.py will be scanned for
version variables, and those will be updated to contain ``0.3.7``.

There are more usage options (enabling for many repositories
selected by location, configuring which files are scanned and
which expressions are updated). See extension README.txt or
http://bitbucket.org/Mekk/mercurial-update_version/
"""

# pylint: disable=unused-argument,no-self-use,too-few-public-methods

from mercurial import commands, util, scmutil, node
from mercurial.i18n import _

import re
import os
import sys


def import_meu():
    """Importing mercurial_extension_utils so it can be found also outside
    Python PATH (support for TortoiseHG/Win and similar setups)"""
    try:
        import mercurial_extension_utils
    except ImportError:
        my_dir = os.path.dirname(__file__)
        sys.path.extend([
            # In the same dir (manual or site-packages after pip)
            my_dir,
            # Developer clone
            os.path.join(os.path.dirname(my_dir), "extension_utils"),
            # Side clone
            os.path.join(os.path.dirname(my_dir), "mercurial-extension_utils"),
        ])
        try:
            import mercurial_extension_utils
        except ImportError:
            raise util.Abort(_("""Can not import mercurial_extension_utils.
Please install this module in Python path.
See Installation chapter in https://bitbucket.org/Mekk/mercurial-dynamic_username/ for details
(and for info about TortoiseHG on Windows, or other bundled Python)."""))
    return mercurial_extension_utils


meu = import_meu()  # pylint: disable=invalid-name

# pylint:disable=fixme,line-too-long,invalid-name
#   (invalid-name because of ui and cmdtable)

############################################################
# Interfaces / base classes
############################################################


class Language(object):
    """Represents language rules"""

    def repo_setup(self, ui, repo):
        """
        Called before first action on given repo, once.  Can
        prepare (and save on attributes)some repository-state-level
        data (like info about current revision)
        """
        pass

    def size_limit(self):
        """
        Max size of the file being edited (bigger are skipped).
        Can be overridden.
        """
        return 16384

    def format_version_no(self, version_parts):
        """
        To be overridden. Formats version string to be used in code.

        :param version_parts: tuple like ("1", "2") or ("1", "7", "04")
                - version number extracted from tag
        :return: formatted string appropriate for language or None
                 if given version is invalid for it (too short, to long etc)
        """
        raise util.Abort(_("Not implemented"))

    def worth_checking(self, repo_path, repo_root):
        """
        To be overridden. Checks whether given file should be
        checked (matches name pattern, depth in repo etc).
        Called by default locate_files, not used if locate_files
        is overridden.

        :param repo_path: File name (relative to repo root)
        :param repo_root: Repository root (full path)
        :return: True if file should be considered, False if not
        """
        raise util.Abort(_("Not implemented"))

    def locate_files(self, ui, repo):
        """Yields all files, which should be checked.

        Can be overridden, by default iterates over all repository
        files (as returned by manifest) and filters them by worth_checking
        and by size limit.

        Yielded names are pairs of path relative repo root and full path
        """
        size_limit = self.size_limit()
        for repo_path in sorted(self.manifest(repo)):
            if self.worth_checking(repo_path, repo.root):
                full_path = os.path.join(repo.root, repo_path)
                size = os.path.getsize(full_path)
                if size <= size_limit:
                    yield repo_path, full_path
                else:
                    ui.debug(_("update_version: Ignoring big file %s (%d bytes > %d limit)\n") % (repo_path, size, size_limit))

    def update_line(self, line, version, repo_path):
        """Edits single line.

        To be overridden. Called by default update_file.

        :param line: complete input line, without final newline
        :param version: version number to save, whatever
               format_version_no returned
        :param repo_path: File name (relative to repo root)
        :return: updated line or None if no changes were needed
               (return updated line if it already contains proper
               version number). Returned value should not have final newline
        """
        raise util.Abort(_("Not implemented"))

    def update_file(self, ui, repo, repo_path, full_path, version, dry_run=False):
        """Edits given file, fixing version to given number

        Can be overridden. By default iterates over file lines
        and calls update_line

        :param full_path: file to edit, full absolute path
        :param repo_path: file to edit, relative repo root
        :param version: version number, whatever format_version_no returned
        :param dry_run: does not save
        :return: list of triples (lineno, before, after)
        """
        file_lines = []
        changes = []
        # basename = os.path.basename(repo_path)

        with open(full_path, "r") as input_fd:
            line_no = 0
            for line in input_fd:
                line_no += 1
                stripped_line = line.rstrip("\r\n")
                fixed_line = self.update_line(stripped_line, version, repo_path)
                if fixed_line is None:
                    file_lines.append(line)
                else:
                    # Reintroduce final newline
                    fixed_line += line[len(stripped_line):]
                    file_lines.append(fixed_line)
                    if fixed_line != line:
                        changes.append((line_no, line, fixed_line))
                    else:
                        ui.status(_("update_version: Line %d in %s already contains proper version number\n") % (line_no, repo_path))

        if changes:
            if not dry_run:
                with open(full_path, "w") as output:
                    output.writelines(file_lines)
        return changes

    def manifest(self, repo):
        """Helper. Yields names (repo-root-relative) of all repository files"""
        ctx = repo['.']
        for fname in ctx.manifest():
            yield fname


class TagFmt(object):
    """Represents tag numbering format"""

    sample = ""

    def extract_no(self, tag_text):
        """Returns tag number or None if tag does not match pattern

        :param tag_text: whatever used gave
        :return: tag number as string tuple like ("1","0","2") or ("3","08") or None
        """
        raise util.Abort(_("Not implemented"))


############################################################
# Languages
############################################################

known_languages = {}


class LanguagePython(Language):
    """Python language rules."""

    tested_file_names = ['setup.py', 'version.py', '__init__.py']

    def format_version_no(self, version_parts):
        return ".".join(str(vp) for vp in version_parts)

    def worth_checking(self, repo_path, repo_root):
        return os.path.basename(repo_path) in self.tested_file_names

    def update_line(self, line, version, repo_path):
        match = self.re_version_line.search(line)
        if match:
            return match.group('before') + version + match.group('after')
        else:
            return None

    re_version_line = re.compile(r'''
    ^   (?P<before>
             \s* VERSION \s* = \s*
             (?P<quote> ["'] )      )
        (?P<version> \d+(?:\.\d+)+  )
        (?P<after>
             (?P=quote)   # closing quote
             .* )
    $ ''', re.VERBOSE)


known_languages['python'] = LanguagePython()


class LanguagePerl(Language):
    """Perl language rules."""

    def format_version_no(self, version_parts):
        if len(version_parts) == 2:
            return ".".join(version_parts)
        if len(version_parts) == 3:
            txt = version_parts[0] + "."
            for item in version_parts[1:]:
                if len(item) > 2:
                    return None
                txt += "0" * (2 - len(item)) + item
            return txt
        return None

    def worth_checking(self, repo_path, repo_root):
        return repo_path.endswith(".pm") \
            or repo_path.endswith(".pl") \
            or repo_path.endswith(".pod") \
            or os.path.basename(repo_path) == "dist.ini"

    def update_line(self, line, version, repo_path):
        if repo_path.endswith(".ini"):
            rgxps = self.re_ini_rgxps
        else:
            rgxps = self.re_perl_rgxps
        for rgxp in rgxps:
            match = rgxp.search(line)
            if match:
                return match.group('before') + version + match.group('after')
        return None

    re_ini_rgxps = [
        re.compile(r'''
        ^   (?P<before>
                 \s* version \s* = \s*  )
        (?P<version> \d+(?:\.\d+)+  )
        (?P<after>
             \s*  (?:\#.*)?  )
        $ ''', re.VERBOSE),
    ]

    re_perl_rgxps = [
        re.compile(r'''
        ^  (?P<before>
               \s* (?: my | our | ) \s*
               \$ VERSION \s* = \s*
               (?P<quote> ["'] )         )
           (?P<version> \d+\.\d+         )
           (?P<after>
               (?P=quote)   # closing quote
               .* )
        $ ''', re.VERBOSE),
        re.compile(r'''
        ^  (?P<before>
               \s* use \s+ constant \s+ VERSION \s* => \s*
               (?P<quote> ["'] )         )
           (?P<version> \d+\.\d+         )
           (?P<after>
               (?P=quote)   # closing quote
               .* )
        $ ''', re.VERBOSE),
        re.compile(r'''
        ^  (?P<before> \s* Version \s+ )
           (?P<ver> \d+\.\d+           )
           (?P<after> \s*              )
           $
        ''', re.VERBOSE),
    ]


known_languages['perl'] = LanguagePerl()


class LanguageJavaScript(Language):
    """JavaScript language rules."""

    def format_version_no(self, version_parts):
        return ".".join(version_parts)

    def worth_checking(self, repo_path, repo_root):
        return repo_path.endswith("version.js") \
            or repo_path.endswith("version.jsx") \
            or os.path.basename(repo_path) == "package.json"

    def update_line(self, line, version, repo_path):
        if repo_path.endswith(".json"):
            rgxps = self.re_json_rgxps
        else:
            rgxps = self.re_js_rgxps
        for rgxp in rgxps:
            match = rgxp.search(line)
            if match:
                return match.group('before') + version + match.group('after')
        return None

    re_json_rgxps = [
        re.compile(r'''
        ^
        (?P<before>
             \s* (?P<quote> ["'] )  version (?P=quote)
             \s* : \s*
             (?P<quote2> ["'] )
        )
        (?P<version> \d+(?:\.\d+)+  )
        (?P<after>
             \s* (?P=quote2) \s* ,? \s*
        )
        $''', re.VERBOSE),
    ]

    re_js_rgxps = [
        re.compile(r'''
        ^  (?P<before>
               \s* (?: const | var | let ) \s+
               VERSION \s* = \s*
               (?P<quote> ["'] )         )
           (?P<version> \d+(?:\.\d+)*    )
           (?P<after>
               (?P=quote)   # closing quote
               .* )
        $ ''', re.VERBOSE),
    ]


known_languages['javascript'] = LanguageJavaScript()


class LanguageCxx(Language):
    """C++ language rules."""

    def format_version_no(self, version_parts):
        return ".".join(version_parts)

    _re_fname = re.compile(r'^version.(cxx|cpp|hxx|hpp)$')

    def worth_checking(self, repo_path, repo_root):
        base = os.path.basename(repo_path)
        match = self._re_fname.search(base)
        return bool(match)

    def update_line(self, line, version, repo_path):
        for rgxp in self.re_const_rgxps:
            match = rgxp.search(line)
            if match:
                return match.group('before') + version + match.group('after')
        return None

    re_const_rgxps = [
        # Zapisy z =
        re.compile(r'''
        ^  (?P<before>
               \s* (?: const \s+ )?
               (?: string \s+ | char \s* \* \s* | char \s+)
               VERSION
               (?: \[\s*\]  )?
               \s* = \s*
               (?P<quote> ["'] )         )
           (?P<version> \d+(?:\.\d+)*    )
           (?P<after>
               (?P=quote)   # closing quote
               .* )
        $ ''', re.VERBOSE),
        # Zapisy z ()
        re.compile(r'''
        ^  (?P<before>
               \s* (?: const \s+ )?
                   string
               \s+
               VERSION
               \s* \(
               (?P<quote> ["'] )         )
           (?P<version> \d+(?:\.\d+)*    )
           (?P<after>
               (?P=quote)   # closing quote
               .* )
        $ ''', re.VERBOSE),
    ]


known_languages['c++'] = LanguageCxx()


class LanguageCvsKeywords(Language):
    """Not quite a language, but using the same base class
    saves some work"""

    def repo_setup(self, ui, repo):
        self.current_rev = scmutil.revsingle(repo, '.')
        # mercurial.context.changectx

        # For Author we take tagging user (it's not worth it to
        # detect last changes for all files and he is to commit them
        # after all)
        # …  self.current_rev.user()
        self.current_fmt_user = util.shortuser(ui.username()) 

    def size_limit(self):
        return 16384 * 1024

    def format_version_no(self, version_parts):
        return ".".join(str(vp) for vp in version_parts)

    def worth_checking(self, repo_path, repo_root):
        return True

    def update_line(self, line, version, repo_path):
        def _replace(match):
            kw = match.group(1)
            resolver = '_resolve_' + kw
            value = None
            if hasattr(self, resolver):
                value = getattr(self, resolver)(version, repo_path)
            if value:
                return '$' + kw + ': ' + value + ' $'
            else:
                return '$' + kw + '$'

        new_line = self.re_keyword.sub(_replace, line)
        if new_line == line:
            return None
        else:
            # print "DBG: swapped\n%s\nto:\n%s\n" % (line, new_line)
            return new_line

    def _resolve_Name(self, version, repo_path):
        # $Name: 0.7.0 $
        return version

    def _resolve_Revision(self, version, repo_path):
        # $Revision: 9754f628932a $
        return node.short(node.bin(self.current_rev.hex()))

    def _resolve_Header(self, version, repo_path):
        # $Header: mercurial_update_version.py,v 9754f628932a 2017/01/09 00:12:41 Marcin Exp $
        return " ".join([
            self._resolve_Source(version, repo_path),
            self._resolve_Revision(version, repo_path),
            self._resolve_Date(version, repo_path),
            self._resolve_Author(version, repo_path),
            self._resolve_State(version, repo_path),
        ])

    def _resolve_Id(self, version, repo_path):
        # $Id: mercurial_update_version.py,v 9754f628932a 2017/01/09 00:12:41 Marcin Exp $
        return " ".join([
            self._resolve_RCSFile(version, repo_path),
            self._resolve_Revision(version, repo_path),
            self._resolve_Date(version, repo_path),
            self._resolve_Author(version, repo_path),
            self._resolve_State(version, repo_path),
        ])

    def _resolve_Source(self, version, repo_path):
        # $Source: mercurial_update_version.py,v $
        return repo_path + ",v"

    def _resolve_RCSFile(self, version, repo_path):
        # $RCSfile: keyword.html,v $
        return os.path.basename(repo_path) + ",v"

    def _resolve_Author(self, version, repo_path):
        # $Author: Marcin $
        return self.current_fmt_user

    def _resolve_Date(self, version, repo_path):
        # $Date: 2017/01/09 00:12:41 $
        d = self.current_rev.date()
        return util.datestr(d, format="%Y/%m/%d %H:%M:%S")

    def _resolve_State(self, version, repo_path):
        # $State: Exp $
        # Some claim Stab or Rel could happen…
        return 'Exp'

    re_keyword = re.compile(r'''
    \$
    (Name|Revision|Header|Id|Source|RCSFile|Author|Date)
    (?:
    : [^\$]*
    )?
    \$
    ''', re.VERBOSE)


############################################################
# Tag formats
############################################################

known_tagfmts = {}


class TagFmtDotted(TagFmt):
    """Dotted (1.2.3) tag format"""

    sample = "1.3.11"
    _re_tag = re.compile(r'^ ( \d+ (?:\.\d+)+ )$', re.VERBOSE)

    def extract_no(self, tag_text):
        match = self._re_tag.search(tag_text)
        if match:
            return match.group(1).split(".")
        else:
            return None


known_tagfmts['dotted'] = TagFmtDotted()


class TagFmtDashed(TagFmt):
    """Dashed tag format (1-2-3, 1-17 etc)"""

    sample = "1-3-11"
    _re_tag = re.compile(r'^ ( \d+ (?:-\d+)+ )$', re.VERBOSE)

    def extract_no(self, tag_text):
        match = self._re_tag.search(tag_text)
        if match:
            return match.group(1).split("-")
        else:
            return None


known_tagfmts['dashed'] = TagFmtDashed()


class TagFmtPfxDotted(TagFmt):
    """Prefixed dotteg tag format (mylib-1.3.11, something_1.7)"""

    sample = "mylib-1.3.11"
    _re_tag = re.compile(r'^ .* [_-] ( \d+ (?:\.\d+)+ )$', re.VERBOSE)

    def extract_no(self, tag_text):
        match = self._re_tag.search(tag_text)
        if match:
            return match.group(1).split(".")
        else:
            return None


known_tagfmts['pfx-dotted'] = TagFmtPfxDotted()


class TagFmtPfxDashed(TagFmt):
    """Prefixed-dashed tag format (abc_1-2-3, xoxo-1-17 etc)"""

    sample = "mylib_1-3-11"
    _re_tag = re.compile(r'^ .* [^\d_-] .*? [-_] ( \d+ (?:\-\d+)+ )$', re.VERBOSE)

    def extract_no(self, tag_text):
        match = self._re_tag.search(tag_text)
        if match:
            return match.group(1).split("-")
        else:
            return None


known_tagfmts['pfx-dashed'] = TagFmtPfxDashed()


############################################################
# Actual extension work
############################################################

class Mode(object):
    """Represents how extension is to work on some repo"""

    def __init__(self, language, tagfmt, expand_keywords=False):
        self.language = language
        self.tagfmt = tagfmt
        self.expand_keywords = expand_keywords

    def __str__(self):
        dscrpt = []
        if self.language:
            dscrpt.append(_("using %s language rules and %s tag format") % (
                self.language, self.tagfmt))
        if self.expand_keywords:
            dscrpt.append(_("expanding CVS keywords"))
        return ", ".join(dscrpt)


def modes_active_on(ui, repo):
    """Checks whether extension is to be active on given repo - and how.
    Returns list of matching Mode objects (which can be empty)."""

    def read_details(ui, language_tag, tagfmt_tag, expand_keywords_tag):
        """Read actual languagename+tagfmtname pair from configuration"""
        language = ui.config("update_version", language_tag, None)
        tagfmt = ui.config("update_version", tagfmt_tag, None)
        expand_keywords = ui.configbool("update_version", expand_keywords_tag, False)

        ui.debug(_("update_version: config checked, %s=%s, %s=%s, %s=%s\n")
                 % (language_tag, language or '', tagfmt_tag, tagfmt or '',
                    expand_keywords_tag, str(expand_keywords)))

        if language and not tagfmt:
            ui.warn(_("update_version: %s not set in [update_version] section\n") % tagfmt_tag)
        if tagfmt and not language:
            ui.warn(_("update_version: %s not set in [update_version] section\n") % language_tag)
        if not language and not tagfmt and not expand_keywords:
            ui.warn(_("update_version: Unconfigured, neither %s, nor %s set in [update_version] section"), language_tag, expand_keywords)
            return None
        mode = Mode(language=language, tagfmt=tagfmt, expand_keywords=expand_keywords)
        return mode

    if not hasattr(repo, 'root'):
        return None

    modes = []

    # enabled by active
    if ui.configbool("update_version", "active", False):
        ui.debug(_("update_version: active on %s due to active=true\n") % (repo.root))
        modes.append(
            read_details(ui, "language", "tagfmt", "expand_keywords"))
    # enabled by active_on
    active_on = ui.configlist("update_version", "active_on", [])
    if active_on:
        if meu.belongs_to_tree_group(repo.root, active_on):
            ui.debug(_("update_version: active on %s due to active_on=%s\n") % (repo.root, ", ".join(active_on)))
            modes.append(
                read_details(ui, "language", "tagfmt", "expand_keywords"))
        else:
            ui.debug(_("update_version: mismatch, %s does not match active_on=%s\n") % (repo.root, ", ".join(active_on)))
    # enabled by label.active_on
    for name, items in meu.suffix_configlist_items(
            ui, "update_version", "active_on"):
        if meu.belongs_to_tree_group(repo.root, items):
            ui.debug(_("update_version: active on %s due to %s.active_on=%s\n") % (repo.root, name, ", ".join(items)))
            modes.append(
                read_details(ui, name + ".language", name + ".tagfmt",
                                 name + ".expand_keywords"))
        else:
            ui.debug(_("update_version: mismatch, %s does not match %s.active_on=%s\n") % (repo.root, name, ", ".join(items)))

    return modes


def _apply_version_constants(ui, repo,
                             tag_name, language_name, tagfmt_name,
                             dry_run=False):
    """Peforms VERSION= changes, as necessary.

    Returns the pair:
    - list of changed files if sth changed, empty list if no changes,
      None if some error happened and was reported,
    - version constant (present if any files are modified)
    """
    language = known_languages.get(language_name)
    if not language:
        ui.warn(_("update_version: Unknown language %s\n") % language_name)
        return [], None
    tagfmt = known_tagfmts.get(tagfmt_name)
    if not tagfmt:
        ui.warn(_("update_version: Unknown tagfmt %s\n") % tagfmt_name)
        return [], None

    version = tagfmt.extract_no(tag_name)
    if not version:
        ui.warn(_("update_version: Invalid tag format: %s (expected %s, for example %s). Version not updated (but tag created).\n") % (
            tag_name, tagfmt_name, tagfmt.sample))
        return [], None  # means OK

    language.repo_setup(ui, repo)

    fmt_version = language.format_version_no(version)
    if not fmt_version:
        ui.warn(_("update_version: Version number not supported by %s language: %s (too many parts or number too big)\n") % (
            language_name, ".".join(version)))
        return None, None  # means FAIL

    # Apply version number on files
    changed_files = []
    for repo_path, full_path in language.locate_files(ui, repo):
        changes = language.update_file(
            ui, repo, repo_path, full_path, fmt_version, dry_run)
        if changes:
            ui.status(_("update_version: Version number in %s set to %s. List of changes:\n") % (repo_path, fmt_version))
            for lineno, before, after in changes:
                ui.status(_("    Line %d\n    < %s\n    > %s\n") % (
                    lineno, before.rstrip("\r\n"), after.rstrip("\r\n")))
            changed_files.append(full_path)
        else:
            ui.debug(_("update_version: no changes in %s\n") % repo_path)

    return changed_files, fmt_version


def _apply_cvs_keywords(ui, repo, tag_name, dry_run=False):
    # Apply version number on files
    language = LanguageCvsKeywords()

    language.repo_setup(ui, repo)

    changed_files = []
    changed_names = []
    for repo_path, full_path in language.locate_files(ui, repo):
        changes = language.update_file(
            ui, repo, repo_path, full_path, tag_name, dry_run=dry_run)
        if changes:
            ui.debug(_("update_version: CVS keywords in %s expanded. List of changes:\n") % (repo_path))
            for lineno, before, after in changes:
                ui.debug(_("    Line %d\n    < %s\n    > %s\n") % (
                    lineno, before.rstrip("\r\n"), after.rstrip("\r\n")))
            changed_files.append(full_path)
            changed_names.append(repo_path)

    if changed_files:
        ui.status(_("update_version: CVS keywords expanded in %s\n") % " ".join(changed_names))

    return changed_files


def update_repository(ui, repo, tag_name, dry_run=False):
    """Perform main actual action"""

    modes = modes_active_on(ui, repo)
    if not modes:
        return

    changed_files = []

    for mode in modes:
        ui.debug(_("update_version: processing mode: %s\n") % str(mode))

        # VERSION=…
        if mode.language:
            ver_changed_files, fmt_version = _apply_version_constants(
                ui, repo, tag_name,
                mode.language, mode.tagfmt, dry_run=dry_run)
            if ver_changed_files is None:
                return True  # means Fail
        else:
            ver_changed_files = []
            fmt_version = tag_name   # For commit message

        # $Keywords$
        if mode.expand_keywords:
            kw_changed_files = _apply_cvs_keywords(
                ui, repo, tag_name, dry_run=dry_run)
            if kw_changed_files is None:
                return True  # means Fail
        else:
            kw_changed_files = []

        changed_files += ver_changed_files
        changed_files += kw_changed_files

    if not changed_files:
        ui.status("update_version: no files changed\n")
        return False  # means OK

    # Commit those changes
    if not dry_run:
        ui.note("update_version: Commiting updated version number\n")
        commands.commit(         # pylint: disable=star-args
            ui, repo,
            *changed_files,
            message=_("Version number set to %s") % fmt_version)

    return False  # means OK


############################################################
# Mercurial extension hooks
############################################################

# Note: as we commit something (updated numbers), the whole action
# must work as pre-tag hook, not pretag! During pretag the changeset
# being tagged is already set (and tag would omit the number-updating
# commit).
#
# According to mercurial docs, pre- hooks should be set during uisetup
# phase, so we enable them during uisetup below…

def pre_tag_hook(ui, repo, hooktype, pats, opts, **kwargs):
    """Hook called before tagging"""

    # Check command arguments. Ignore local tags, tags removal,
    # tags placed by revision (hg tag -r ... sth) unless they point
    # to the current revision. Extract final tag value.
    if opts.get('local'):
        ui.status("update_version: ignoring local tag (version number not updated)\n")
        return
    if opts.get('remove'):
        ui.status("update_version: ignoring tag removal (version number not updated)\n")
        return
    if opts.get('rev'):
        # Generally we ignore tags by revision, but it makes sense
        # to handle hg tag -r ‹current-rev› (especially considering
        # TortoiseHg tags by rev when someone tags via gui)
        current_rev = scmutil.revsingle(repo, '.').node()
        given_rev = scmutil.revsingle(repo, opts['rev']).node()
        if current_rev != given_rev:
            ui.status("update_version: ignoring tag placed -r revision (tag is placed, but version number not updated)\n")
            return
        else:
            # Rewriting rev param (missing param means tagging current
            # repo-revision so let's do just so, we are to make additional commit)
            opts['rev'] = None
    if len(pats) != 1:
        # ui.status("update_version: ignoring unexpected arguments (tag deletion?), pats=%s\n" % pats)
        ui.status("update_version: ignoring unexpected arguments (bad tag args?)\n")
        return

    tag_name = pats[0]
    update_repository(ui, repo, tag_name)

    return False  # means ok


def uisetup(ui):
    """Enable pre-tag hook"""
    meu.enable_hook(ui, "pre-tag.update_version", pre_tag_hook)


# def reposetup(ui, repo):
#     # Test
#     def fire_me(*args, **kwargs):
#         print "I am fired", args, kwargs
#     meu.enable_hook(ui, "pretag.test", fire_me)


############################################################
# Commands
############################################################

cmdtable = {}
command = meu.command(cmdtable)


@command("tag_version_test",
         [],
         "tag_version_test TAG")
def cmd_tag_version_test(ui, repo, tag, **opts):
    """
    Dry-run, listing what would be changed
    """
    modes = modes_active_on(ui, repo)
    if not modes:
        ui.status(_("update_version: not active in this repository\n"))
        return
    for mode in modes:
        ui.status("update_version: %s\n" % str(mode))

    update_repository(ui, repo, tag, dry_run=True)


############################################################
# Extension setup
############################################################

testedwith = '2.7 2.9 3.0 3.3 3.6 3.7 3.8 4.0 4.1 4.2 4.3 4.5 4.6'
buglink = 'https://bitbucket.org/Mekk/mercurial-update_version/issues'
