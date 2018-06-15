# -*- coding: utf-8 -*-
"""Provides the command  line options for *multico*.
"""
from __future__ import absolute_import

import sys
import os
import argparse
import platform

from pysourceinfo.fileinfo import getcaller_linenumber

import multiconf
from multiconf import MultiConfError
from multiconf import V3K, ISSTR


if V3K:
    unicode = str  # @ReservedAssignment

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2017 Arno-Can Uestuensoez" \
                " @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.1'
__uuid__ = "9b3aa92b-2168-457c-ba42-dc1f4885b420"

__docformat__ = "restructuredtext en"

# cached defaults
_verbose = multiconf._verbose
_debug = multiconf._debug
_header = ''

_appname = "multico"

class FetchOptionsError(MultiConfError):
    def __init__(self, *args, **kargs):
        super(FetchOptionsError, self).__init__(*args, **kargs)


#
# buffer for options evaluation
_clibuf = []

#
# early fetch for the parameter of the ArgumentParser constructor
#
if '--fromfile' in sys.argv:
    _formfile='@'
else:
    _fromfile = None


class FormatTextRaw(argparse.HelpFormatter):
    """Formatter for help."""

    def _split_lines(self, text, width):
        """Customize help format."""
        if text.startswith('@R:'):
            return text[3:].splitlines()
        return argparse.HelpFormatter._split_lines(self, text, width)


class ActionExt(argparse.Action):
    """Extends the 'argparse.Action'
    """
    def __init__(self, *args, **kwargs):
        super(ActionExt, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Adds context help on each option.
        """
        if _debug > 2:
            if values:
                sys.stderr.write(
                    "RDBG:%d:CLI:option: %s=%s\n" %(
                        getcaller_linenumber(), 
                        str(option_string),
                        str(values)
                        )
                    )
            else:
                sys.stderr.write(
                    "RDBG:%d:CLI:option: %s\n" %(
                        getcaller_linenumber(), 
                        str(option_string)
                        )
                    )
            
        if values and (values in ("help", "?") or type(values) is list and values[0] in ("help", "?")):
            form = FormatTextRaw('rdbg')
            # print('\n' + str(sys.argv[-2]))
            if self.__doc__:
                print('\n  ' +
                      '\n  '.join(FormatTextRaw._split_lines(
                          form, "@R:" + self.__doc__, 80)) + '\n')
            else:
                print('\n  ' +
                      '\n  '.join(FormatTextRaw._split_lines(
                          form, "No help.", 80)) + '\n')
            sys.exit(0)

        self.call(parser, namespace, values, option_string)

    def get_help_text(self):
        form = FormatTextRaw('rdbg')
        #print('\n' + str(sys.argv[-2]))
        if self.__doc__:
            return '\n  ' + '\n  '.join(FormatTextRaw._split_lines(
                form, "@R:" + self.__doc__, 80)) + '\n'
        else:
            return '\n  ' + '\n  '.join(FormatTextRaw._split_lines(
                form, "No help.", 80)) + '\n'
        
    def help_option(self):
        print(self.get_help_text())
        sys.exit(0)


class OptActionPathAppend(ActionExt):
    """
Path for search, appended at the end of current search path.

  --append=<path-list>

Repetition adds multiple in given order.

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionPathAppend, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        if not values:
            raise MultiConfError("Requires value for'--append'")
        namespace.append.extend(values)
        if not namespace.append:
            raise MultiConfError("No valid paths found '--append'")


class OptActionPathPrepend(ActionExt):
    """
Path for search, insert at the eginning of current search path.

  --prepend=<path-list>

Repetition inserts multiple in given order at position '0',
effetively prepends in reversed order.

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionPathPrepend, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        if not values:
            raise MultiConfError("Requires value for'--prepend'")
        namespace.prepend.insert(0, values[0])
        if not namespace.prepend:
            raise MultiConfError("No valid paths found '--prepend'")


class OptActionPathReplace(ActionExt):
    """
Path for search. When multiple repetition
of option is required, use for the following 
either '--append', or '--prepend'.

  --replace=<path-list>

Repetition extends the replacement path list.

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionPathReplace, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        if not values:
            raise MultiConfError("Requires value for'--replace'")
        namespace.replace.extend(values)
        if not namespace.replace:
            raise MultiConfError("No valid paths found '--replace'")


class OptActionAllowNoVal(ActionExt):
    """
Specific option for the *INI* file syntax, permits
keys without value assignment.

  --allow-no-val

    default := False

"""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionAllowNoVal, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        namespace.allownoval = True


class OptActionDebug(ActionExt):
    """
Activates debug output including stacktrace,
multiple raise the debug level.

  --debug[=#level]
  -d

    initial := 0, sys.stacktrace=0
    default := +1, sys.stacktrace=1000

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionDebug, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        global _debug
        if values == '0':
            multiconf._debug = 0
            _debug = multiconf._debug
            namespace.debug = _debug
            sys.tracebacklimit = 0
        elif not values:
            multiconf._debug += 1
            _debug = multiconf._debug
            namespace.debug = _debug
            sys.tracebacklimit = 1000  # the original default
        else:
            try:
                multiconf._debug = int(values)
                _debug = multiconf._debug
                namespace.debug = _debug
                sys.tracebacklimit = 1000  # the original default
            except ValueError:
                raise MultiConfError("'--debug' requires 'int', got: " + str(values))


class OptActionDebugOptions(ActionExt):
    """
Print provided command line options.

  --debug-options[=('json' | 'repr' | 'str')[ cont]]
  
  default := 'json'

"""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionDebugOptions, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        namespace.debug_options = []
        if values in ('', None, [],):
            namespace.debug_options.append('json')
        elif values[0].lower() in ('json', 'repr', 'str'):
            namespace.debug_options.append(values[0])
            if values[-1].lower() == 'cont':
                namespace.debug_options.append(values[1])
            elif len(values) >1:
                raise MultiConfError("invalid value: --debug-options=" + str(values))
        else:
            raise MultiConfError("invalid value: --debug-options=" + str(values)) 


class OptActionEnvironDetails(ActionExt):
    """
Details of runtime environment.

   --environ

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionEnvironDetails, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):

        _osu = platform.uname()
        _dist, _distver, _x = platform.dist()
        
        print("")
        print("app:                   " + str(_appname))
        print("")
        print("python running multico:")
        print("  running version:     " + str(platform.python_version()))
        print("  compiler:            " + str(platform.python_compiler()))
        print("  build:               " + str(platform.python_build()))
        print("")
        sys.exit()


class OptActionFromfile(ActionExt):
    """
Enables the read of options from an options file.
For details refer to *argparse.ArgumentParse* constructor
option  *fromfile_prefix_chars*. ::

  --fromfile

    hard-coded activation of *fromfile_prefix_chars='@'*

REMARKS: for file format:

- Trailing spaces are significant, these change the option and
  are than considered by *argparse* as the first argument following
  the option list. Thus may lead to confusing results.

- Current release of *argparse* has an issue with double dash line
  following an argument with optional values, but none.
  So the double dash works only when following complete options,
  which means including it's complete set of optional values.

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionFromfile, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        namespace.fromfile = True


class OptActionH(ActionExt):
    """
Usage.

  -h

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionH, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        parser.print_usage()
        sys.exit(0)


class OptActionHelp(ActionExt):
    """
This help.

  -help --help

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionHelp, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        parser.print_help()
        sys.exit(0)


class OptActionPrintOutFormat(ActionExt):
    """
Defines the processed output format.

  --out-format=<format>
    format := (
       'json' | 'raw' | 'repr' | 'str'
    )

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionPrintOutFormat, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        if not values[0]:
            raise  MultiConfError("Requires value for'--out-format'")
        elif values[0] in ('ini', 'conf', 'csv', 'json', 'raw', 'repr', 'str'):
#        elif values[0] in ('ini', 'conf', 'csv', 'json', 'raw', 'repr', 'str'):
            namespace.out_format = values[0]
        else:
            raise  MultiConfError("Unknown output format:" + str(values))


class OptActionQuiet(ActionExt):
    """
Suppress output

  --quiet

"""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionQuiet, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        namespace.quiet = True


class OptActionIgnoreErrors(ActionExt):
    """
Ignores errors and continues with the processing of the next file.

  --ignore-errors

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionIgnoreErrors, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        namespace.ignore_errors = True


class OptActionInterpolation(ActionExt):
    """
Controls interpolation.

  --interpolation=(True | False)

    True:  enable interpolation 
    False: disable interpolation 
    
    default := False

For current release specific for the *INI* file syntax. 

"""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionInterpolation, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        if values[0].lower() in ('off', 'false', 'no', '0', 0, False):
            namespace.interpolation = False
        elif values[0].lower() in ('on', 'true', 'yes', '1', 1, True):
            namespace.interpolation = True
        else:
            raise MultiConfError("Unknown value --interpolation=" + str(values))


class OptActionParser(ActionExt):
    """
Selects the configuration parser.

  --parser <class-name> <parser-module> <module-path>
  
    class-name:    "The name of the parser class."
    parser-module: "The module name of the parser." 
    module-path:   "The file path name of the parser module." 

Example:

  --parser ConfigDataCONF multiconf.parser.conf multiconf/parser/conf.py

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionParser, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        if not values:
            raise  MultiConfError("Requires values for'--parser'")
        elif len(values) != 3:
            raise  MultiConfError("Requires exactly 3 parameters for '--parser': " + str(values))

        namespace.parser = values[:]

        if not os.path.exists(values[2]):
            raise MultiConfError("Missing module path " + str(values))

class OptActionParserRegister(ActionExt):
    """
Adds a configuration parser to the internal syntax dispatcher.

  --parser-register <class-name> <parser-module> <module-path>[ <suffix-list>]
  
    class-name:    "The name of the parser class."
    parser-module: "The module name of the parser." 
    module-path:   "The file path name of the parser module." 

    suffix-list := <suffix>[ <suffix-list>]
    suffix:        "Additional suffix to be registered for the parser"

Could be repeated multiple times, each add the standard list of suffixes 
and the optional suffix-list  to the registry.

Example:

  --parser-register ConfigDataCONF multiconf.parser.conf multiconf/parser/conf.py
  --parser-register ConfigDataINIX multiconf.parser.inix multiconf/parser/inix.py
  --parser-register ConfigDataJSON multiconf.parser.json multiconf/parser/json.py
  --parser-register ConfigDataXML  multiconf.parser.xml  multiconf/parser/xml.py
  --parser-register ConfigDataYAML multiconf.parser.yaml multiconf/parser/yaml.py

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionParserRegister, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        if not values:
            raise  MultiConfError("Requires values for'--parser-register'")
        elif len(values) < 3:
            raise  MultiConfError("Requires at leats 3 parameters for '--parser-register': " + str(values))
        
        record = values[:3]
        if len(values) > 3:
            # suffixes as one list
            record.append(values[3:])
        else:
            record.append([])

        if not os.path.exists(values[2]):
            raise MultiConfError("Missing module path " + str(values))

        namespace.parser_register.append(record)


class OptActionConfApp(ActionExt):
    """
Selects the configuration app.

  --confapp <class-name> <parser-module> <module-path>
  
    class-name:    "The name of the parser class."
    parser-module: "The module name of the parser." 
    module-path:   "The file path name of the parser module." 

Examples:

  --confapp ConfigEnviron   multiconf.apps.environ   multiconf/apps/environ.__init__.py
  --confapp ConfigMulticonf multiconf.apps.multiconf multiconf/apps/multiconf.__init__.py

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionConfApp, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        if not values:
            raise  MultiConfError("Requires values for'--confapp'")
        elif len(values) != 3:
            raise  MultiConfError("Requires exactly 3 parameters for '--confapp': " + str(values))

        namespace.confapp = values[:]

        if not os.path.exists(values[2]):
            raise MultiConfError("Missing module path " + str(values))


class OptActionStrict(ActionExt):
    """
Strict verification

  --strict

"""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionStrict, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        namespace.strict = True


class OptActionSyntax(ActionExt):
    """
Selects the syntax for the configuration parser.

  --syntax=<parser-syntax>
  
    parser-syntax := (
         conf
       | ini
       | inix
       | json
       | xml   (soon)
       | yaml  (soon)
    )

    default: "either based on the suffix, or as the final default 'ini'" 

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionSyntax, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        if not values:
            raise  MultiConfError("Requires syntax name for '--syntax'")

        namespace.syntax = values[0].lower()

        if values[0].lower() not in ('conf', 'ini', 'json', 'xml', 'yaml',):
            raise MultiConfError("Unknown syntax " + str(values))



class OptActionVerbose(ActionExt):
    """
Verbose, some relevant states for basic analysis.
Repetition raises the display level.

  --verbose[=#level]
  -v

    initial := 0, sys.stacktrace=0
    default := +1, sys.stacktrace=1000

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionVerbose, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        global _verbose
        if values == '0':
            namespace.verbose = _verbose = multiconf._verbose = 0
        elif not values:
            multiconf._verbose += 1
            _verbose = multiconf._verbose
            namespace.verbose = _verbose
        else:
            try:
                multiconf._verbose = int(values)
                _verbose = multiconf._verbose
                namespace.verbose = _verbose
            except ValueError:
                raise MultiConfError("'--verbose' requires 'int', got: " + str(values))


class OptActionVersion(ActionExt):
    """
Current version - terse.

  --version

    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionVersion, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        print(str(__version__))
        sys.exit()


class OptActionVersionDetails(ActionExt):
    """
Current version - detailed.

  --Version
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptActionVersionDetails, self).__init__(
            option_strings, dest, nargs, **kwargs)

    def call(self, parser, namespace, values, option_string=None):
        # if not values:
        #     namespace.optargs['Version'] = 0
        #     return
        # namespace.optargs['Version'] = values

        print("")
        print("app:         " + str(_appname))
        print("id:          " + str(__uuid__))
        print("multiconf:   " + str(multiconf.__version__))
        print("multico:     " + str(__version__))
        print("")
        print("Project:     " + 'https://multiconf.sourceforge.net/')
        print("SCM:         " + 'https://github.com/ArnoCan/multiconf/')
        print("package:     " + 'https://pypi.python.org/pypi/multiconf/')
        print("docs:        " + 'https://pythonhosted.org/multiconf/')
        print("")
        print("author:      " + str(multiconf.__author__))
        print("author-www:  " + 'https://arnocan.wordpress.com')
        print("")
        print("copyright:   " + str(multiconf.__copyright__))
        print("license:     " + str(multiconf.__license__))
        print("")
        sys.exit()


class OptionsNamespace(object):
    """Namespace object for parameter passing.
    """

    def __init__(self, argv, optargs, env=None):
        self._argv = argv  #: The original argv
        self.optargs = optargs  #: the result formatted as JSON compatible

        self.rdbgenv = env  #: FIXME:

    def get_optvalues(self):
        """Gets the resulting command line parameters."""
        return self.optargs

#
# option parser/scanner
#
class OptionsParser(object):

    def __init__(self, argv=None, *args, **kargs):
        """
        Args:
            argv: 
                call options

        Returns:
            (opts, unknown, args)

        Raises:
            pass-through
        """
        # prep argv
        if argv and type(argv) in ISSTR:
            self.argv = argv.split()
        elif argv and type(argv) in (list,):
            self.argv = argv[:]
        elif argv is None:
            self.argv = sys.argv[:]
        else:
            self.argv = argv

        self.optargs = {}  #: resulting options and arguments'--

    def get_options(self):

        _myspace = OptionsNamespace(self.argv, self.optargs)

        # set and call parser
        self.parser = argparse.ArgumentParser(
            prog='multico',
            add_help=False,
            description="""
The 'multico' command line interface provides basic 
dialogue access to the library modules of 'multiconf'.

""",
            formatter_class=FormatTextRaw,
            fromfile_prefix_chars=_fromfile  # from early fetch
        )

        group_options = self.parser.add_argument_group(
            'Parser:',
            ''
        )
        group_options.add_argument(
            '--confapp',
            nargs=3,
            type=str,
            default=[],
            action=OptActionConfApp,
            help="@R:" + OptActionConfApp.__doc__
        )
        group_options.add_argument(
            '--parser',
            nargs=3,
            type=str,
            default=[],
            action=OptActionParser,
            help="@R:" + OptActionParser.__doc__
        )
        group_options.add_argument(
            '--parser-register',
            nargs='*',
            # type=list,
            default=[],
            action=OptActionParserRegister,
            help="@R:" + OptActionParserRegister.__doc__
        )
        group_options.add_argument(
            '--syntax',
            nargs=1,
            type=str,
            default='',
            action=OptActionSyntax,
            help="@R:" + OptActionSyntax.__doc__
        )

        group_options = self.parser.add_argument_group(
            'Search Path:',
            ''
        )
        group_options.add_argument(
            '--append',
            nargs=1,
            type=str,
            default=[],
            action=OptActionPathAppend,
            help="@R:" + OptActionPathAppend.__doc__
        )
        group_options.add_argument(
            '--prepend',
            nargs=1,
            type=str,
            default=[],
            action=OptActionPathPrepend,
            help="@R:" + OptActionPathPrepend.__doc__
        )
        group_options.add_argument(
            '--replace',
            nargs=1,
            type=str,
            default=[],
            action=OptActionPathReplace,
            help="@R:" + OptActionPathReplace.__doc__
        )
          
        group_options = self.parser.add_argument_group(
            'Generic Support Options:',
            ''
        )
        group_options.add_argument(
            '--allownoval',
            nargs=0,
            default=False,
            action=OptActionAllowNoVal,
            help="@R:" + OptActionAllowNoVal.__doc__
        )
        group_options.add_argument(
            '-d', '--debug',
            nargs='?',
            type=int,
            default=0,
            const=None,
            action=OptActionDebug,
            help="@R:" + OptActionDebug.__doc__
        )
        group_options.add_argument(
            '--debug-options',
            nargs='*',
            #type=str,
            default=[],
            #const=[ 'json', 'break',],
            action=OptActionDebugOptions,
            help="@R:" + OptActionDebugOptions.__doc__
        )
        group_options.add_argument(
            '--environ', '--env',
            nargs=0,
            action=OptActionEnvironDetails,
            default=None,
            const=None,
            help="@R:" + OptActionEnvironDetails.__doc__
        )
        group_options.add_argument(
            '--fromfile',
            nargs=0,
            action=OptActionFromfile,
            help="@R:" + OptActionFromfile.__doc__
        )
        group_options.add_argument(
            '--ignore-errors',
            nargs=0,
            default=False,
            action=OptActionIgnoreErrors,
            help="@R:" + OptActionIgnoreErrors.__doc__
        )
        group_options.add_argument(
            '--interpolation',
            nargs=1,
            # default=False,
            action=OptActionInterpolation,
            help="@R:" + OptActionInterpolation.__doc__
        )
        group_options.add_argument(
            '--out-format',
            nargs=1,
            type=str,
            default='str',
            const='json',
            action=OptActionPrintOutFormat,
            help="@R:" + OptActionPrintOutFormat.__doc__
        )
        group_options.add_argument(
            '-q', '--quiet',
            nargs=0,
            default=False,
            action=OptActionQuiet,
            help="@R:" + OptActionQuiet.__doc__
        )
        group_options.add_argument(
            '--strict',
            nargs=0,
            default=False,
            action=OptActionStrict,
            help="@R:" + OptActionStrict.__doc__
        )
        group_options.add_argument(
            '-v', '--verbose',
            nargs='?',
            type=int,
            action=OptActionVerbose,
            default=0,
            const=0,
            help="@R:" + OptActionVerbose.__doc__
        )
        group_options.add_argument(
            '--version',
            nargs=0,
            action=OptActionVersion,
            default=None,
            help="@R:" + OptActionVersion.__doc__
        )
        group_options.add_argument(
            '--Version',
            nargs=0,
            action=OptActionVersionDetails,
            default=None,
            help="@R:" + OptActionVersionDetails.__doc__
        )
        group_options.add_argument(
            '--help', '-help',
            nargs=0,
            action=OptActionHelp,
            default=None,
            help="@R:" + OptActionHelp.__doc__
        )
        group_options.add_argument(
            '-h',
            nargs=0,
            action=OptActionH,
            default=None,
            help="@R:" + OptActionH.__doc__
        )
 
 
        # defined args
        # a little extra
        if self.argv == sys.argv:
            argv = self.argv[1:]
        else:
            argv = self.argv 

        group_arguments = self.parser.add_argument_group(
            'ARGUMENTS:','' 
        )
        group_arguments.add_argument(
            'ARGS',
            nargs=argparse.REMAINDER,
            help="""@R:
[--]
  The double hyphen terminates the options of the call,
  thus the remaining part of the call is treated as:
  
      <COMMAND> <argument-list>

<COMMAND>

    The supported common parameter for configuration file lists 
    within *argument-list* is:

       file-name-pattern-list := <file-name-pattern>[ <file-name-pattern-list>]

       file-name-pattern := (
            <absolute-file-path-name>
          | <relative-file-path-name>
          | <literal-file-name>
          | <glob>
       )

    The suffix could be omitted, the suffix list is searched than.
    See parameter *--suffixes*.

  CONCAT:
     Displays the concatenation of all resulting 
     configurations from the file list, where each 
     is a separate branch with the file path name
     as the key.
    
       CONCAT <file-name-pattern-list>

       see common parameter *file-name-pattern-list*

  CONFIG:
    Gets first matched file path name.
    
       CONFIG <file-name-pattern-list>

       see common parameter *file-name-pattern-list*

  ENUMERATE:
    Enumerates matched files, default is all
    within search path.

       ENUMERATE <file-name-pattern-list>

       see common parameter *file-name-pattern-list*

  ENVIRON:
    Special command for the class *ConfigEnviron*.
    Displays the resulting environment after the
    super positioning of all environment
    configuration files.

       ENVIRON <file-name-pattern-list>

       see common parameter *file-name-pattern-list*
    
    Loads implicitly *ConfigEnviron*.

  LIST:
    Lists current search paths.

  MERGE:
    Merges all provided files into one configuration
    by superpositioning and writes to 'STDOUT',
    see also '--out-format'.

       ENVIRON <file-name-pattern-list>

       see common parameter *file-name-pattern-list*

  SHOW:
     Displays for each file the resulting 
     configuration.

       SHOW <file-name-pattern-list>

       see common parameter *file-name-pattern-list*

  VERIFY:
     Verifies the syntax of each file.

       VERIFY <file-name-pattern-list>

       see common parameter *file-name-pattern-list*
  
  
"""
            )
 
        group_result = self.parser.add_argument_group(  # @UnusedVariable
            'RESULT:',
            "Success '0'."
        )
 
        group_see = self.parser.add_argument_group(  # @UnusedVariable
            'SEE ALSO:',
            """
            https://pypi.python.org/pypi/multiconf/\n
            https://pythonhosted.org/multiconf/
            """
        )
 
        group_copyright = self.parser.add_argument_group(  # @UnusedVariable
            'COPYRIGHT:',
            'Arno-Can Uestuensoez (C)2018 @Ingenieurbuero Arno-Can Uestuensoez',
        )
 
        # defined args
        if "--" in argv:
            idx = argv.index('--')
            opts, unknown = self.parser.parse_known_args(argv, namespace=_myspace)
            args = argv[idx + 1:]
        else:
            opts, unknown = self.parser.parse_known_args(argv, namespace=_myspace)
            args = opts.ARGS 

        # for later post-processing
        self.opts = _myspace
        self.args = args
        self.unknown = unknown
 
        if unknown:
            raise MultiConfError("Unknown options:" + str(unknown))

        if multiconf._debug:
            sys.stderr.write("MULTICO:CLI:PID=%d, PPID=%d\n" % (os.getpid(), os.getppid(),))

        if _myspace.debug_options:
            if self.opts.debug_options[0] == 'str':
                for k,v, in self.get_items():
                    print("%-20s: %s" % (k, v,))
            elif self.opts.debug_options[0] == 'repr':
                print(repr(self.get_JSON_bin()))
            elif self.opts.debug_options[0] == 'json':
                import jsondata.jsondata
                print(str(jsondata.jsondata.JSONData(self.get_JSON_bin())))
            else:
                raise  MultiConfError("Output format not supported for options print:" + str(self.opts.out_format))

            if len(self.opts.debug_options) == 1:
                sys.exit(0)

        return opts, unknown, args

    def get_JSON_bin(self):
        """Provides structured data of the compile task in-memory in 
        JSON format. ::

           result := {
              'allownoval': '',
              'confapp': [],
              'debug': '',
              'debug_options': '',
              'interpolation': '',
              'ignore_errors': '',
              'outform': {
                  'out_format': '',
              },
              'path': {
                  'append': [],
                  'prepend': [],
                  'replace': [],
              },
              'parser': [],
              'parser_register': [],
              'strict': '',
              'syntax': '',
              'quiet': '',
              'verbose': '',

              'args': [],
           }
        """
        j =  {}
        j['allownoval'] =  self.opts.allownoval
        j['confapp'] =  self.opts.confapp
        j['debug'] =  self.opts.debug
        j['debug_options'] =  self.opts.debug_options
        j['ignore_errors'] =  self.opts.ignore_errors
        j['interpolation'] =  self.opts.interpolation
        j['outform'] =  {}
        j['outform']['out_format'] =  self.opts.out_format
        j['parser'] =  self.opts.parser
        j['parser_register'] =  self.opts.parser_register
        j['path'] =  {}
        j['path']['append'] =  self.opts.append
        j['path']['prepend'] =  self.opts.prepend
        j['path']['replace'] =  self.opts.replace
        j['quiet'] =  self.opts.quiet
        j['strict'] =  self.opts.strict
        j['syntax'] =  self.opts.syntax
        j['verbose'] =  self.opts.verbose

        j['args'] =  self.args

        return j 

    def get_items(self):
        """Provides a list of flat str-value tuples ::

           result := [
            ('allownoval', ')'
            ('append', ')'
            ('args', []),
            ('confapp', []),
            ('debug', ''),
            ('debug_options', ''),
            ('ignore_errors', ''),
            ('interpolation', ''),
            ('out_format', ''),
            ('parser', []),
            ('parser_register', []),
            ('prepend', ''),
            ('quiet', ''),
            ('replace, ''),
            ('syntax, ''),
            ('strict, ''),
            ('verbose', ''),
           ]
        """
        return [
            ('allownoval',  self.opts.allownoval),
            ('append',  self.opts.append),
            ('args', self.args),
            ('confapp', self.opts.confapp),
            ('debug', self.opts.debug),
            ('debug_options', self.opts.debug_options),
            ('ignore_errors', self.opts.ignore_errors),
            ('interpolation', self.opts.interpolation),
            ('out_format', self.opts.out_format),
            ('parser', self.opts._parser),
            ('parser_register', self.opts._parser_register),
            ('prepend', self.opts.prepend),
            ('quiet', self.opts.quiet),
            ('replace', self.opts.replace),
            ('strict', self.opts.strict),
            ('syntax', self.opts.syntax),
            ('verbose', self.opts.verbose),
        ]

    def print_usage(self, *args):
        self.parser.print_usage(*args)

    def print_help(self, *args):
        self.parser.print_help(*args)
