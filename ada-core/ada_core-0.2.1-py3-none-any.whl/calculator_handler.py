"""
Author: qiacai
"""

"""
API for Calculator Module
This module transform an input into a value
The input could be:
1. Calculator,
2. Transformer,
3. Value
4. TimeSeries
5. Entry
The output could be:
Value
Entry
Bool

"""

from ada_core.algorithms.calculator.all import calculators_pool
from ada_core import exceptions
from ada_core.base_handler import Handler
from ada_core.algorithms import Algorithm
from ada_core import utils


class CalculatorHandler(Handler):
    def __init__(self, handler_input, algorithm_name: str = None, algorithm_class=None, params: dict = None):

        super(CalculatorHandler, self).__init__(handler_input=handler_input, algorithm_name=algorithm_name,
                                                algorithm_class=algorithm_class, params=params)

        self._parse_params()
        self._handle()

    def _get_algorithm(self, algorithm_name):

        try:
            calculator = calculators_pool[algorithm_name]
            return calculator
        except KeyError:
            raise exceptions.AlgorithmNotFound('algorithms.calculator: ' + str(algorithm_name) + 'not found.')

    def _load_input(self, handler_input):
        if utils.isSimpleValue(handler_input):
            self.to_calculate = handler_input
        elif isinstance(handler_input, Algorithm):
            self.to_calculate = handler_input.run()
        elif isinstance(handler_input, Handler):
            self.to_calculate = handler_input.get_result()
        else:
            raise exceptions.InvalidDataFormat('calculator_handler: cannot recognize the type of handler_input')

    def _parse_params(self):

        if not self.params:
            self.params = {"to_calculate": self.to_calculate}
        else:
            self.params.update({"to_calculate": self.to_calculate})
