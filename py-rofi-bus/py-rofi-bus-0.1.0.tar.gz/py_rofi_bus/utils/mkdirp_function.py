# pylint:disable=W,C,R
from errno import EEXIST
from os import makedirs
from os.path import isdir


def mkdirp(directory=None):
    if directory:
        try:
            makedirs(directory)
        except OSError as error:
            if EEXIST == error.errno and isdir(directory):
                pass
            else:
                raise
