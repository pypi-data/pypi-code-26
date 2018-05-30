import numpy as np
import pandas as pd


def array_equal(l1, l2):
    if not len(l1) == len(l2):
        return False

    for i in range(len(l1)):
        if np.isnan(l1[i]) and np.isnan(l2[i]):
            continue
        if not l1[i] == l2[i]:
            return False

    return True


def generate_ohlc_df():
    dates = pd.date_range('2018-1-1', '2018-1-31')
    data = [{'open': 1, 'high': 2, 'low': 1, 'close': 2, 'volume': 100}] * len(dates)
    return pd.DataFrame(data=data, index=dates)


def assert_ohlc_df(df):
    assert 'open' in df
    assert 'high' in df
    assert 'low' in df
    assert 'close' in df
    assert 'volume' in df

