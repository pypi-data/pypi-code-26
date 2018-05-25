import os
import importlib
import json
import jsonschema
from collections import MutableMapping, OrderedDict

import yaml
from yaml import SafeLoader, SafeDumper
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .storage.base import StorageConfig
from .storage.memory import MEMORY_REPOSITORY
from .storage import (
    SQLiteConfig,
    MemoryConfig,
)


BASE_SCHEMA = """
type: object
required:
    - storage
properties:
  storage:
    type: object
    required:
        - engine
        - config
        - module
    properties:
      engine:
        type: string
      config:
        type: string
      module:
        type: string
"""


class AttribDict(MutableMapping):
    """
    Based on source:
    Thanks @nivk
    https://stackoverflow.com/a/47081357/4145300
    """

    def __init__(self, ordered):
        super(AttribDict, self).__setattr__('cnf', OrderedDict(ordered))

    def __repr__(self, indent=None):
        return json.dumps(self.cnf, default=OrderedDict, indent=indent)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setattr__(self, key, val):
        self.__setitem__(key, val)

    def __delitem__(self, key):
        raise RuntimeError("Can not delete option.")

    def __getitem__(self, key):
        if key not in self.cnf:
            raise RuntimeError("Option {!r} does not exists.".format(key))
        return self.cnf[key]

    def __setitem__(self, key, val):
        if key not in self.cnf:
            raise RuntimeError("Adding new option is not allowed.")
        self.cnf[key] = val

    def __iter__(self):
        return iter(self.cnf)

    def __len__(self):
        return len(self.cnf)

    def __restriction__(self, *args, **kwargs):
        raise RuntimeError('Can not use this method.')

    clear = __restriction__
    pop = __restriction__
    popitem = __restriction__
    setdefault = __restriction__
    update = __restriction__

    def pretty(self):
        return self.__repr__(indent=4)

    def reload(self, repository=None, update=None):
        if repository is not None:
            configure = MontyConfigure(repository)
            if not configure.exists():
                raise RuntimeError("Config file must be saved before reload.")
            update = configure.load().config

        for key in self.cnf:
            # new config should have the same key.
            val = update[key]
            if isinstance(self.cnf[key], AttribDict):
                self.cnf[key].reload(update=val)
            else:
                self.cnf[key] = val


def yaml_config_load(stream, Loader=Loader, object_pairs_hook=AttribDict):
    """
    Based on source:
    Thanks @coldfix
    https://stackoverflow.com/a/21912744/4145300
    """
    class AttribLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    AttribLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)

    return yaml.load(stream, AttribLoader)


def yaml_config_dump(data, stream=None, Dumper=Dumper, **kwds):
    """
    Based on source:
    Thanks @coldfix.
    https://stackoverflow.com/a/21912744/4145300
    """
    class AttribDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    AttribDumper.add_representer(AttribDict, _dict_representer)

    return yaml.dump(data, stream, AttribDumper, **kwds)


class MontyConfigure(object):
    """
    Args:
        repository (str): Database root directory path.

        storage_config (str, optional): YAML format config string.
            Defaults to `montydb.storage.SQLiteConfig`.
            If no `conf.yaml` config file exists in `repository` path,
            will take this parameter and save as `conf.yaml`.
            Ignored if `conf.yaml` exists.
    """

    __config_filename = "conf.yaml"

    def __init__(self, repository):
        self.in_memory = repository == MEMORY_REPOSITORY
        self._repository = repository
        self._config = None
        self._schema = None

    def __repr__(self):
        return "MontyConfigure(\n{})".format(self.to_yaml())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.save()

    def _get_storage_engine(self):
        """Get storage engine from config
        """
        engine_cls_name = self._config.storage.engine
        module = importlib.import_module(self._config.storage.module)
        engine_cls = getattr(module, engine_cls_name)
        return engine_cls(self._repository, self._config)

    def _get_storage_config_schema(self):
        """Get storage engine config schema from config
        """
        config_cls_name = self._config.storage.config
        module = importlib.import_module(self._config.storage.module)
        config_cls = getattr(module, config_cls_name)
        return config_cls.schema

    @property
    def config(self):
        return self._config

    @property
    def config_path(self):
        if self.in_memory:
            return None
        return os.path.join(self._repository, self.__config_filename)

    def validate(self):
        yaml_config = self.to_yaml()
        jsonschema.validate(yaml.load(yaml_config, SafeLoader),
                            yaml.load(BASE_SCHEMA, SafeLoader))
        if self._schema:
            jsonschema.validate(yaml.load(yaml_config, SafeLoader),
                                yaml.load(self._schema, SafeLoader))

    def to_yaml(self):
        return yaml_config_dump(self._config,
                                Dumper=SafeDumper,
                                default_flow_style=False)

    def load(self, storage_config=None):
        if self.in_memory:
            storage_config = MemoryConfig
        elif storage_config and not issubclass(storage_config, StorageConfig):
            raise TypeError("Need a subclass of 'StorageConfig'")
        storage_config = storage_config or SQLiteConfig

        if self.exists():
            # Ignore param `storage_config`
            with open(self.config_path, "r") as stream:
                self._config = yaml_config_load(stream, SafeLoader)
                self._schema = self._get_storage_config_schema()
                self.validate()
        else:
            self._config = yaml_config_load(storage_config.config, SafeLoader)
            self._schema = storage_config.schema

        return self

    def save(self):
        if self.in_memory:
            return None

        if not os.path.isdir(self._repository):
            os.makedirs(self._repository)

        self.validate()
        with open(self.config_path, "w") as stream:
            yaml_config_dump(self._config,
                             stream,
                             Dumper=SafeDumper,
                             default_flow_style=False)

    def exists(self):
        if self.in_memory:
            return None
        return os.path.isfile(self.config_path)
