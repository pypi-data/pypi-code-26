from . import FilePath
import os


class Path:
    def __init__(self, envvar):
        self.envvar = envvar
        self.items = []
        self.load()

    def load(self):
        items = os.environ.get(self.envvar, '').split(':')
        for item in items:
            self.items.append(FilePath(item, exist_required=False))

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, item):
        return item in self.items

    def __getitem__(self, item):
        return self.items[item]

    def __setitem__(self, key, value):
        self.items[key] = FilePath(value, exist_required=False)

    def __getattr__(self, item):
        return getattr(self.items, item)