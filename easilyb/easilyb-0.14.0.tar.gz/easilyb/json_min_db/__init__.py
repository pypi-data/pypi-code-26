from threading import Lock
import os
import easilyb.json_serialize as jsons
import json
import yaml


def _load_json(path, driver=jsons):
    with open(path) as fin:
        return driver.load(fin)


def _save_json(data, path, indent=None, driver=jsons):
    with open(path, 'w') as fou:
        if driver == yaml:
            driver.dump(data, fou, indent=indent, default_flow_style=False)
        else:
            driver.dump(data, fou, indent=indent)


class JsonMinConnexion:
    """Minimalistic Json Database Connexion class."""

    def __init__(self, path, create=True, template=None, template_file=None, indent=3, readonly=False, driver="jsons"):
        """JsonMinDb constructor.

        :param path: json file path.
        :type path: str.
        :param create: Create if json file does not exist.
        :type create: bool.
        :param template: if create is True, create from template.
        :type template: dict.
        :param template_file: if create is True and template is None, create from template_file.
        :type template_file: str.
        :param indent: if create is True, create from template.
        :type indent: int.
        :raises: ValueError

        """
        self.path = path
        self.indent = indent
        self.readonly = readonly
        self.lock = Lock()
        if driver == "json":
            self.driver = json
        elif driver == "yaml":
            self.driver = yaml
        elif driver == "jsons" or driver == "json_serialize":
            self.driver = jsons
        else:
            raise ValueError("Unkown driver: %s!" % driver)
        if not os.path.isfile(path):
            if create:
                if template:
                    _template = template
                elif template_file:
                    _template = _load_json(template_file, driver=self.driver)
                else:
                    _template = {}

                _save_json(_template, path, indent=indent, driver=self.driver)
                self.db = _load_json(path, driver=self.driver)
            else:
                raise ValueError("Database file doesn't exist: " + path)
        self.db = _load_json(path, driver=self.driver)

        # db dict calls
        # self.__contains__ = self.db.__contains__
        # self.__delitem__ = self.db.__delitem__
        # self.__getitem__ = self.db.__getitem__
        # self.__iter__ = self.db.__iter__
        # self.__len__ = self.db.__len__
        # self.__setitem__ = self.db.__setitem__
        #
        # #self.clear = self.db.clear
        # #self.copy = self.db.copy
        # #self.fromkeys = self.db.fromkeys
        # try: # only in python2
        #     self.has_key = self.db.has_key
        #     self.iteritems = self.db.iteritems
        #     self.iterkeys = self.db.iterkeys
        #     self.itervalues = self.db.itervalues
        # except:
        #     pass
        # self.items = self.db.items
        # self.keys = self.db.keys
        # self.update = self.db.update
        # self.values = self.db.values

    def __contains__(self, k):
        return self.db.__contains__(k)

    def __delitem__(self, k):
        return self.db.__delitem__(k)

    def __getitem__(self, k):
        return self.db.__getitem__(k)

    def __iter__(self):
        return self.db.__iter__()

    def __len__(self):
        return self.db.__len__()

    def __setitem__(self, k, o):
        return self.db.__setitem__(k, o)

    def items(self):
        return self.db.items()

    def keys(self):
        return self.db.keys()

    def update(self):
        return self.db.update()

    def values(self):
        return self.db.values()

    def has_key(self):
        try: return self.db.has_key()
        except: pass

    def save(self):
        """updates database persistance file in the disk. """
        if self.readonly:
            raise Exception("Read Only Access!")
        _save_json(self.db, self.path, indent=self.indent, driver=self.driver)

    def reload(self):
        """reload database from disk."""
        self.db = _load_json(self.path, driver=self.driver)

    def __str__(self):
        return "<kutils.json_min_db.JsonMinConnexion instance %s>" % self.db.__str__()

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.save()
        finally:
            self.lock.release()
