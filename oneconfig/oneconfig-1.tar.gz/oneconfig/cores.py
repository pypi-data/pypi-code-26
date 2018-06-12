import json
import sys
import os

import yaml

import logging

from oneconfig import modes

logger = logging.getLogger('envs')
logger.setLevel(logging.DEBUG)


class ConfigLoader(object):
    def __init__(self):
        self.configs = {}
        self.config_hash = None

    def load(self):
        return self.configs


def json_file_config_load_handler(path):
    return json.load(open(path))


def yaml_file_config_load_handler(path):
    return yaml.load(open(path))


class FileConfigLoader(ConfigLoader):
    __config_file_loaders__ = {
        '.json': json_file_config_load_handler,
        '.yaml': yaml_file_config_load_handler,
        '.yml': yaml_file_config_load_handler
    }

    def __init__(self, filename, loaders=None):
        self.filename = filename

        if loaders is not None:
            self.__config_file_loaders__.update(loaders)

    def load(self):
        ext = '.{}'.format(self.filename.split('.')[-1])
        handler = self.__config_file_loaders__[ext]
        self.configs = handler(self.filename)
        return self.configs


class CommandLineConfigLoader(ConfigLoader):
    def load(self):

        for i in range(len(sys.argv)):
            item = sys.argv[i]
            if item.startswith('--'):
                if item.find('=') <= -1:
                    self.configs[item[2:]] = True
                else:
                    item_arr = item.split('=')
                    key = item_arr[0][2:]
                    val = item_arr[1]
                    if isinstance(val, str) and val in ['False', 'True']:
                        val = True if val == 'True' else False
                    self.configs[key] = val
            else:
                pass
        return self.configs


def get_config_by_path_value(path, value, mapping=None):
    if isinstance(path, str):
        path = path.split('.')

    if mapping is None:
        mapping = dict()

    if len(path) > 1:
        m = dict()

        get_config_by_path_value(path[1:], value, m)

        mapping[path[0]] = m
    else:
        mapping[path[0]] = value
    return mapping


def get_config_mode_by_filename(filename):
    parts = filename.split('.')
    for item in parts:
        if item in dir(modes):
            return item
    return modes.Default


class Configuration(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Configuration, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

        self.loader_entities = []

        self.config_files = []

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def option(self, key, obj):
        values = self.get(key, dict())
        obj.update(values)
        return obj

    @property
    def mode(self):
        return self.get('mode', modes.Development)

    def add_file_by_prefix(self, filename_prefix, follow_mode=True):
        paths = os.path.split(filename_prefix)
        d, filename = os.path.join('.' if paths[0] == '' else paths[0]), paths[-1]
        files = os.listdir(d)
        config_files = [x for x in files if x.startswith(filename_prefix)]

        if follow_mode:
            config_files = [x for x in config_files if get_config_mode_by_filename(x) == self.mode]

        config_fs = []
        for item in config_files:
            if item.startswith('./'):
                config_fs.append(item[1:])
            else:
                config_fs.append(item)

        config_files = list(set(config_fs))

        for item in config_files:
            self.add_file_by_name(os.path.join(d, item))
        self.config_files = config_files
        return self

    def add_file_by_name(self, filename):
        loader = FileConfigLoader(filename)
        self.config_files.append(filename)
        self.update(loader.load())
        self.loader_entities.append(loader)
        return self

    def add_by_env_mode(self, mode=None, dir_path='.'):
        if mode is None:
            mode = self.mode

        files = os.listdir(dir_path)
        files = [x for x in files if os.path.splitext(x)[1] in FileConfigLoader.__config_file_loaders__.keys()]
        files = [x for x in files if get_config_mode_by_filename(x) == mode]

        self.config_files.extend(files)
        self.config_files = list(set(self.config_files))

        for item in files:
            self.add_file_by_name(os.path.join(dir_path, item))
        return self

    def set(self, path, value):
        m = get_config_by_path_value(path, value)
        self.update(m)
        return self

    def mappings(self):
        return dict(self.items())
