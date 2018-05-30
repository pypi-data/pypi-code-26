import importlib
import inspect
import logging
import os
import sys
from pydoc import help

logging.basicConfig(format='(%(asctime)s %(levelname)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


class CommandLineInterface(object):
    def __init__(self, modules_dir, modules_parent_path, debug):
        LOG_LEVEL = 20 if not debug else 10
        logger.setLevel(LOG_LEVEL)
        self.logger = logger
        self.modules_dir = modules_dir
        self.modules_parent_path = modules_parent_path

    def _list_available_arguments(self, module):
        # Get module's path, list dirs and filter out ones starting with __, remove .py from the accepted rest
        ignored_arguments = []
        ignorefile_path = f'{module.__path__[0]}/.appsetignore'
        try:
            with open(ignorefile_path) as f:
                for line in f.readlines():
                    if line:
                        ignored_arguments.append(line.rstrip())
        except FileNotFoundError:
            logger.debug(f'{ignorefile_path} not found')
        available_arguments = list(
            map(lambda y: y.replace('.py', ''),
                filter(lambda x: not x.startswith('__') and x != '.appsetignore' and x not in ignored_arguments,
                       os.listdir(module.__path__[0]))))
        available_arguments.sort()
        self.logger.info(available_arguments)
        sys.exit(0)

    def _parse_params(self, params):
        kwargs = {}
        for param in params:
            key, value = param.split('=')
            kwargs[key] = value
        return kwargs

    def _validate_function_args(self, function, params):
        try:
            passed_args = sorted(list(params.keys()))
        except AttributeError:
            passed_args = []
        nl = '\n'
        self.logger.debug(f'Delivered arguments: \n{nl.join(passed_args)}')
        # Check function's expected arguments
        function_inspect = inspect.getfullargspec(function)
        args, defaults = function_inspect.args, function_inspect.defaults
        # Divide funtion's arguments into required and optionals
        args_len, defaults_len = len(args) if args else 0, len(defaults) if defaults else 0
        required, optionals = args[:args_len - defaults_len], args[args_len - defaults_len:]
        self.logger.debug(f'Expected required arguments:\n{nl.join(required)}\n'
                          f'Expected optional arguments: \n{nl.join(optionals)}')
        # Return True only if all required keys were delivered and all of delivered keys are expected by function
        return True if all(key in passed_args for key in required) and all(
            key in args for key in passed_args) else False

    def run_command(self, command, params=[], run_help=False):
        self.logger.debug(f'Command arguments are: {command}')
        # If params were passed, parse them to dictionary
        if params:
            params = self._parse_params(params)
            self.logger.debug(f'Params are: {params}')
        # Import modules package first
        spec = importlib.util.spec_from_file_location(self.modules_dir,
                                                      self.modules_parent_path + self.modules_dir + '/__init__.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        current_module = importlib.import_module(self.modules_dir)
        self.logger.debug(f'Imported {current_module}')
        visited_path = ""
        # Go through command nested arguments like a tree
        for i, argument in enumerate(command):
            self.logger.debug(f'Importing {current_module.__name__}.{argument}')
            try:
                # Import current command's slice from previously imported package within this loop
                current_module = importlib.import_module(current_module.__name__ + '.' + argument)
                visited_path += f"{argument}"
                # If current command's slice is the last one and help is True, return docstring of this package
                if i + 1 == len(command) and run_help:
                    help(current_module)
                    sys.exit(0)
            except ModuleNotFoundError:
                # Enter when there's no such package to be imported during the loop
                self.logger.debug(f'Module {current_module.__name__}.{argument} not found')
                # If it's the last command's slice, check if it wasn't a built-in function
                if i + 1 == len(command):
                    self.logger.debug(f'{argument} was the last argument of the command')
                    if argument == 'list':
                        self._list_available_arguments(current_module)
                self.logger.error(f'Could not find `{argument}` in command `{" ".join(command)}`')
                sys.exit(1)
        try:
            self.logger.debug(f'Executing run() for command {current_module}')
            # Validate delivered params against required and optionals of the desired function
            if not self._validate_function_args(current_module.run, params):
                self.logger.debug(f'Arguments validation failed.')
                self.logger.error('Some parameters are missing or not expected by the function.')
                sys.exit(1)
            self.logger.debug(f'Arguments validated successfully')
            self.logger.debug(f'Executing {" ".join(command)}')
            return current_module.run(**params) if params else current_module.run()
        except AttributeError:
            # Enter when there's no expected run() function inside the found package, usually a developer's mistake
            self.logger.debug(f'{current_module.__name__} has no run() function, returning available arguments')
            self.logger.info(f'{current_module.__name__} can\'t be run directly, available ways to go are:')
            self.logger.info(f'{self._list_available_arguments(current_module)}')
