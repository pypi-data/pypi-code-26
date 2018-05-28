#!/usr/bin/env python
import os

from thicket.paths import Path
from thicket.utils import is_dir


class Directory(Path):
    type = 'directory'

    @staticmethod
    def is_dir(path):
        return is_dir(path)
