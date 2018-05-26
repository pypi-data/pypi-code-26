from .handler.path import PathHandler
from .handler.pickle import PickleHandler
from .directory.local import LocalDirectory
from pathlib import Path
import json, io


class Cache:

    @classmethod
    def default_handlers(cls):
        return [PathHandler(), PickleHandler()]

    def __init__(
        self,
        name="default",
        directory=LocalDirectory(Path.home() / ".nyptune"),
        secret=None,
        handlers=None,
    ):
        """Create a new instance of a Cache in the specified Directory."""
        self.base_directory = directory
        self.secret = secret
        self.name = name
        self.handlers = handlers or self.default_handlers()

    def save(self):
        """Writes a listing of the currently cached files/metadata to NAME.json"""
        with self.directory.writer(self.namespace + ".json") as file:
            json.dump(self.metadata, io.TextIOWrapper(file))

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, secret):
        self._secret = secret
        if secret:
            self.directory = EncryptedDirectory(self.base_directory, secret)
        else:
            self.directory = self.base_directory

    @property
    def name(self):
        return self.namespace

    @name.setter
    def name(self, name):
        self.namespace = name
        if self.directory.exists(name + ".json"):
            try:
                with self.directory.reader(name + ".json") as file:
                    self.metadata = json.load(file)
            except:
                print("cannot read metadata, continuing")
                self.metadata = {}
        else:
            self.metadata = {}

    def is_cached(self, name):
        return name in self.metadata

    def retrieve(self, name):
        metadata = self.metadata[name]
        handler = [
            h for h in self.handlers if h.__class__.__name__ == metadata["type"]
        ][0]
        with self.directory.reader(metadata["checksum"]) as file:
            return handler.deserialize(metadata, file)

    def cache(self, name, value, save=True):
        for handler in self.handlers:
            existing = self.metadata.get(name, {})
            if handler.understands(value):
                if handler.checksum_matches_existing(value, existing):
                    pass
                else:
                    metadata = existing
                    metadata["type"] = handler.__class__.__name__
                    metadata["quicksum"] = handler.quicksum(value)
                    metadata["checksum"] = handler.checksum(value)
                    with self.directory.writer(metadata["checksum"]) as file:
                        more = handler.serialize(value, file)
                        self.metadata[name] = {**metadata, **more}
                if save:
                    self.save()
                return

    def invalidate(self, name):
        del (self.metadata[name])
