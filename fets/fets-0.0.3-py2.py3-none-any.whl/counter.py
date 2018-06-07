import pandas as pd
from sklearn.base import TransformerMixin


class TSCount(TransformerMixin):
    """IT will transform any numerical or non-numerical series into a series of
    integer representing the count of samples per period.
    """

    def __init__(self, period):
        self.period = period

    def fit(self, X, y=None):
        return self

    def transform(self, input_series):
        if not isinstance(input_series, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_series

        return input_series.resample(self.period).count()

