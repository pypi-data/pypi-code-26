'''
docstring
'''

from collections import namedtuple
import logging
import os.path
import sys

_THIS = sys.modules[__name__]

AppProperties = namedtuple('AppProperties', ('name',
                                             'directories',
                                             'config_file_path',
                                             'root_logger',
                                             'init',
                                             'get_path',
                                             'get_logger'))

def _dummy(*args, **kwargs):
    pass

def _get_logger(fullmodulename):
    ''' docstring '''
    if fullmodulename == '__main__' or fullmodulename == _THIS.Properties.name:
        logname = _THIS.Properties.name
    else:
        modulename = fullmodulename.split('.')[-1]
        if not modulename: logname = _THIS.Properties.name
        else: logname = '.'.join((_THIS.Properties.name, modulename))
    return logging.getLogger(logname)

def _get_path(extension, path_given, app_name=None, app_dirs=None):
    ''' docstring '''
    if app_name is None: app_name = _THIS.Properties.name
    if app_dirs is None: app_dirs = _THIS.Properties.directories
    if extension[0] != '.': extension = '.' + extension # just in case
    if not path_given or path_given == '.': path_given = './'
    if path_given == '..': path_given = '../'
    dirname, filename = os.path.split(path_given.strip())
    if filename == '': filename = ''.join((app_name, extension)) # default name
    dirname = os.path.normpath(dirname) # not sure it is necessary
    if os.path.isabs(dirname):
        return os.path.normpath(os.path.join(dirname, filename))
    else: # dirname is relative
        paths = [os.path.normpath(os.path.join(pth, dirname, filename)) for pth in app_dirs]
        for pth in paths:
            if os.path.exists(pth): return pth
        return paths[0] # even if it will fail, return the first path in the list

def _init_properties(app_path=None, app_name=None):
    ''' docstring '''
    if not app_name:
        app_name = os.path.splitext(os.path.basename(app_path))[0] # first part of the filename, without extension
    script_dir = os.path.realpath(os.path.dirname(app_path)) # full path of directory of launching script
    current_working_dir = os.getcwd()
    # Find configuration file
    if len(sys.argv) >= 2: pathgiven = sys.argv[1].strip()
    else: pathgiven = '' # default location in case no file name or path is given
    config_file_path = _get_path('.conf', pathgiven, app_name=app_name,
                                 app_dirs=(current_working_dir, script_dir))
    config_file_dir = os.path.dirname(config_file_path)
    dirs = (config_file_dir, current_working_dir, script_dir)
    root_logger = logging.getLogger(app_name)
    _THIS.Properties = AppProperties(app_name, dirs, config_file_path, root_logger,
                                     _dummy, _get_path, _get_logger)

Properties = AppProperties('', [], '', None, _init_properties, _dummy, _dummy)
