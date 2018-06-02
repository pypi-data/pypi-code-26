#!/usr/bin/env python
import hashlib
import os
import shutil
from os.path import isfile

import magic
import xxhash

from thicket.paths import Path
from thicket.utils import get_media_type, get_mimetype


class File(Path):

    type = 'file'

    @property
    def info(self):
        return magic.from_file(self.abspath)

    def create_hard_link(self, link_path):
        os.link(self.abspath, link_path)
        return True

    def create_symbolic_link(self, link_path, relative=False):
        if not relative:
            os.symlink(self.abspath, link_path)
            return True

    def copy_file(self, new_path, hard_link=True, symbolic_link=False, preserve_attributes=True):
        if hard_link:
            try:
                self.create_hard_link(new_path)
                return True
            except OSError:
                pass

        elif symbolic_link:
            self.create_symbolic_link(self.abspath, new_path)
            return True

        elif preserve_attributes:
            try:
                shutil.copy2(self.abspath, new_path)
                return True
            except shutil.Error:
                return False

        else:
            shutil.copy(self.abspath, new_path)
        return True

    def open_file(self, mode='r'):
        mode = mode.replace('b', '')
        return open(self.abspath, mode + 'b')

    def read_file(self):
        return self.open_file().read()

    @property
    def xxhash32(self):
        hasher = xxhash.xxh32()
        with open(self.abspath, 'rb') as open_file:
            while True:
                data = open_file.read(65536)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()

    @property
    def xxhash64(self):
        hasher = xxhash.xxh64()
        with open(self.abspath, 'rb') as open_file:
            while True:
                data = open_file.read(65536)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()

    @property
    def md5(self):
        hasher = hashlib.md5()
        with open(self.abspath, 'rb') as open_file:
            while True:
                data = open_file.read(65536)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()

    @property
    def sha1(self):
        hasher = hashlib.sha1()
        with open(self.abspath, 'rb') as open_file:
            while True:
                data = open_file.read(65536)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()

    @property
    def sha256(self):
        hasher = hashlib.sha256()
        with open(self.abspath, 'rb') as open_file:
            while True:
                data = open_file.read(65536)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()

    @property
    def sha512(self):
        hasher = hashlib.sha512()
        with open(self.abspath, 'rb') as open_file:
            while True:
                data = open_file.read(65536)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()

    @property
    def big_name(self, seperator='_'):
        date = self.mtime.date().isoformat()
        time = self.mtime.time().isoformat()
        date_name = '{}{}{}'.format(date, seperator, time)

        hash_value = self.sha1
        return '{}{}{}{}'.format(date_name, seperator, hash_value, self.name_ext.lower())

    @property
    def mime(self):
        return get_mimetype(self.abspath)

    @property
    def media_type(self):
        return get_media_type(self.abspath)

    @staticmethod
    def is_file(path):
        return isfile(path)
