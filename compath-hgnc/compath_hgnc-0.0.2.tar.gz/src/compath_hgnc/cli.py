# -*- coding: utf-8 -*-

"""Builds the CLI for ComPath HGNC."""

import logging

from .manager import Manager

log = logging.getLogger(__name__)

main = Manager.get_cli()

if __name__ == '__main__':
    main()
