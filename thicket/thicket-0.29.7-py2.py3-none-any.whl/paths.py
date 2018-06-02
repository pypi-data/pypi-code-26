#!/usr/bin/env python
import os

from thicket.utils import get_atime, get_ctime, get_folder_size, get_inode, get_mtime, get_path_type, get_size


class Path(object):

    type = 'path'

    def __init__(self, path):
        self.initial_path = str(path)

    @property
    def initial_abspath(self):
        return os.path.abspath(self.initial_path)

    @property
    def path_type(self):
        return get_path_type(self.abspath)

    @property
    def abspath(self):
        return self.initial_abspath

    @property
    def dir_name(self):
        return os.path.dirname(self.abspath)

    @property
    def name_ext(self):
        return os.path.splitext(self.abspath)[1]

    @property
    def name_base(self):
        return self.name[:-abs(len(self.name_ext))]

    @property
    def name(self):
        return self.abspath.split('/')[-1]

    @property
    def size(self):
        return get_size(self.abspath)

    @property
    def dir_size(self):

        if self.exists:

            if self.path_type == 'directory':
                size = get_folder_size(self.abspath)

            elif self.path_type == 'file':
                size = get_folder_size(self.dir_name)

            else:
                raise ValueError("Path exists, but is not a directory or file - WTF!!??")
        else:
            size = None

        return size

    @property
    def inode(self):
        return get_inode(self.abspath)

    @property
    def realpath(self):
        if self.is_link:
            result = os.path.realpath(self.abspath)
            if result == self.abspath:
                raise Exception("Cyclical link - will loop forever")
            return result
        return self.abspath

    @property
    def is_link(self):
        return os.path.islink(self.abspath)

    @property
    def exists(self):
        return os.path.exists(self.abspath)

    @property
    def stat(self):
        return os.stat(self.abspath)

    @property
    def atime(self):
        return get_atime(self.abspath)

    @property
    def mtime(self):
        return get_mtime(self.abspath)

    @property
    def ctime(self):
        return get_ctime(self.abspath)

    @property
    def dropbox_name(self, seperator=''):
        date = self.mtime.date().isoformat()
        time = self.mtime.time().isoformat()

        if not seperator:
            return '{} {}{}'.format(date, time, self.name_ext.lower())

        return '{}{}{}{}'.format(date, seperator, time, self.name_ext.lower())

    def __str__(self):
        return '<{} at {}>'.format(self.__class__.__name__, self.abspath)

    def __repr__(self):
        return '<{} at {}>'.format(self.__class__.__name__, self.abspath)

    def rename(self, new_name):
        dir_name = self.dir_name
        new_name = os.path.join(dir_name, new_name)
        os.rename(self.abspath, new_name)
