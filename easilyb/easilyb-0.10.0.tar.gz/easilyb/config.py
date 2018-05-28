import logging
from easilyb.json_min_db import JsonMinConnexion
from threading import Lock

logger = logging.getLogger(__name__)
NOTHING = object()


class EasyConfig:
    def __init__(self, filepath, create=True, template=None, template_file=None, indent=3, driver="yaml"):
        self.db = JsonMinConnexion(filepath, create=create, template=template, template_file=template_file,
                                   indent=indent, driver=driver)
        self._lock = Lock()
        self._save = True

    def get(self, key, default=NOTHING, set_default=True, save=True):
        try:
            return self.db[key]
        except:
            if default == NOTHING:
                raise KeyError(key)
            else:
                if set_default:
                    self.set(key, default, save=save)
                return default

    def set(self, key, value, save=True):
        if self._save:
            with self._lock:
                self.db[key] = value
                if save:
                    self.db.save()
        else:
            self.db[key] = value

    def save(self):
        self.db.save()

    def __enter__(self):
        self._lock.acquire()
        self._save = False
        self.db.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.db.__exit__(exc_type, exc_val, exc_tb)
        finally:
            self._save = True
            self._lock.release()
