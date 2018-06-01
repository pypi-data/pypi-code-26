#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from genestack_client import (FilesUtil, get_connection,
                              make_connection_parser)

@pytest.fixture(scope='module')
def files_utils():
    connection = get_connection(make_connection_parser().parse_args())
    files_utils = FilesUtil(connection)
    return files_utils


def test_get_special_folder_created(files_utils):
    assert isinstance(files_utils, FilesUtil)
    files_utils.share_folder('GSF007281', 'GSG000006', password='pwdTester123')
    assert False

if __name__ == '__main__':
    pytest.main(['-v', '--tb', 'long', __file__])
