#!/usr/bin/env python
# coding: utf-8
"""
utility functions
"""
__author__ = "Riku Okajima<riku.okajima@gmail.com>"
__date__ = "2018-06-04"

import datetime
import pathlib
import re
from subprocess import Popen
from typing import List


def create_file(path: str, lines: List[str]):
    """
    create file with given lines
    """
    with open(path, "w") as fo:
        fo.write("\n".join(lines))


def format_parameter(param: List[str]) -> str:
    """
    format string of qsub parameter
    """
    return "#$ {}".format(" ".join(param))


def escape_string(string: str) -> str:
    """
    escape special chars(\();)
    """
    return re.sub(r"(?<!\\)([[\];()])", r"\\\1", string)


def exec_script(path: str, qsub="/opt/uge/bin/lx-amd64/qsub"):
    popen = Popen([qsub, path])
    popen.wait()


def aquire_script_path(directory: str, name: str) -> str:
    num = 0
    directory = pathlib.Path(directory)
    if not directory.exists():
        directory.mkdir(parents=True)
    while True:
        path = directory / "{}_{}_{:03}.sh".format(
            name,
            datetime.datetime.today().strftime("%y%m%d%H"),
            num
        )
        if not path.is_file():
            break
        num += 1
    return path
