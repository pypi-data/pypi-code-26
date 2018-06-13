"""
Author: qiacai
"""

from ada_core import exceptions
from ada_core.algorithms import Algorithm
from ada_core.data.time_series import TimeSeries

__all__ = ['seasonal_decompose', 'basic_transformers']


class Transformer(Algorithm):
    """
    Base class for transformers
    """

    def __init__(self, class_name, ori_time_series):
        """

        :param class_name:
        :param time_series:
        :return:
        """

        super(Transformer, self).__init__(class_name=class_name)
        self.ori_time_series = ori_time_series
        self.time_series = TimeSeries()

        if not isinstance(self.ori_time_series, TimeSeries):
            raise exceptions.ParametersNotPassed('transformer.Transformer the parameter ori_time_series is not correct')

    def _transform(self):
        """
        The transform function, need override
        :return:
        """
        raise NotImplementedError

    def _get_result(self):
        """
        Get transformed time_series
        :return: TimeSeries
        """
        return self.time_series

    def _run(self):

        self._transform()