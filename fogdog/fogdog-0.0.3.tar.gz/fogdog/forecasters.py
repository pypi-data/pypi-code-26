import numpy as np
import scipy.stats as ss


__all__ = ['forecaster', 'CIFrame']


# --------------------------------
# Decorator
# For registering forecasters
# --------------------------------
class Forecaster(object):

    def __init__(self):
        self._forecasters = {}

    def __call__(self, name):
        def wrapper(func):
            self._forecasters[name] = func
            return func
        return wrapper

    def getattr(self, name):
        if name in self._forecasters.keys():
            return self._forecasters[name]
        else:
            raise ValueError('Forecaster is not registered! name = %s' % name)


forecaster = Forecaster()
# --------------------------------


class CIFrame(object):
    """ Data structure: Frame of Confidence Intervals.
    """

    def __init__(self):
        self._cif = []

    def __len__(self):
        return len(self._cif)

    def __repr__(self):
        return str(self._cif)

    def is_empty(self):
        return True if not self._cif else False

    def get(self, alpha, forecast_index=1):
        """ Gets confidence interval.

        :param alpha: confidence level, integer in [1, 99]
        :param forecast_index: integer, indicating which forecasting time unit
        :return: confidence interval (tuple of length 2)
        """
        if not isinstance(alpha, int) or not 1 <= alpha <= 99:
            raise ValueError("alpha must be integer in [1, 99]!")
        if not isinstance(forecast_index, int) or not 1 <= forecast_index <= len(self._cif):
            raise ValueError("forecast_index must be integer in [1, %d]!" % len(self._cif))
        return self._cif[forecast_index - 1][alpha - 1]

    @staticmethod
    def _check_ci_slice(ci_slice):
        if not isinstance(ci_slice, list):
            return False
        if not isinstance(ci_slice[0], tuple):
            return False
        i = 0
        for ci in ci_slice:
            i += 1
            if not len(ci) == 2:
                return False
        if i != 99:
            return False
        return True

    def put(self, ci_slice):
        """ Puts confidence interval slice into data structure.

        :param ci_slice: list, satisfying len(ci_slide) = 99.
        """
        if not self._check_ci_slice(ci_slice):
            raise ValueError("'ci_slice' is wrong format!")
        self._cif.append(ci_slice)


# --------------------------------
# Registered forecasters.
# --------------------------------


@forecaster('LR')
def lr(row, fn=1):
    """ Forecasting confidence interval under Normal distribution.

    :param row: 1d array or list
    :param fn: the number of forecasting time units
    :return: CIFrame object
    """

    x = np.array(range(len(row)))
    # linear regression
    slope, intercept, r_value, p_value, std_err = ss.linregress(x, row)
    # forecast
    cif = CIFrame()
    for i in range(fn):
        mean = slope * (len(x) + fn) + intercept
        ci_slice = [ss.norm.interval(alpha/100, mean, std_err) for alpha in range(1, 100)]
        cif.put(ci_slice)
    return cif

