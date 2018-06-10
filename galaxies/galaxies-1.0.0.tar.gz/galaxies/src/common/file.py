# -*- coding: utf-8 -*-
""" This module contains commons methods which has no dependencies (except for
the base python library) and thus are usable in every part of the software.

The methods included in this modules are all file-related functions.
"""

import mmap
import os
import os.path
import shelve


def line_count(file_path: str) -> int:
    """ Efficiently count the number of lines in a file.
    If possible, the UNIX command `wc -l` must be used instead (as its much
    faster).
    """
    f = open(file_path, "r+")
    buf = mmap.mmap(f.fileno(), 0)
    lines = 0
    read_line = buf.readline
    while read_line():
        lines += 1
    return lines


def delete_existing_files(*file_paths) -> None:
    """ Delete all files passed as parameters. """
    for file_path in file_paths:
        if os.path.isfile(file_path):
            os.remove(file_path)


def print_shelve(path_file: str) -> None:
    """ Display the content of a shelve object with the key alphabetically sorted. """
    with shelve.open(path_file) as dictionary:
        for key in sorted(list(dictionary.keys())):
            print(key, dictionary[key])


def makedirs(*directories, exist_ok: bool) -> None:
    """ Wrapper for the os.makedirs function with multiple parameters. """
    for directory in directories:
        os.makedirs(directory, exist_ok=exist_ok)


if __name__ == "__main__":
    pass
