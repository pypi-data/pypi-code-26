from .util import array_equal
from .util import generate_ohlc_df
from .util import assert_ohlc_df
import numpy as np


def test_array_equal():
    l1 = [1, 2, 3, 4, 5]
    l2 = [1, 2, 3, 4, 5]
    l3 = [1, 2, 3, 4]
    l4 = [np.nan, np.nan, 1, 1]
    l5 = [np.nan, np.nan, 1, 1]

    assert array_equal(l1, l2)
    assert not array_equal(l1, l3)
    assert array_equal(l4, l5)


def test_generate_ohlc_df():
    df = generate_ohlc_df()
    assert_ohlc_df(df)
