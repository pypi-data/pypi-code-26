from .data import *
from .fci import *
import pickle
from pathlib import Path


__all__ = ['Session']


class Session(object):

    def __init__(self):
        self.hist_data = None
        self.cooker = cooker_move_sum
        self.spices = None
        self.fci = ForecastCI()
        self.fore_conf_intss = None

    def load_data(self, path, sep='\t'):
        self.hist_data = load_data(path, sep)

    def set_cooker(self, cooker):
        self.cooker = cooker

    def set_spices(self, spices):
        self.spices = spices

    def cook_hist_data(self):
        params = {
            'cooker': self.cooker,
            'spices': self.spices
        }
        for row in cook_data(self.hist_data, params):
            yield row

    def config_fci(self, fn):
        self.fci.fn = fn

    def run_fci(self, save_to):
        self.fore_conf_intss = []
        for row in self.cook_hist_data():
            self.fci.config(row)
            self.fci.run()
            self.fore_conf_intss.append(self.fci.fore_conf_ints)
        # save result
        if save_to:
            with open(save_to, 'wb') as f:
                pack = {
                    'fn': self.fci.fn,
                    'fci': self.fore_conf_intss
                }
                pickle.dump(pack, f)

    def run(self, save_to=None):
        self.cook_hist_data()
        self.run_fci(save_to)

    def load_fci(self, path):
        if not Path(path).exists():
            raise FileNotFoundError('File does not exist! path = ', path)
        with open(path, 'rb') as f:
            pack = pickle.load(f)
            self.fci.fn = pack['fn']
            self.fore_conf_intss = pack['fci']

    def get_fci(self, row_i, alpha, fi=1):
        return self.fore_conf_intss[row_i-1][fi-1][alpha-1]

