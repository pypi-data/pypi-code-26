"""
Author: qiacai
"""

import math
from numbers import Number
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

from ada_core import constants, utils, exceptions
from ada_core.algorithms.transformer import Transformer
from ada_core.data.time_series import TimeSeries


class SeasonalDecompose(Transformer):

    def __init__(self, ori_time_series, freq=None, trend_only=None, is_fillna=None):
        """
        Initializer

        :return:
        """

        super(SeasonalDecompose, self).__init__(self.__class__.__name__, ori_time_series=ori_time_series)

        if freq is None:
            self.freq = constants.ALGORITHM_DEFAULT_TRANSFORMER_SEASONAL_DECOMPOSE_FREQ

        if not isinstance(freq, Number):
            if utils.isfloat(freq):
                self.freq = int(float(freq))
            else:
                raise exceptions.ParametersNotPassed(
                    "transformer.SeasonalDecompose, the data type of param freq is not correct")
        else:
            self.freq = int(freq)

        if self.freq <= 0:
            raise exceptions.ParametersNotPassed(
                "transformer.SeasonalDecompose, the param freq not in range")

        if len(self.ori_time_series) <= self.freq:
            raise exceptions.ParametersNotPassed('ada.algorithms.transformer.seasonal_decompose: '
                                                   'the lengh of the original time series is less than one period')

        if trend_only is None:
            self.trend_only = constants.ALGORITHM_DEFAULT_TRANSFORMER_SEASONAL_DECOMPOSE_TREND_ONLY

        if not utils.isbool(trend_only):
                raise exceptions.ParametersNotPassed(
                    "transformer.SeasonalDecompose, the data type of param trend_only is not correct")
        else:
            self.trend_only = utils.str2bool(trend_only)

        if is_fillna is None:
            self.is_fillna = constants.ALGORITHM_DEFAULT_TRANSFORMER_SEASONAL_DECOMPOSE_FILLNA

        if not utils.isbool(is_fillna):
                raise exceptions.ParametersNotPassed(
                    "transformer.SeasonalDecompose, the data type of param is_fillna is not correct")
        else:
            self.is_fillna = utils.str2bool(is_fillna)

    def _transform(self):

        valueList = self.ori_time_series.getValueList()
        valueList = [valueList.median() if math.isnan(value) else value for value in valueList]
        results = seasonal_decompose(valueList, freq=self.freq, two_sided=False, model='additive')

        if self.trend_only:
            time_series = results.trend
        else:
            time_series = results.trend + results.resid

        time_series = pd.Series(time_series, self.ori_time_series.getKeyList())

        if self.is_fillna:
            time_series = time_series.fillna(method='bfill')
        else:
            time_series = time_series[self.freq:]

        self.time_series = TimeSeries(dict(time_series.to_dict()))