from ._session import *


__all__ = ['Session']


class Session(object):

    def __init__(self):
        self._sess = _Session()

    def load_data(self, path, sep='\t', dtype=int):
        """ Loads data.

        Note: All data elements are of the same data type.
        :param path: directory or single path or a list of paths
        :param sep: separator
        :param dtype: data type
        :return: iterable (each row of data)
        """
        self._sess.load_data(path, sep, dtype)

    def cook_data(self, cooker, spices):
        """ Cooks data.

        :param cooker: cooker name
        :param spices: single tuple or a list of tuples
        :return: iterable rows
        """
        self._sess.cook_data(cooker, spices)

    def forecast_ci(self, forecaster, fn=1, save_to=None):
        """ Forecasts confidence intervals.

        :param forecaster: name of a registered forecaster
        :param fn: number of forecasting time units
        :param save_to: saving path
        """
        self._sess.forecast_ci(forecaster, fn, save_to)

    def load_fci(self, path):
        """ Loads CIFrame objects.

        :param path: file path
        :return: List of CIFrame objects
        """
        self._sess.load_fci(path)

    def get_fci(self, row_index, alpha, forecast_index=1):
        """ Gets forecasting confidence interval.

        :param row_index: row index or row label defined by row label files.
        :param alpha: confidence level, integer in [1, 99]
        :param forecast_index: index of the forecasting time unit
        :return: confidence interval
        """
        return self._sess.get_fci(row_index, alpha, forecast_index)
