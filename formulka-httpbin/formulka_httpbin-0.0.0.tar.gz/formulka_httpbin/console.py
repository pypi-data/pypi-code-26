# -*- coding: utf-8 -*-
# Copyright (c) 2018 Petr Olah <djangoguru@gmail.com>
#
# this file is part of the project "Petr Olah HTTPBin Client" released under the "MIT" open-source license

"""formulka-httpbin's command-line utility

Ideally use a tool such as `click <http://click.pocoo.org/5/>`_

For more information check py:func:`click.command` and py:class:`click.Command`
"""

from formulka_httpbin import HttpBinClient


def entrypoint():
    client = HTTPBinClient()
    print("your IP is: " + client.ip())
    raise SystemExit(1)


if __name__ == '__main__':
    # this makes the script executable without needing to install
    # the formulka-httpbin package
    entrypoint()
