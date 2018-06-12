"""
Author: qiacai
"""

"""
API for Time Series Judger Module
This module transform an input into a True/False Decision
The input could be Timeseries, Entry, Handlers, Algorithm
The output is a True/False Judgement
"""

from ada_core.algorithms import Algorithm
from ada_core.base_handler import Handler
from ada_core import utils, exceptions
from ada_core.algorithms.judger.all import judgers_pool


class JudgerHandler(Handler):
    def __init__(self, handler_input, comparator=None, algorithm_name: str = None, algorithm_class=None,
                 params: dict = None):

        super(JudgerHandler, self).__init__(handler_input=handler_input, algorithm_name=algorithm_name,
                                            algorithm_class=algorithm_class, params=params)

        if comparator is not None:
            self._load_comparator(comparator)
        self._parse_params()
        self._handle()

    def _get_algorithm(self, algorithm_name):

        try:
            judger = judgers_pool[algorithm_name]
            return judger
        except KeyError:
            raise exceptions.AlgorithmNotFound('algorithms.judger: ' + str(algorithm_name) + 'not found.')

    def _load_input(self, handler_input):
        if utils.isSimpleValue(handler_input):
            self.to_judge = handler_input
        elif isinstance(handler_input, Algorithm):
            self.to_judge = handler_input.run()
        elif isinstance(handler_input, Handler):
            self.to_judge = handler_input.get_result()
        else:
            raise exceptions.InvalidDataFormat('judger_handler: cannot recognize the type of handler_input')

    @staticmethod
    def _load_comparator_single(comparator):
        """
        The function to load the input
        :param handler_input:
        :return:
        """
        if utils.isSimpleValue(comparator):
            return comparator
        elif isinstance(comparator, Algorithm):
            return comparator.run()
        elif isinstance(comparator, Handler):
            return comparator.get_result()
        else:
            raise exceptions.InvalidDataFormat('judger_handler: cannot recognize the type of comparator')

    def _load_comparator(self, comparator):

        if isinstance(comparator, list):
            self.comparator = [JudgerHandler._load_comparator_single(com) for com in comparator]
        else:
            self.comparator = JudgerHandler._load_comparator_single(comparator)

    def _parse_params(self):
        if self.comparator is not None:
            if not self.params:
                self.params = {"comparator": self.comparator}
            else:
                self.params.update({"comparator": self.comparator})
        if not self.params:
            self.params = {"to_judge": self.to_judge}
        else:
            self.params.update({"to_judge": self.to_judge})