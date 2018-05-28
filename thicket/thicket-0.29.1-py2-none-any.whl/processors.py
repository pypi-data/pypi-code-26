#!/usr/bin/env python
import os

from forest.videos import VideoFile
from forest.files import File
from forest.dirs import Directory
from forest.paths import Path


class PathProcessor(object):

    @staticmethod
    def process(path):
        if os.path.exists(path):
            if os.path.isfile(path):
                return File(path)
            if os.path.isdir(path):
                return Directory(path)
        else:
            return Path(path)
