import numpy as np
import scipy.stats as ss
import pickle
from pathlib import Path


__all__ = ['ForecastCI']


class ForecastCI(object):

    def __init__(self):
        self.hist_data = None
        self.fn = 1
        self.fore_conf_ints = None  # forecasting confidence intervals

    def config(self, hist_data, fn=1):
        """ Configurations.

        :param hist_data: 1d list or numpy array
        :param fn: the number of forecasting time intervals
        """
        self.hist_data = np.array(hist_data)
        if isinstance(fn, int):
            self.fn = fn
        else:
            raise ValueError('future is either integer or iterable!')

    def run(self, save_to=None):
        self.fore_conf_ints = []
        for fi in range(1, self.fn + 1):
            conf_ints = [fci_normal(self.hist_data, alpha / 100, fi) for alpha in range(1, 100)]
            self.fore_conf_ints.append(conf_ints)
        # save result
        if save_to:
            with open(save_to, 'wb') as f:
                pack = {
                    'fn': self.fn,
                    'fci': self.fore_conf_ints
                }
                pickle.dump(pack, f)

    def load_fci(self, path):
        if not Path(path).exists():
            raise FileNotFoundError('File does not exist! path = ', path)
        with open(path, 'rb') as f:
            pack = pickle.load(f)
            self.fn = pack['fn']
            self.fore_conf_ints = pack['fci']

    def get_fci(self, alpha, fi=None):
        """ Gets forecasting confidence interval.

        :param alpha: percentage confidence level, integer in [1, ..., 99]
        :param fi: of the fi -th time interval, 1 <= fi <= fn (default value is 1)
        :return: interval (tuple of length two)
        """
        if not fi:
            fi = 1
        assert isinstance(alpha, int) and 1 <= alpha <= 99, 'alpha must be integer in [1, 99]!'
        assert isinstance(fi, int) and 1 <= fi <= self.fn, 'fi must be integer in [1, fn]!'
        if not self.fore_conf_ints:
            raise ValueError('No forecast data!')

        return self.fore_conf_ints[fi-1][alpha-1]


def fci_normal(data, p, fi):
    """ Forecasting confidence interval under Normal distribution.

    :param data: 1d array or list
    :param p: confidence, in (0, 1)
    :param fi: of the fi -th time interval, 1 <= fi <= fn (default value is 1)
    :return: interval (tuple of length two)
    """

    x = np.array(range(len(data)))
    # linear regression
    slope, intercept, r_value, p_value, std_err = ss.linregress(x, data)
    # forecast
    mean = slope * (len(x) + fi - 1) + intercept
    return ss.norm.interval(p, mean, std_err)
