#!/usr/bin/env python
import os
from os.path import isfile

import mimetypes

def is_video(path):
    
    if isfile(path):
        abspath = os.path.abspath(path)
        tipe = mimetypes.guess_type(abspath)[0].split('/')[0]
        if tipe == 'video':
            return True

    return False
