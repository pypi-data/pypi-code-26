from .interfaces.model import Model
from .interfaces.optimizer import Optimizer
from .interfaces.variables import InputVariable, OutputVariable
import sys
import os.path
import json
import collections


class Design(object):

    def __init__(self):

        self._models = {}
        self._models_ordered = []
        self._validated = False
        self._free_variables = collections.defaultdict(list)
        self._input_variables = {}
        self._output_variables = {}
        self._IO_relationships = {}

        self._config_fp = None
        
        self._optimizer = None
        self._objective_function = None
        self._constraints = {'equality': [],
                             'inequality': []}
        
        self.lastx = []
        

        pass

    def add_model(self, model: Model):

        if not isinstance(model, Model):
            raise TypeError("The registered model must be an instance of Model.")
        
        if model in self._models:
            raise Exception("Duplicate model in tree")

        if model.__name__ is ('free'):
            raise Exception("Name 'free' for model not allowed")

        self._models[model.__name__] = model
        self._input_variables[model.__name__] = (model.input_variables)
        self._output_variables[model.__name__] = (model.output_variables)

    
    def add_constraint(self, constraint, equality=True):
            evaluate_func = self.__generate_evaluation_formula()
            
            def cons(x):
                evaluate_func(x)
                return (constraint(**self._models))

            cons.name = constraint.__name__

            if equality:
                self._constraints['equality'].append(cons)
            else:
                self._constraints['inequality'].append(cons)

    def set_objective_function(self, function):
        if not callable(function):
            raise Exception("The supplied argument is not a function.")
        
        self._objective_function = function

    def set_optimizer(self, optimizer: Optimizer):
        if not isinstance(optimizer, Optimizer):
             raise TypeError("The given optimizer must be an instance of Optimizer")
        
        self._optimizer = optimizer

    def set_config(self, path: str):
        self._config_fp = open(path, 'r')

    def validate(self):
        filename = '_'.join([name for name, _ in self._models.items()]) + '.cfg'
        
        try:
            if self._config_fp == None:
                fp = open(filename, 'r')
            else:
                fp = self._config_fp
            
            self._read_config(fp)
            
        except IOError:
            self._generate_config(filename)
            print('No config file found. Automatically generated as {}'.format(filename))
            sys.exit(1)

        self._get_model_order()
        self._validated = True

    def _validate_minimize(self):
        if self._objective_function is None:
            raise Exception("No objective function set.")
        
        if len(self._constraints) is 0:
            print("WARNING: No constraints set")

        if self._optimizer is None:
            raise Exception("No optimizer set.")

    def evaluate(self, values):
        if not self._validated:
            raise Exception('Configuration not validated yet. Call .validate() first.')

        func = self.__generate_evaluation_formula()
        
        for index, var_list in self._free_variables.items():
            for var in var_list:
                var.value = values[index]

        # print(func(values))
        func(values)
        
    def minimize(self):
        self._validate_minimize()

        #TODO: Check if defaults invalidate constraints
        x0 = [0]*len(self._free_variables)
        for index, var_list in self._free_variables.items():
            x0[index] = var_list[0].default

        for constraint_type, func_list in self._constraints.items():
            if constraint_type == 'inequality':
                for func in func_list:
                    if func(x0) < 0:
                        raise Exception("Default value for constraint {} out of bounds".format(func.name))
            elif constraint_type == 'equality':
                for func in func_list:
                    if func(x0) != 0:
                        raise Exception("Default value for constraint {} out of bounds".format(func.name))
        
        cost_func = self._generate_minimization_formula()

        self._optimizer.run(x0, cost_func, self._constraints)


    def summary(self):
        for model_name, model in self._models.items():
            print(model_name)
            
            print('\t Inputs')
            for iv_name, iv in model.input_variables.items():
                print('\t\t {}: {}'.format(iv_name, iv.value))

            print('\t Outputs')
            for ov_name, ov in model.output_variables.items():
                print('\t\t {}: {}'.format(ov_name, ov.value))
                    


    def tree(self):
        if not self._validated:
            raise Exception('Configuration not validated yet. Call .validate() first.')
        
        print(" --> ".join([m.__name__ for m in self._models_ordered]))

        for model_name, iv_dict in self._input_variables.items():
            print(model_name)
            for variable_name, iv in iv_dict.items():
                print("\t{}: {}".format(variable_name, iv()))


    def _generate_config(self, filename):
        #TODO: Add functionality for multiple vars of same class
        model_names = [name for name, _ in self._models.items()]
        input_variable_names = [ [ iv.__class__.__name__ for _, iv in model.input_variables.items() ] for _, model in self._models.items()]
        #output_variable_names = [ [ ov.__class__.__name__ for _, ov in model.output_variables.items() ] for model in self._models]

        json_dict = {'model relationship dependencies': {}}

        for i, model_input_variable_name in enumerate(input_variable_names):
            json_dict['model relationship dependencies'][model_names[i]] = {}
            for input_variable in model_input_variable_name:
                json_dict['model relationship dependencies'][model_names[i]][input_variable] = None
        

        with open(filename, 'w') as outfile:
            json.dump(json_dict, outfile, indent = 4, ensure_ascii = False)

    def _read_config(self, fp):
        json_dict = json.load(fp)
        if ('model relationship dependencies') not in json_dict.keys():
            raise Exception("Invalid config file given")

        model_names = [name for name, _ in self._models.items()]
        
        for model_name, input_variable_dict in json_dict['model relationship dependencies'].items():
            if model_name not in model_names:
                raise Exception("Specified input_variable model '{}' does not match loaded models : [{}]".format(model_name, model_names))
            
            input_model_instance = self._models[model_name]

            for input_variable_name, output_variable in input_variable_dict.items():

                if input_variable_name not in input_model_instance.input_variables.keys():
                    raise Exception("Input variable: {} does not exist in model: {}".format(input_variable_name, model_name))

                iv_instance = input_model_instance.input_variables[input_variable_name]
                
                if output_variable == None:
                    raise Exception()
                elif output_variable.split('.')[0] == "free":
                    index = int(output_variable.split('.')[1])
                    self._free_variables[index].append(iv_instance)
                    continue

                output_module_name, output_variable_name = output_variable.split('.')

                if model_name not in model_names:
                    raise Exception("Specified input_variable model '{}' does not match loaded models : [{}]".format(output_module_name, model_names))

                output_model_instance = self._models[output_module_name]

                if output_variable_name not in output_model_instance.output_variables.keys():
                    raise Exception("Output variable: {} does not exist in model: {}".format(output_variable_name, output_module_name))

                ov_instance = output_model_instance.output_variables[output_variable_name]

                self._IO_relationships[iv_instance] = ov_instance

    def _get_model_order(self):
        visited = []
        stack = []
        
        def DFS(node):
            visited.append(node)
            neighbors = []
            for iv, ov in self._IO_relationships.items():
                if ov.model == node:
                    neighbors.append(iv.model)
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    DFS(neighbor)

            stack.insert(0, node)
        
        for _, node in self._models.items():
            if node not in visited:
                DFS(node)
        
        self._models_ordered = stack
            

    def __generate_evaluation_formula(self):
        def evaluation_function(x):
            x = list(x)
            if x != self.lastx:
                self.lastx = x
                for index, var_list in self._free_variables.items():
                    for var in var_list:
                        var.value = x[index]

                for model in self._models_ordered:
                    model.evaluate()

                    for iv, ov in self._IO_relationships.items():
                        if ov.model is model:
                            iv.value = ov.value

                
        
        return evaluation_function
        



    def _generate_minimization_formula(self):
        evaluate_func = self.__generate_evaluation_formula()
    
        def minimization_function(x):
            # print("ccpunction value", self._objective_function(**self._models))

            evaluate_func(x)
            return self._objective_function(**self._models)

        return minimization_function    




        


    

