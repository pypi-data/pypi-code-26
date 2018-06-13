from os import path, walk
import pandas as pd


class CsvDataHandler(object):
    _suffix = ".csv"

    def __init__(self, data_dir):
        self.data_dir = data_dir

    def get_time_series_data(self, ticker):
        filename = ticker + self._suffix
        for dir_path, dir_names, filenames in walk(self.data_dir):
            if filename in set(filenames):
                return read_time_series_csv(path.join(dir_path, filename))


def read_time_series_csv(filename):
    return pd.read_csv(filename, header=0, parse_dates=True, index_col=0)
