"""
Author: qiacai
"""
from numbers import Number
import numpy as np

from ada_core import constants, utils, exceptions
from ada_core.algorithms.transformer import Transformer
from ada_core.data.time_series import TimeSeries


class ValueOffset(Transformer):
    def __init__(self, ori_time_series, offset_value=None):
        super(ValueOffset, self).__init__(self.__class__.__name__, ori_time_series=ori_time_series)

        if offset_value is None:
            self.offsetValue = constants.ALGORITHM_DEFAULT_TRANSFORMER_OFFSET_VALUE

        if not isinstance(offset_value, Number):
            if utils.isfloat(offset_value):
                self.offsetValue = float(offset_value)
            else:
                raise exceptions.ParametersNotPassed(
                    "transformer.ValueOffset, the data type of param offset_value is not correct")
        else:
            self.offsetValue = float(offset_value)

    def _transform(self):

        for timestamp, value in self.ori_time_series.items():
            self.time_series.update({timestamp: (value + self.offsetValue)})


class TimeOffset(Transformer):
    def __init__(self, ori_time_series, offset_time=None):
        super(TimeOffset, self).__init__(self.__class__.__name__, ori_time_series=ori_time_series)

        if offset_time is None:
            self.offsetTime = constants.ALGORITHM_DEFAULT_TRANSFORMER_OFFSET_TIME

        if not isinstance(offset_time, Number):
            if utils.isfloat(offset_time):
                self.offsetTime = int(float(offset_time))
            else:
                raise exceptions.ParametersNotPassed(
                    "transformer.ValueOffset, the data type of param offset_value is not correct")
        else:
            self.offsetTime = int(offset_time)

    def _transform(self):

        self.time_series = TimeSeries()
        for timestamp, value in self.ori_time_series.items():
            self.time_series.update({timestamp + self.offsetTime: value})


class StandardNormalization(Transformer):
    def __init__(self, ori_time_series):
        super(StandardNormalization, self).__init__(self.__class__.__name__, ori_time_series=ori_time_series)

    def _transform(self):
        mean = np.asscalar(np.average(self.ori_time_series.values()))
        std = np.asscalar(np.std(self.ori_time_series.values()))
        self.time_series = TimeSeries()
        for timestamp, value in self.ori_time_series.items():
            if std <= 0:
                self.time_series.update({timestamp: value})
            else:
                self.time_series.update({timestamp: (value - mean) / std})


class ScaleNormalization(Transformer):
    def __init__(self, ori_time_series):
        super(ScaleNormalization, self).__init__(self.__class__.__name__, ori_time_series=ori_time_series)

    def _transform(self):

        max = np.asscalar(np.max(self.ori_time_series.values()))
        min = np.asscalar(np.min(self.ori_time_series.values()))
        self.time_series = TimeSeries()
        for timestamp, value in self.ori_time_series.items():
            if max <= min:
                self.time_series.update({timestamp: value})
            else:
                self.time_series.update({timestamp: (value - min) / (max - min)})


class ExponentialSmooth(Transformer):
    """
    return a new time series which is a exponential smoothed version of the original data series.
    soomth forward once, backward once, and then take the average.

    :param float smoothing_factor: smoothing factor
    :return: :class:`TimeSeries` object.
    """

    def __init__(self, ori_time_series, smoothing_factor=None):
        super(ExponentialSmooth, self).__init__(self.__class__.__name__, ori_time_series=ori_time_series)

        if smoothing_factor is None:
            self.smoothFactor = constants.ALGORITHM_DEFAULT_TRANSFORMER_OFFSET_TIME

        if not isinstance(smoothing_factor, Number):
            if utils.isfloat(smoothing_factor):
                self.smoothFactor = float(smoothing_factor)
            else:
                raise exceptions.ParametersNotPassed(
                    "transformer.ExponentialSmooth, the data type of param smoothing_factor is not correct")
        else:
            self.smoothFactor = float(smoothing_factor)

        if self.smoothFactor > 1 or self.smoothFactor < 0:
            raise exceptions.ParametersNotPassed(
                "transformer.ExponentialSmooth, the param smoothing_factor not in range")

    def _transform(self):

        forward_smooth = {}
        backward_smooth = {}
        output = {}

        pre_entry = self.ori_time_series.getValueList()[0]
        next_entry = self.ori_time_series.getValueList()[-1]

        for key, value in self.ori_time_series.items():
            forward_smooth[key] = self.smoothFactor * pre_entry + (1 - self.smoothFactor) * value
            pre_entry = forward_smooth[key]
        for key, value in self.ori_time_series.items():
            backward_smooth[key] = self.smoothFactor * next_entry + (1 - self.smoothFactor) * value
            next_entry = backward_smooth[key]
        for key in forward_smooth.keys():
            output[key] = (forward_smooth[key] + backward_smooth[key]) / 2
        self.time_series = TimeSeries(output)
