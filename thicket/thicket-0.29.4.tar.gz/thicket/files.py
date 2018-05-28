#!/usr/bin/env python
import hashlib
import os
import shutil
import magic
import xxhash

from thicket.paths import Path
from thicket.utils import is_file, get_mime_from_extension


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
        hash = xxhash.xxh32()
        with open(self.abspath, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                hash.update(data)
        return hash.hexdigest()

    @property
    def xxhash64(self):
        hash = xxhash.xxh64()
        with open(self.abspath, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                hash.update(data)
        return hash.hexdigest()

    @property
    def md5(self):
        hash = hashlib.md5()
        with open(self.abspath, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                hash.update(data)
        return hash.hexdigest()

    @property
    def sha1(self):
        hash = hashlib.sha1()
        with open(self.abspath, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                hash.update(data)
        return hash.hexdigest()

    @property
    def sha256(self):
        hash = hashlib.sha256()
        with open(self.abspath, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                hash.update(data)
        return hash.hexdigest()

    @property
    def sha512(self):
        hash = hashlib.sha512()
        with open(self.abspath, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                hash.update(data)
        return hash.hexdigest()

    @property
    def big_name(self, seperator='_'):
        date = self.mtime.date().isoformat()
        time = self.mtime.time().isoformat()
        dn = '{}{}{}'.format(date, seperator, time)

        hash = self.sha1
        return '{}{}{}{}'.format(dn, seperator, hash, self.name_ext.lower())

    @property
    def mime(self):
        return get_mime_from_extension(self.name_ext)

    @staticmethod
    def is_file(path):
        return is_file(path)
