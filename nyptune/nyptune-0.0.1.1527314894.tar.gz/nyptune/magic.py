import pprint
import json, base64
from subprocess import *
from pathlib import Path
from abc import ABC, abstractmethod
from collections import namedtuple
import pickle, os
import hashlib
from IPython.core.magic import *
from .util import *
from nyptune.cache import *
from collections import namedtuple
from collections import OrderedDict


@magics_class
class CacheMagics(Magics):

    def __init__(self, **kwargs):
        super(CacheMagics, self).__init__(**kwargs)
        cacheargs = kwargs.copy()
        del (cacheargs["shell"])
        self._cache = Cache(**cacheargs)
        self.enabled = True

    @line_cell_magic
    def nyptune_name(self, line, cell=None):
        """Set the namespace used by this cache.  This should be similar to the notebook name
        and will cause other notebooks with the same nyptune_name on this computer to share 
        cache entries."""
        self._cache.name = line.strip()

    @line_cell_magic
    def nyptune_secret(self, line, cell=None):
        """Optionally set the encryption key used by this cache, if desired."""
        self._cache.secret = line.strip()

    @line_magic
    def caching(self, line):
        line = line.strip()
        if line == "on":
            self.enabled = True
        elif line == "off":
            self.enabled = False

    @line_magic
    def invalidate(self, line, cell=None):
        """Remove the names listed from the cache.  Note that this does not clean up much disk 
        space until you run `nyptune gc`."""
        names = line.strip().split()
        for name in names:
            self._cache.invalidate(name)

    @line_cell_magic
    def recache(self, line, cell=None):
        """Recalculate and saves into cache this line/cell."""
        self._cache(line, cell, overwrite=True)

    def checkpoint(self, *names):
        for name in names:
            value = self.shell.user_ns[name]
            self.shell.user_ns[name] = self._cache.cache(name, value)
        self._cache.save()

    def restore(self, *names):
        for name in names:
            self.shell.user_ns[name] = self._cache.retrieve(name)

    def is_cached(self, *names):
        for name in names:
            if not self._cache.is_cached(name):
                return False
        return True

    @line_cell_magic
    def cache(self, line, cell=None, overwrite=False):
        names = line.strip().split()
        if cell:
            m = hashlib.md5()
            m.update(cell.encode("utf-8"))
            cell_id = m.hexdigest()
            if self.enabled:
                if self.is_cached(*names) and not overwrite:
                    self.restore(*names)
                    if self._cache.is_cached(cell_id):
                        return self._cache.retrieve(cell_id).result
                    else:
                        print(
                            "Your variables were restored from cache, but we could not find the output of this cell in cache"
                        )
                        return None
                else:
                    output = self.shell.run_cell(cell)
                    self._cache.cache(cell_id, output)
                    self.checkpoint(*names)
                    return output.result
            else:
                return self.shell.run_cell(cell)
        else:
            name = names[0]
            if self.enabled:
                if self.is_cached(name) and not overwrite:
                    return self.restore(name)
                else:
                    self.shell.run_cell(line)
                    self.checkpoint(name)
                    return self.shell.user_ns[name]
            else:
                self.shell.run_cell(line)
                return self.shell.user_ns[name]
