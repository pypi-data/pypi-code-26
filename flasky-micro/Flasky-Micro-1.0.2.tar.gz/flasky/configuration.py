import os
import yaml
from .exceptions import ConfigurationException
from .exceptions import FileNotFoundException
from .exceptions import KeyNotFoundException
from .exceptions import FormatValueException


class Configuration:

    def __init__(self):
        self.config = None

    def load(self, file):
        if not file or not os.path.exists(file):
            raise FileNotFoundException(file)

        try:
            with open(file, "r") as file:
                self.config = yaml.load(file)
        except Exception as ex:
            raise ConfigurationException(ex)

    def get(self, *key, default=None, required=False, formatter=None):
        value = self.config
        for k in key:
            if value is not None:
                if type(value) is dict:
                    value = value.get(k, None)
                else:
                    raise ConfigurationException("Configuration key is not a dict")

        if value is None:
            if required:
                raise KeyNotFoundException(key)
            else:
                return default

        if formatter and value:
            try:
                value = formatter(value)
            except:
                raise FormatValueException(value)

        return value

    def get_by_path(self, path, default=None, required=False, formatter=None):
        keys = self._split_path(path)
        return self.get(*keys, default=default, required=required, formatter=formatter)

    def _split_path(self, path, delimiter=".", escape="\\"):
        ret = []
        current = []
        itr = iter(path)
        for ch in itr:
            if ch == escape:
                try:
                    current.append(next(itr))
                except StopIteration:
                    continue
            elif ch == delimiter:
                ret.append("".join(current))
                current = []
            else:
                current.append(ch)
        ret.append("".join(current))
        return ret
