#!/usr/bin/env python
import os

from thicket.dirs import Directory
from thicket.files import File
from thicket.paths import Path
from thicket.videos import VideoFile


class PathProcessor(object):

    @staticmethod
    def process(path):
        if os.path.exists(path):
            if VideoFile.is_video(path):
                return VideoFile(path)
            if os.path.isfile(path):
                return File(path)
            if os.path.isdir(path):
                return Directory(path)
        return Path(path)
