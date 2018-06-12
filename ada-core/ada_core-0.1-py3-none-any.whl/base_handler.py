"""
Author: qiacai
"""

"""
Base Class for Handlers
Handlers are used to call the corresponding algorithms based on the input parameters

"""

from ada_core.data.time_series import TimeSeries
from ada_core.data.entry import Entry
from ada_core import exceptions
from ada_core.algorithms import Algorithm


class Handler(object):
    def __init__(self, handler_input, algorithm_name: str = None, algorithm_class=None, params: dict = None):
        """

        :param input:
        :param algorithm_name:
        :param params:
        :return:
        """
        self.handler_input = self._load_input(handler_input)
        self.handler_output = None
        self.algorithm = algorithm_class or self._get_algorithm(algorithm_name)
        self.params = params or {}
        #self._handle()

    def _get_algorithm(self, algorithm_name):
        """
        Get the algorithm based on the algorithm_name
        :param algorithm_name:
        :return:
        """
        raise NotImplementedError

    def _load_input(self, handler_input):
        """
        The function to load the input
        :param handler_input:
        :return:
        """
        raise NotImplementedError

    def _parse_params(self):
        """
        The function to parse the config
        :param params:
        :return:
        """
        raise NotImplementedError

    def _handle(self):
        """
        Run the handler
        :return:
        """

        algorithm_obj = self.algorithm(**self.params)

        self.handler_output = algorithm_obj.run()

    def get_result(self):
        """
        Get the result
        :return:
        """

        if self.handler_output is None:
            self._parse_params()
            self._handle()

        return getattr(self, 'handler_output', None)
