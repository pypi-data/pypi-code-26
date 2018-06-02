import os
import json


def load(location, auto_save=True):
    return Database(location, auto_save)


class Database:
    def __init__(self, path, auto_save=True):
        self.db = None
        self.location = None
        self.auto_save = None

        self.load(path, auto_save)

    def _load(self):
        file = open(self.location, 'r')
        self.db = json.loads(file.read())
        file.close()

    def _dump(self):
        file = open(self.location, 'wt')
        json.dump(self.db, file)
        file.close()

    def _auto_save(self):
        if self.auto_save:
            self._dump()

    def load(self, location, auto_save):
        location = os.path.expanduser(location)

        self.location = location
        self.auto_save = auto_save

        if os.path.exists(location):
            self._load()
        else:
            self.db = {}

        return True

    def dump(self):
        self._dump()
        return True

    def get(self, key):
        try:
            return self.db[key]
        except KeyError:
            return None

    def set(self, key, value):
        self.db[key] = value
        self._auto_save()
        return True

    def drop(self, key):
        del self.db[key]
        self._auto_save()
        return True

    def get_keys(self):
        return set(self.db.keys())
