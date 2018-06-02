#!/usr/bin/env python

from collections.abc import MutableSequence
from os.path import isdir, isfile


class Collection(list, MutableSequence):

    @property
    def items(self):
        return self

    @property
    def tolist(self):
        return list(self)

    @property
    def num_items(self):
        return len(self)

    @property
    def files(self, tolist=False):

        if not tolist:
            return Collection([item for item in self.items if isfile(item.abspath)])

        return [item for item in self.items if isfile(item.abspath)]

    @property
    def dirs(self, tolist=False):

        if not tolist:
            return Collection([item for item in self.items if isdir(item.abspath)])

        return [item for item in self.items if isdir(item.abspath)]

    @property
    def images(self, tolist=False):
        if not tolist:
            return Collection([item for item in self.files.items if item.mime[0] == 'image'])

        return [item for item in self.files.items if item.mime[0] == 'image']

    @property
    def pngs(self, tolist=False):

        if not tolist:
            return Collection([item for item in self.images.items if item.mime[1] == 'png'])

        return [item for item in self.images.items if item.mime()[1] == 'png']

    @property
    def jpgs(self, tolist=False):

        if not tolist:
            return Collection([item for item in self.images.items if item.mime[1] == 'jpg' or item.mime[1] == 'jpeg'])

        return [item for item in self.images.items if item.mime[1] == 'jpg' or item.mime[1] == 'jpeg']

    @property
    def gifs(self, tolist=False):

        if not tolist:
            return Collection([item for item in self.files.items if item.mime[0] == 'gif'])

        return [item for item in self.files.items if item.mime[0] == 'gif']

    @property
    def tiffs(self, tolist=False):

        if not tolist:
            return Collection([item for item in self.files.items if item.mime[0] == 'tiff'])

        return [item for item in self.files.items if item.mime[0] == 'tiff']

    def copy_files(self, file_path_string):
        for item in self.files.items:
            item.copy_file(file_path_string, hard_link=False, symbolic_link=False, preserve_attributes=True)
