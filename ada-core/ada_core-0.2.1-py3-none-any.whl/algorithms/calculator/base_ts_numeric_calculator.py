"""
Author: qiacai
"""

"""
For this type of calculator:
input: timeseries
output: number
"""

from numbers import Number
import numpy as np

from ada_core import exceptions, utils, constants
from ada_core.algorithms.calculator import Calculator
from ada_core.data.time_series import TimeSeries


class BaseTsNumericCalculator(Calculator):
    def __init__(self, class_name, to_calculate, default=None):

        super(BaseTsNumericCalculator, self).__init__(class_name=class_name, to_calculate=to_calculate)
        self.default = default
        self._validate_input()

    def _validate_input(self):
        if not self.to_calculate or not isinstance(self.to_calculate, TimeSeries):
            raise exceptions.ParametersNotPassed
        if self.default is not None and not isinstance(self.default, Number):
            raise exceptions.ParametersNotPassed

    def _validate_output(self):
        if self.calculated is None or not isinstance(self.calculated, Number):
            raise exceptions.AlgorithmOutputFormatError

    def _get_result(self):
        """
        Get decision
        :return: Bool
        """
        self._validate_output()

        return self.calculated

    def _calculate(self):
        """
        The calculate function, need override
        :return:
        """
        raise NotImplementedError


class Mean(BaseTsNumericCalculator):
    def __init__(self, to_calculate, default=None):
        super(Mean, self).__init__(self.__class__.__name__, to_calculate=to_calculate, default=default)

    def _calculate(self):
        self.calculated = np.asscalar(np.average(self.to_calculate.getValueList())) if self.to_calculate.values() else self.default


class Median(BaseTsNumericCalculator):
    def __init__(self, to_calculate, default=None):
        super(Median, self).__init__(self.__class__.__name__, to_calculate=to_calculate, default=default)

    def _calculate(self):
        self.calculated = np.asscalar(np.median(self.to_calculate.getValueList())) if self.to_calculate.values() else self.default


class Max(BaseTsNumericCalculator):
    def __init__(self, to_calculate, default=None):
        super(Max, self).__init__(self.__class__.__name__, to_calculate=to_calculate, default=default)

    def _calculate(self):
        self.calculated = np.asscalar(np.max(self.to_calculate.getValueList())) if self.to_calculate.values() else self.default


class Min(BaseTsNumericCalculator):
    def __init__(self, to_calculate, default=None):
        super(Min, self).__init__(self.__class__.__name__, to_calculate=to_calculate, default=default)

    def _calculate(self):
        self.calculated = np.asscalar(np.min(self.to_calculate.getValueList())) if self.to_calculate.values() else self.default


class Percentile(BaseTsNumericCalculator):
    def __init__(self, to_calculate, percent=None, default=None):
        super(Percentile, self).__init__(self.__class__.__name__, to_calculate=to_calculate, default=default)

        if percent is None:
            self.percent = constants.ALGORITHM_DEFAULT_CALCULATOR_PERCENTILE_PERCENT

        if not isinstance(percent, Number):
            if utils.isfloat(percent):
                self.percent = int(float(percent))
            else:
                raise exceptions.ParametersNotPassed(
                    "calculator.Percentile, the data type of param percent is not correct")
        else:
            self.percent = int(percent)

        if self.percent > 100 or self.percent < 0:
            raise exceptions.ParametersNotPassed("calculator.Percentile, the param percent not in range")

    def _calculate(self):
        self.calculated = np.asscalar(
            np.percentile(self.to_calculate.getValueList(), self.percent)) if self.to_calculate.values() else self.default


class Std(BaseTsNumericCalculator):
    def __init__(self, to_calculate, default=None):
        super(Std, self).__init__(self.__class__.__name__, to_calculate=to_calculate, default=default)

    def _calculate(self):
        self.calculated = np.asscalar(np.std(self.to_calculate.getValueList())) if self.to_calculate.values() else self.default


class Mad(BaseTsNumericCalculator):
    def __init__(self, to_calculate, default=None):
        super(Mad, self).__init__(self.__class__.__name__, to_calculate=to_calculate, default=default)

    def _calculate(self):
        if self.to_calculate.values():
            median_value = np.asscalar(np.median(self.to_calculate.getValueList()))
            median_diff_list = [np.asscalar(np.abs(x - median_value)) for x in self.to_calculate.getValueList()]
            self.calculated = np.asscalar(np.median(median_diff_list))
        else:
            self.calculated = self.default


class Count(BaseTsNumericCalculator):
    def __init__(self, to_calculate, default=None):
        super(Count, self).__init__(self.__class__.__name__, to_calculate=to_calculate, default=default)

    def _calculate(self):
        self.calculated = len(self.to_calculate.getValueList()) if self.to_calculate.values() else self.default


class Sum(BaseTsNumericCalculator):
    def __init__(self, to_calculate, default=None):
        super(Sum, self).__init__(self.__class__.__name__, to_calculate=to_calculate, default=default)

    def _calculate(self):
        self.calculated = np.asscalar(np.sum(self.to_calculate.getValueList())) if self.to_calculate.values() else self.default
