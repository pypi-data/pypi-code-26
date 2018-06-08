'''Some utility functions'''

import logging
from importlib.util import spec_from_file_location, module_from_spec
from os import chdir, getcwd
from os.path import normpath
from os.path import join as pjoin
from contextlib import contextmanager


def def_get(target, key, default=None):
    '''Special get function. Return default if the value is None.'''
    value = target.get(key, default)
    if value is None:
        return default
    return value


def file_read(file_name, *path, encoding="utf-8"):
    '''Just a wrapper, since nearly always only read or write are used in this script'''
    if path:
        path = path + (file_name,)
        file_name = pjoin(path[0], *path[1:])
    with open(file_name, encoding=encoding) as ffile:
        return ffile.read()


def file_write(file_name, string, *path, mode="w", encoding="utf-8"):
    '''Just a wrapper, since nearly always only read or write are used in this script'''
    if path:
        path = path + (file_name,)
        file_name = pjoin(path[0], *path[1:])
    with open(file_name, mode, encoding=encoding) as ffile:
        ffile.write(string)
    return file_name


def has_extension(ffile, extensions):
    '''Check if ffile has an extension given in extensions. Extensions can be
    a string or a list of strings.'''
    if isinstance(extensions, str):
        extensions = [extensions]
    if ffile.rpartition('.')[-1] in extensions:
        return True
    return False


def is_markdown_file(ffile):
    return has_extension(ffile, ['md', 'markdown'])


def import_script_from_file(path, name="transform_styles"):
    '''Import a script from an external file.'''
    transform = None
    try:
        import_path = normpath(path)
        spec = spec_from_file_location(name, import_path)
        transform = module_from_spec(spec)
        spec.loader.exec_module(transform)
    except FileNotFoundError:
        logging.error(f"{import_path} not found!")
    return transform


@contextmanager
def change_dir(new_dir):
    current_dir = getcwd()
    chdir(new_dir)
    yield
    chdir(current_dir)
