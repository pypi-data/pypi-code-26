# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

import sys
import os                 # NOQA

from ruamel.std.argparse import ProgramBase, option, CountAction, \
    SmartFormatter, sub_parser, version, store_true
from ruamel.appconfig import AppConfig
from ruamel.std.pathlib import Path

from . import __version__
from .virtualenvutils import VirtualEnvUtils


def to_stderr(*args):
    sys.stderr.write(' '.join(args))


class VirtualEnvUtilsCmd(ProgramBase):
    def __init__(self):
        super(VirtualEnvUtilsCmd, self).__init__(
            formatter_class=SmartFormatter,
            # aliases=True,
            # usage="""""",
        )

    # you can put these on __init__, but subclassing VirtualEnvUtilsCmd
    # will cause that to break
    @option('--verbose', '-v',
            help='increase verbosity level', action=CountAction,
            const=1, nargs=0, default=0, global_option=True)
    @version('version: ' + __version__)
    def _pb_init(self):
        # special name for which attribs are included in help
        pass

    def run(self):
        self.virtualenvutils = VirtualEnvUtils(self._args, self._config)
        if hasattr(self._args, 'func'):  # not there if subparser selected
            return self._args.func()
        self._parse_args(['--help'])     # replace if you use not subparsers

    def parse_args(self):
        self._config = AppConfig(
            'virtualenvutils',
            filename=AppConfig.check,
            parser=self._parser,  # sets --config option
            warning=to_stderr,
            add_save=False,  # add a --save-defaults (to config) option
        )
        # self._config._file_name can be handed to objects that need
        # to get other info>mation from the configuration directory
        self._config.set_defaults()
        self._parse_args(
            # default_sub_parser="",
        )

    @sub_parser(help='generate aliases from virtualenv utility installations')
    # @option('--session-name', default='abc')
    @option('dir', nargs='+')
    def alias(self):
        self.virtualenvutils.alias()

    @sub_parser(help='update packages in virtualenvs')
    @option('--python', action=store_true,
            help="upgrade Python minor version, by doing full reinstall")
    @option('--python3', action=store_true,
            help="upgrade from Python 2.x to latest 3.x, and full reinstall")
    @option('--pre', action=store_true, help="""pass on --pre to 'pip update'""")
    @option('dir', nargs='+')
    def update(self):
        self.virtualenvutils.update()

    @sub_parser(help='install package(s) in virtualenvs')
    @option('--python', '-p', type=Path,
            help='path to python binary to be used for virtualenv')
    @option('--pkg', help='name of the package to be installed (default: taken from'
            'last part of dir)')
    @option('--link', action='store_true',
            help='create a link in site-packages to current directory')
    @option('dir', nargs='+')
    def install(self):
        self.virtualenvutils.install()

    @sub_parser(help='scan versions of python and packages')
    @option('dir', nargs='+')
    def version(self):
        self.virtualenvutils.version()


def main():
    n = VirtualEnvUtilsCmd()
    n.parse_args()
    sys.exit(n.run())


if __name__ == '__main__':
    main()
