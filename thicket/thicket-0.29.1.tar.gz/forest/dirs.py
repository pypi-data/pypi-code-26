#!/usr/bin/env python
import os

from forest.paths import Path
from forest.utils import is_dir


class Directory(Path):
    type = 'directory'

    @staticmethod
    def is_dir(path):
        return is_dir(path)
