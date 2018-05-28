from .data import *
from .fci import *
import pickle
from .logger import *
from pathlib import Path


__all__ = ['_Session']


class _Session(object):

    def __init__(self):
        self.hist_data = None
        self.ready_data = None
        self.row_labels = {}
        self.ci_frames = []

    @property
    def fn(self):
        """ Counts the number of forecasting time units.
        """
        if self.ci_frames:
            return len(self.ci_frames[0])
        return 1

    def load_data(self, path, sep='\t', dtype=int):
        """ Loads data.

        Note: All data elements are of the same data type.
        :param path: directory or single path or a list of paths
        :param sep: separator
        :param dtype: data type
        :return: iterable (each row of data)
        """
        self.hist_data = read_data(path, sep, dtype)
        if has_row_labels(path):
            i = 0
            for rl in read_row_labels(path):
                self.row_labels[rl] = i
                i += 1

    def cook_data(self, cooker, spices):
        """ Cooks data.

        :param cooker: cooker name
        :param spices: single tuple or a list of tuples
        :return: iterable rows
        """
        self.ready_data = cook_data(self.hist_data, cooker, spices)

    def forecast_ci(self, forecaster, fn=1, save_to=None):
        """ Forecasts confidence intervals.

        :param forecaster: name of a registered forecaster
        :param fn: number of forecasting time units
        :param save_to: saving path
        """
        for ci_frame in forecast_ci(self.ready_data, forecaster, fn):
            self.ci_frames.append(ci_frame)

        if save_to:
            self._save_fci(save_to)

    def _save_fci(self, path):
        if not self.ci_frames:
            raise ValueError('No ci frames!')
        pack = {
            'rl': self.row_labels,
            'cif': self.ci_frames
        }
        with open(path, 'wb') as f:
            pickle.dump(pack, f)
        logger.info("Forecasting results saved. save_to = '%s'" % path)

    def load_fci(self, path):
        """ Loads CIFrame objects.

        :param path: file path
        :return: List of CIFrame objects
        """
        if not Path(path).exists():
            raise FileNotFoundError('File not found! path = ', path)

        with open(path, 'rb') as f:
            pack = pickle.load(f)
            self.row_labels = pack['rl']
            self.ci_frames = pack['cif']

        logger.info("Forecasting results loaded. path = '%s'" % path)

    def get_fci(self, row_index, alpha, forecast_index=1):
        if not (isinstance(alpha, int) and 1 <= alpha <= 99):
            raise ValueError('Significance level alpha should be integer in [1, 99]!')
        if not (isinstance(forecast_index, int) and 1 <= forecast_index <= self.fn):
            raise ValueError('Forecast index is integer in [1, %d]!' % self.fn)

        if isinstance(row_index, int):
            assert row_index > 0, 'Row index starts from one!'
            return self.ci_frames[row_index-1].get(alpha, forecast_index)
        elif isinstance(row_index, str):
            assert self.row_labels, 'Row labels are empty!'
            if row_index not in self.row_labels.keys():
                raise ValueError('Row index is not correct!')
            ind = self.row_labels[row_index]
            return self.ci_frames[ind].get(alpha, forecast_index)
        else:
            raise ValueError('Row index has wrong format!')
