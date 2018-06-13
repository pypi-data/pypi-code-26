"""
Author: qiacai
"""

from ada_core.algorithms import Algorithm

__all__ = ['base_ts_numeric_calculator']


class Calculator(Algorithm):
    """
    Base class for Calculator
    """

    def __init__(self, class_name, to_calculate):
        """

        :param class_name:
        :param to_calculate:
        :return:
        """
        super(Calculator, self).__init__(class_name=class_name)

        self.to_calculate = to_calculate
        self.calculated = self.to_calculate

    def _calculate(self):
        """
        The calculate function, need override
        :return:
        """
        raise NotImplementedError

    def _get_result(self):
        """
        Get decision
        :return: Bool
        """
        return self.calculated

    def _run(self):
        """
        Execute the algorithm
        :return: Bool
        """
        self._calculate()