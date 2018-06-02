#!/usr/bin/env python
import datetime
import mimetypes
import os
from os.path import exists, isdir, isfile


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


def get_mimetype(path):
    if not mimetypes.guess_type(path)[0]:
        return ''
    return mimetypes.guess_type(path)[0]


def get_media_type(path):
    try:
        return get_mimetype(path).split('/')[0]
    except:
        return ''
