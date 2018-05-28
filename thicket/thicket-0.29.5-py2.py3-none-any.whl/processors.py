#!/usr/bin/env python
import os

from thicket.videos import VideoFile
from thicket.files import File
from thicket.dirs import Directory
from thicket.paths import Path


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
