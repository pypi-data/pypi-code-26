#!/usr/bin/env python
import os
from os.path import isfile

from thicket.utils import get_media_type


def is_video(path):

    if not path:
        return False

    if isfile(path):
        abspath = os.path.abspath(path)
        media_type = get_media_type(abspath)
        if media_type == 'video':
            return True

    return False
