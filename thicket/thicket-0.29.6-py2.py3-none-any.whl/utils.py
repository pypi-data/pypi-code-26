#!/usr/bin/env python
import datetime
import os
from os.path import exists
from os.path import isdir
from os.path import isfile
import mimetypes
from thicket.ffmpeg_wrapper.utils import is_video

try:
    from string import maketrans
except ImportError:
    maketrans = str.maketrans

from thicket.info import MIME_EXTENSION_DICT


# For backwards compatibility. Previously, this module include unnecessary functions:
# def is_dir() and def is_file().
from os.path import isdir as is_dir
from os.path import isfile as is_file


def remove_nondigits(string_arg):
    """
    Removes all non-digits (letters, symbols, punctuation, etc.)
    :param str:
    :return: string consisting only of digits
    :rtype: str
    """

    return ''.join(filter(lambda x: x.isdigit() or x == '.', string_arg))


def get_path_type(path):
    """
    Gets the type of a path. Acceptable return values: 'directory', 'file', and ''.
    :param str path:
    :return: 'directory', 'file', and ''
    :rtype: str
    """

    if exists(path):
        if isfile(path):
            return 'file'
        elif isdir(path):
            return 'directory'
        raise ValueError('Path exists, but is neither file nor directory. WTF!!??')

    return ''


def is_image(path):
    if isfile(path):
        try:
            mime = get_mimetype(path).split('/')
        except AttributeError:
            return False
        if mime[0] == 'image':
            return True
    return False


def get_size(path):
    return os.stat(path).st_size


def get_inode(path):
    return os.stat(path).st_ino


def get_atime(path):
    return datetime.datetime.fromtimestamp(os.stat(path).st_atime)


def get_mtime(path):
    return datetime.datetime.fromtimestamp(os.stat(path).st_mtime)


def get_ctime(path):
    return datetime.datetime.fromtimestamp(os.stat(path).st_ctime)


def get_folder_size(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += get_folder_size(itempath)
    return total_size


# todo: add get mimetype util here. change test to accompany it.
def get_mimetype(path):
    return mimetypes.guess_type(path)[0]
