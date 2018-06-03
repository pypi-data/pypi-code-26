# -*- coding: utf-8 -*-
# Copyright (c) 2018 Tomáš Linhart <pasmen@gmail.com>
#
# this file is part of the project "Tomáš Linhart HTTPBin Client" released under the "MIT" open-source license

"""tlinhart-httpbin's command-line utility

Ideally use a tool such as `click <http://click.pocoo.org/5/>`_

For more information check py:func:`click.command` and py:class:`click.Command`
"""

from tlinhart_httpbin.client import HttpBinClient

def entrypoint():
    client = HttpBinClient()
    print(client.ip())


if __name__ == '__main__':
    # this makes the script executable without needing to install
    # the tlinhart-httpbin package
    entrypoint()
