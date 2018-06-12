# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: Red Hat Inc. 2018
# Author: Cleber Rosa <crosa@redhat.com>

"""
Asset fetcher/cache command
"""

from avocado.core.output import LOG_UI
from avocado.core.plugin_interfaces import CLICmd


class Asset(CLICmd):

    """
    Implements the avocado 'asset' subcommand
    """

    name = 'asset'
    description = "Inspects the asset cache"

    def configure(self, parser):
        parser = super(Asset, self).configure(parser)
        parser.add_argument("urls", type=str, default=[], nargs='*',
                            metavar="URL_OR_NAME",
                            help='List of asset URLs or file names')

    def _download(self, url):
        pass

    def run(self, args):
        for url in args.urls:
            LOG_UI.info("Checking %s", url)
            self._download()
