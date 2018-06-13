from os import path
from unittest import TestCase
import pandas as pd
import pandas.util.testing as pdt

from .data import read_time_series_csv


def assert_ts_frame_equal(df, filename, generate_ref=False, precision=10):
    df = df if isinstance(df, pd.DataFrame) else df.to_frame()
    df.columns = df.columns.astype(str)
    df = df.round(precision)
    if generate_ref:
        df.to_csv(filename)
    else:
        df_ref = read_time_series_csv(filename)
        pdt.assert_frame_equal(df_ref, df, check_less_precise=precision)


class TsTestCase(TestCase):
    assert_pd_series_equal = staticmethod(pdt.assert_series_equal)
    assert_pd_frame_equal = staticmethod(pdt.assert_frame_equal)

    @classmethod
    def setUpClass(cls):
        cls.ref_dir = cls.get_ref_dir()

    @classmethod
    def get_ref_dir(cls):
        raise NotImplementedError()

    def assert_frame_equal(self, df, name, generate_ref=False, precision=10):
        filename = path.join(self.ref_dir, name + ".csv")
        assert_ts_frame_equal(
            df, filename, generate_ref=generate_ref, precision=precision
        )
