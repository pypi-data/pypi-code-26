# -*- coding: utf-8 -*-
"""The filesysobjects.pprint module provides pretty printer for paths.
"""
from __future__ import absolute_import
from __future__ import print_function

import os


from filesysobjects import V3K, ISSTR, RTE, PrettyPrintError

#
# for some display enhancements, for now uses the initial only
#
try:
    if V3K:
        columns, rows = os.get_terminal_size(0)  # @UndefinedVariable
    else:
        import curses
        stdscr = curses.initscr()
        curses.cbreak()
        curses.noecho()
        stdscr.keypad(1)
        columns, rows = stdscr.getmaxyx()
        curses.endwin()
except:
    # common defaults
    columns = 80
    rows = 24


from filesysobjects.apppaths import splitapppathx

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez" \
                "@Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.20'
__uuid__ = "4135ab0f-fbb8-45a2-a6b1-80d96c164b72"

__docformat__ = "restructuredtext en"


class PPPathVar(object):
    """Pretty printer for *PATH* variables.
    """

    def __init__(self, path, **kargs):
        """Pretty print search path variables.
        Splits and returns the formatted printable string for 
        search path variables of type *PATH*.
        
        The input: ::

           posix: path = "/path/entry/0:/path/entry/1"
           win32: path = "\\path/entry\\0;\\path\\entry\\1" 

        results in the output of 'format=console': ::

           ...MYPATH = [
           ...::::"/path/entry/0",
           ...::::"/path/entry/1",
           ...]
           
        for the output parameters: ::

            <format>:        the output format, here format='console'
           'MYPATH':         the prefix, here 'MYPATH'
           '=':              the assignchar, here '='
           "/path/entry/0":  first path entry
           "/path/entry/1":  second path entry
           '.' * n:          'n' offset, here n=3
           '.':              offsetchar, here '.'
           ':' * m:          'm' indent, here m=4
           ':':              indentchar, here ':'
        
        For further details and examples refer to the manual.

        Args:
            **path**:
                The search path to be pretty printed. ::

                path := (
                     <search-path-string>
                   | <list-of-search-paths>
                   | <tuple-of-search-paths>
                )

                search-path-string := "string of PATH syntax, see 'tpf' and 'spf'"
                list-of-search-paths := [<path-entry-0>, <path-entry-1>, ...]
                tuple-of-search-paths := (<path-entry-0>, <path-entry-1>, ...)

            kargs:
                **assignchar**:
                    The character representing the assignment.

                **format**:
                    The output format.::

                       format := (
                             console    # formatted for console display
                           | ini        # simple path print with normalized path
                           | inix0      # multiline colon separated list
                           | inix1      # multiple key repetition
                           | json       # JSON syntax module
                           | properties # 
                           | python     # same as json
                           | xml        # XML syntax module
                           | yaml       # YAML syntax module
                       )

                    See manual for details.

                **indent**:
                    Indention of each path item. ::

                       indent := <#int>

                    default := 4

                **indentchar**:
                    The character used for padding of the indention.
                    The use of 'indentchar[0]' only is forced. ::

                       offsetchar := <printable-character>

                    default := ' '  # space

                **indentclip**:
                    Indention clipped overflows for of each individual
                    path item. ::

                       indent := <#int>

                    default := 2

                **indentclipchar**:
                    The character user for extra padding of clipped 
                    items. The use of 'indentchar[0]' only is forced. ::

                       offsetchar := <printable-character>

                    default := ' '  # space

                **keepentry**:
                    Preserves path entries from overflow 
                    handling. ::

                       keepentry := (
                            True    # ignore overflow for single path entries
                          | False   # applies overflow processing within single
                                    # path entries
                       )

                **maxwidth**:
                    The maximal line width.

                    default := 80

                **linesep**:
                    The output line separator.

                    default := os.linesep

                **linesepfinal**:
                    Controls the print of a line separator at the end
                    of the string. ::

                       linesepfinal := (
                            True   # prints a line separator as last character
                          | False  # suppress the final line separator
                       )

                    default := True

                **offset**:
                    The left side offset margin for all output strings. ::

                       offset := <#int>

                    default := 0

                **offsetchar**:
                    The character used for padding of a general offset.
                    The use of 'offsetchar[0]' only is forced. ::

                       offsetchar := <printable-character>

                    default := ' '  # space

                **overflow**:
                    The behavior, when line is longer than 
                    *maxwidth*. ::

                       overflow := (
                             'ignore'     # ignores overflow

                           | 'cut'        # drops the overflow

                           | 'clip'       # continues with the overflow  
                                          # in next line, starts new for
                                          # next item

                           | 'clipmerge'  # continues with the overflow 
                                          # in next line, concatenates
                                          # next item 
                       )

                    default := 'ignore'

                **pathsepin**:
                    The input path separator.
                    
                    default := os.pathsep

                **pathsepout**:
                    The output path separator.
                    
                    default := os.pathsep

                **prefix**:
                    The prefix to be printed first. ::
                    
                       prefix := "string without line breaks"
    
                    The output is: ::
    
                       <prefix> = [
                          "<path-entry-0>",
                          "<path-entry-1>",
                       ]
    
                    default := 'PATH'
                
                **spf**:
                    Source platform.

                **tpf**:
                    Target platform.


        Returns:
            Object/None
            
        Raises:
            pass-through
            
        """
        self.assignchar = kargs.get("assignchar", '=')
        self.format = kargs.get("format", 'console')
        self.indent = kargs.get("indent", 4)
        self.indentchar = kargs.get("indentchar", ' ')
        self.indentclip = kargs.get("indentclip", 2)
        self.indentclipchar = kargs.get("indentclipchar", ' ')
        self.keepentry = kargs.get("keepentry", True)
        self.linesep = kargs.get("linesep", os.linesep)
        self.linesepfinal = kargs.get("linesepfinal", True)
        self.maxwidth = kargs.get("maxwidth", columns)
        self.offset = kargs.get("offset", 0)
        self.offsetchar = kargs.get("offsetchar", ' ')
        self.overflow = kargs.get("overflow", 'ignore')
        self.pathsepin = kargs.get("pathsepin", os.pathsep)
        self.pathsepout = kargs.get("pathsepout", os.pathsep)
        self.prefix = kargs.get("prefix", 'PATH')

#        self.tpf = kargs.get("tpf", RTE)
        
        kw = {}
        try:
            self.tpf = kargs.pop("tpf")
            kw['tpf'] = self.tpf 
        except KeyError:
            self.tpf = False

        try:
            self.spf = kargs.pop("spf")
            kw['spf'] = self.spf 
        except KeyError:
            self.spf = False

        self._raw = path
        if type(path) in ISSTR:
            self.path = splitapppathx(
                path, apppre=False, pathsep=self.pathsepin,
                **kw,
                )

        elif type(path) in (list, tuple):
            # lists and tuples are expected to be split resource paths.
            self.path = path

        else:
            raise PrettyPrintError("type not supported: " +str(path))


    def __str__(self):
        """Pretty prints as defined by the creation parameters.
        """
        
        if self.format.lower() == 'console':
            return self.str_console()
        elif self.format.lower() == 'ini':
            return self.str_ini()
        elif self.format.lower() == 'inix0':
            return self.str_inix0()
        elif self.format.lower() == 'inix1':
            return self.str_inix1()
        elif self.format.lower() == 'inix2':
            return self.str_inix2()
        elif self.format.lower() == 'json':
            return self.str_json()
        elif self.format.lower() == 'properties':
            return self.str_properties()
        elif self.format.lower() == 'xml':
            return self.str_xml()
        elif self.format.lower() == 'yaml':
            return self.str_yaml()
        
        return self.str_console()


    def str_console(self):
        """Creates the string for standard display output.
        """
        res = ''
        
        offset = self.offset
        offsetstr = self.offset * self.offsetchar
        indent = offset + self.indent
        indentstr = offsetstr + self.indent * self.indentchar
        indentclip = indent + self.indentclip
        indentclipstr = indentstr + self.indentclip * self.indentclipchar

        if self.overflow == 'clipmerge':
            # the complete string
            resi = self.prefix + ' ' + self.assignchar + ' "' + self.pathsepout.join(self.path)
            l0 = len(resi)

            if l0 < self.maxwidth:
                # fits into current linen length
                return resi + '"'

            #
            # needs clipping
            #
            res += offsetstr + resi[:self.maxwidth - offset - 1] + '"'# + self.linesep
            plen = self.maxwidth - indent
            lx = plen + offset - 1  # logically pushed back for an extra quote
            while lx < l0:
                res += self.linesep
                res += indentstr + (
                    '"' + resi[lx : lx + plen-2]  + '"'
                    ) #+ self.linesep
                lx += plen - 2
            return res + self.linesep

        res += offsetstr + self.prefix + ' ' + self.assignchar + ' [' + self.linesep
        for p in self.path:
            resi = '"%s' % (str(p))

            l0 = len(resi)
            if self.overflow == 'ignore':
                res += indentstr + resi + '",' + self.linesep
            elif l0 > (self.maxwidth - indent) and not self.keepentry:

                plen = self.maxwidth - indent
                res += indentstr + resi[:plen]
                if self.overflow == 'cut':
                    res = res[:-2] + '*"'  + self.linesep
                    continue

                elif self.overflow == 'clip':
                    res = res[:-1] + '"'  + self.linesep
                    plen = self.maxwidth - indentclip
                    lx = plen + 1  # extra quote
                    plen -= self.indentclip
                    while lx < l0:
                        res += indentclipstr + (
                            '"' + resi[lx : lx + plen]  + '"'
                            ) + self.linesep
                        lx += plen

                res = res[:-len(self.linesep) - 1] + '",' + self.linesep
            else:
                res += indentstr + resi + '",' + self.linesep

        if res.endswith(',' + self.linesep):
            res = res[:-len(',' + self.linesep)] + self.linesep

        if self.linesepfinal:
            res += offsetstr + ']' + self.linesep
        else:
            res += offsetstr + ']'

        return res

    def str_ini(self):
        """Creates the string for standard *INI* format.
        """
        offsetstr = self.offset * self.offsetchar

        # the complete string
        if self.linesepfinal:
            return offsetstr + self.prefix + ' ' + self.assignchar + ' "' + self.pathsepout.join(self.path)  + '"'+ self.linesep
        else:
            return offsetstr + self.prefix + ' ' + self.assignchar + ' "' + self.pathsepout.join(self.path)  + '"'

    def str_inix0(self):
        """Creates the string for extended *INI* format 
        based on colon separated multi-line lists.
        """
        res = ''
        offsetstr = self.offset * self.offsetchar
        indentstr = offsetstr + self.indent * self.indentchar

        res += offsetstr + self.prefix + ' ' + self.assignchar + ' '
        for p in self.path:
            res += self.linesep 
            res += indentstr + ':%s' % (str(p)) 

        if self.linesepfinal:
            return res + self.linesep
        else:
            return res

    def str_inix1(self):
        """Creates the string for the extended *INI* format
        based on multiple key repetition.
        """
        res = ''
        offsetstr = self.offset * self.offsetchar

        for p in self.path:
            resi = self.prefix + ' ' + self.assignchar + ' %s' % (str(p)) 
            res += offsetstr + resi + self.linesep

        if self.linesepfinal:
            return res
        else:
            return res[:-len(self.linesep)]

    def str_inix2(self):
        """Creates the string for the extended *INI* format
        based on multiple keys with incremented index extension.
        """
        res = ''
        offsetstr = self.offset * self.offsetchar

        idx = 0
        for p in self.path:
            resi = self.prefix + str(idx) + ' ' + self.assignchar + ' %s' % (str(p)) 
            res += offsetstr + resi + self.linesep
            idx += 1

        if self.linesepfinal:
            return res
        else:
            return res[:-len(self.linesep)]

    def str_json(self):
        """Creates the string for standard *INI* format.
        """
        res = ''
        
        offsetstr = self.offset * self.offsetchar
        indentstr = offsetstr + self.indent * self.indentchar

        res += offsetstr + '"' + self.prefix + '": ['
        empty = True 
        for p in self.path:
            empty = False 
            res += self.linesep
            resi = '"%s' % (str(p))
            res += indentstr + resi + '",'

        if empty:
            res += self.linesep + offsetstr + ']'
        else:
            res = res[:-1] + self.linesep + offsetstr + ']'

        if self.linesepfinal:
            return res + self.linesep
        else:
            return res

    def str_properties(self):
        """Creates the string for standard *INI* format.
        """
        res = ''
        
#         self.assignchar = kargs.get("assignchar", '=')
#         self.format = kargs.get("format", 'print')
#         self.indent = kargs.get("indent", 4)
#         self.indent = kargs.get("indent", 4)
#         self.indentchar = kargs.get("indentchar", ' ')
#        self.indentclip = kargs.get("indentclip", 2)
#         self.keepentry = kargs.get("keepentry", True)
#         self.keepentry = kargs.get("keepentry", True)
#         self.linesep = kargs.get("linesep", os.linesep)
#         self.maxwidth = kargs.get("maxwidth", 80)
#         self.maxwidth = kargs.get("maxwidth", columns)
#         self.offset = kargs.get("offset", 4)
#         self.offsetchar = kargs.get("offsetchar", ' ')
#         self.overflow = kargs.get("overflow", 'clip')
#         self.overflow = kargs.get("overflow", 'ignore')
#         self.pathsepin = kargs.get("pathsepin", os.pathsep)
#         self.pathsepout = kargs.get("pathsepout", os.pathsep)
#         self.prefix = kargs.get("prefix", path.__name__)
        return res

    def str_xml(self):
        """Creates the string for standard *XML* format.
        """
        res = ''
        
        offsetstr = self.offset * self.offsetchar
        indentstr = offsetstr + self.indent * self.indentchar

        res += offsetstr + '<' + self.prefix + '>' + self.linesep
        idx = 0
        for p in self.path:
            resi = '<entry idx=' + str(idx) + '>' + '%s' % (str(p)) + '</entry>' 
            res += indentstr + resi + self.linesep
            idx += 1

        if self.linesepfinal:
            res += offsetstr + '</' + self.prefix + '>'  + self.linesep
        else:
            res += offsetstr + '</' + self.prefix + '>'

        return res


    def str_yaml(self):
        """Creates the string for standard *INI* format.
        """
        res = ''
        
        offsetstr = self.offset * self.offsetchar
        indentstr = offsetstr + self.indent * self.indentchar

        res += offsetstr + self.prefix + ':'
        for p in self.path:
            resi = '- ' + '%s' % (str(p)) 
            res += self.linesep + indentstr + resi

        if self.linesepfinal:
            return res + self.linesep
        else:
            return res
        
        return res

    def __repr__(self):
        return repr(self._raw)

    def raw(self):
        return self._raw
