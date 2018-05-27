# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import print_function

import os

import pytest
from click.testing import CliRunner
from sqlitebiter._enum import ExitCode
from sqlitebiter.sqlitebiter import cmd


class Test_file_subcommand_ipynb(object):

    @pytest.mark.parametrize(["file_path", "expected"], [
        ["test/data/pytablewriter_examples.ipynb", ExitCode.SUCCESS],
        ["test/data/jupyter_notebook_example.ipynb", ExitCode.SUCCESS],
    ])
    def test_smoke_one_file(self, file_path, expected):
        db_path = "test.sqlite"
        if os.path.isfile(db_path):
            os.remove(db_path)
        runner = CliRunner()

        result = runner.invoke(cmd, ["file", file_path, "-o", db_path])
        print(result.output)

        assert result.exit_code == expected, result.output
