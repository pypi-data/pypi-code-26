"""
Author: qiacai
"""

"""
API for Time Series Transformation Module
This module transform a time series into time series(s),
currently only consider single in and single out
"""

from ada_core.base_handler import Handler

from ada_core import exceptions
from ada_core.algorithms import Algorithm
from ada_core.algorithms.transformer.all import transformers_pool
from ada_core.data.time_series import TimeSeries


class TransformerHandler(Handler):
    def __init__(self, handler_input, algorithm_name: str = None, algorithm_class=None, params: dict = None):

        super(TransformerHandler, self).__init__(handler_input=handler_input, algorithm_name=algorithm_name,
                                                 algorithm_class=algorithm_class, params=params)

        self._parse_params()
        self._handle()

    def _get_algorithm(self, algorithm_name):

        try:
            transformer = transformers_pool[algorithm_name]
            return transformer
        except KeyError:
            raise exceptions.AlgorithmNotFound('algorithms.transformer: ' + str(algorithm_name) + 'not found.')

    def _load_input(self, handler_input):
        if isinstance(handler_input, Algorithm):
            handler_input = handler_input.run()
        if isinstance(handler_input, Handler):
            handler_input = handler_input.get_result()
        if isinstance(handler_input, TimeSeries):
            self.ori_time_series = handler_input
        else:
            raise exceptions.InvalidDataFormat('calculator_handler: cannot recognize the type of handler_input')

    def _parse_params(self):

        if not self.params:
            self.params = {"ori_time_series": self.ori_time_series}
        else:
            self.params.update({"ori_time_series": self.ori_time_series})
