from .base import DirectoryBase
import os, pathlib, fnmatch


class LocalDirectory(DirectoryBase):
    """A simple local directory on the FileSystem.
    """

    def __init__(self, path):
        self.root = pathlib.Path(path)
        os.makedirs(self.root, exist_ok=True)

    def glob(self, pattern):
        return [
            file for file in os.listdir(self.root) if fnmatch.fnmatch(file, pattern)
        ]

    def remove(self, name):
        os.unlink(self.root / name)

    def exists(self, name):
        return (self.root / name).is_file()

    def writer(self, name):
        return open(self.root / name, "wb")

    def reader(self, name):
        return open(self.root / name, "rb")
