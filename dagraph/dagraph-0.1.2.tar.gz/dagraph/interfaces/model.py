# from .misc import _singleton
from .variables import InputVariable, OutputVariable, Constant

import importlib
import inspect
import json
import os.path

class Model():
        

    def __init__(self, name, package_name):
        self.__name__ = name
        self.input_variables = {}
        self.output_variables = {}
        self.constants = {}

        self._init_variables(package_name)
        self._generate_config()

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return id(self) == id(other)
    
    def _generate_config(self):
        filename = "model_configs/{}.cfg".format(self.__name__)

        if os.path.exists(filename):
            return

        json_dict = {"constants": {},
                     "input variables": {}}
        
        for key, var in self.constants.items():
            json_dict['constants'][key] = var.default
        
        for key, var in self.input_variables.items():
            json_dict['input variables'][key] = var.default

        with open(filename, 'w') as outfile:
            json.dump(json_dict, outfile, indent = 4, ensure_ascii = False)
        

    def load_config(self, config_path):
        fp = open(config_path, 'r')
        json_dict = json.load(fp)

        for constant_name, constant_value in json_dict['constants'].items():
            if constant_name not in self.constants.keys():
                raise Exception('Constant "{}" is not defined'.format(constant_name))
            
            self.constants[constant_name].value = constant_value

        for iv_name, iv_value in json_dict['input variables'].items():
            if iv_name not in self.input_variables.keys():
                raise Exception("Input Variable '{}' is not defined".format(iv_name))
            
            self.input_variables[iv_name].default = iv_value

    def evaluate(self):
        pass

    def _init_variables(self, name):
       self._init_inputs(name)
       self._init_outputs(name)
       self._init_constants(name)

    
    def _init_inputs(self, name):
        module =importlib.import_module('..input_variables', name)
        inputs = inspect.getmembers(module, inspect.isclass)
        for iv in filter(lambda x: x[0] !='InputVariable', inputs):
            self._add_input_variable(iv[1](self))

    def _init_outputs(self, name):
        module =importlib.import_module('..output_variables', name)
        inputs = inspect.getmembers(module, inspect.isclass)
        for iv in filter(lambda x: x[0] !='OutputVariable', inputs):
            self._add_output_variable(iv[1](self))

    def _init_constants(self, name):
        module =importlib.import_module('..constants', name)
        inputs = inspect.getmembers(module, inspect.isclass)
        for iv in filter(lambda x: x[0] !='Constant', inputs):
            self._add_constant(iv[1](self))

    def _add_input_variable(self, input_variable: InputVariable):
        if not isinstance(input_variable, InputVariable):
            raise Exception("The given argument is not of type InputVariable")
        # used because in json file variable names are specified
        self.input_variables[input_variable.__class__.__name__] = input_variable
    
    def _add_output_variable(self, output_variable: OutputVariable):
        if not isinstance(output_variable, OutputVariable):
            raise Exception("The given argument is not of type OutputVariable")
        
        self.output_variables[output_variable.__class__.__name__] = output_variable


    def _add_constant(self, constant: Constant):
        if not isinstance(constant, Constant):
            raise Exception("The given argument is not of type OutputVariable")
        
        self.constants[constant.__class__.__name__] = constant

