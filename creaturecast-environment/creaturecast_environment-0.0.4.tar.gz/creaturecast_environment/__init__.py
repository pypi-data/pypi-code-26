__version__ = '0.0.4'
__description__ = 'Creaturecast Environment'
__author__ = 'Paxton Gerrish'
__email__ = 'creaturecastlabs@gmail.com'
__url__ = 'https://github.com/Paxtongerrish/creaturecast_environment.git'

import os
import json
import copy
from os.path import expanduser

server_url = 'http://creaturecast-library.herokuapp.com'

home_directory = expanduser("~").replace('\\', '/')
creaturecast_directory = '%s/creaturecast' % home_directory

if not os.path.exists(creaturecast_directory):
    os.makedirs(creaturecast_directory)


class VariablesBase(object):
    def __init__(self, name, **kwargs):
        super(VariablesBase, self).__init__()

        self.local_path = '%s/%s.json' % (
            creaturecast_directory,
            name
        )
        self.package_path = '%s/data/%s.json' % (
            os.path.dirname(__file__.replace('\\', '/')),
            name
        )

        self.variables = dict()
        if os.path.exists(self.local_path):
            with open(self.local_path, mode='r') as f:
                file_contents = f.read()
            if file_contents:
                self.variables = json.loads(file_contents)
        else:
            with open(self.package_path, mode='r') as f:
                json_string = f.read()
                self.variables = json.loads(json_string)
            with open(self.local_path, mode='w') as f:
                f.write(json_string)

    def write_to_disk(self):
        with open(self.local_path, mode='w') as f:
            json_string = json.dumps(
                self.variables,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )

            f.write(json_string)

    def __getitem__(self, item):
        return copy.copy(self.variables[item])

    def __setitem__(self, key, value):
        self.variables[key] = copy.copy(value)
        self.write_to_disk()

    def get(self, *args, **kwargs):
        return self.variables.get(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.variables.update(*args, **kwargs)
        self.write_to_disk()



class EnvironmentVariables(VariablesBase):
    def __init__(self, *args, **kwargs):
        super(EnvironmentVariables, self).__init__()
        self.variables_path = '%s/environment_variables.json' % creaturecast_directory
        self.variables = dict()
        if os.path.exists(self.variables_path):
            with open(self.variables_path, mode='r') as f:
                file_contents = f.read()
            if file_contents:
                self.variables = json.loads(file_contents)

    def write_to_disk(self):
        with open(self.variables_path, mode='w') as f:
            json_string = json.dumps(
                self.variables,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )

            f.write(json_string)

    def __getitem__(self, item):
        return copy.copy(self.variables[item])

    def __setitem__(self, key, value):
        self.variables[key] = copy.copy(value)
        self.write_to_disk()

    def get(self, *args, **kwargs):
        return self.variables.get(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.variables.update(*args, **kwargs)
        self.write_to_disk()


environment_variables = VariablesBase('environment_variables')
handle_shapes = VariablesBase('handle_shapes')
rig_settings = VariablesBase('rig_settings')