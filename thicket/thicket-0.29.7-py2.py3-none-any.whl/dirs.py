#!/usr/bin/env python

from os.path import isdir

from thicket.paths import Path


class Directory(Path):
    type = 'directory'

    @staticmethod
    def is_dir(path):
        return isdir(path)
