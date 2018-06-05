import pandas as pd
from sklearn.base import TransformerMixin

class TSCountPrefix(TransformerMixin):
    """ Count occurences starting with a given prefix
    """

    def __init__(self, period, keys, name=""):
        """Constructor

            Makes 1 to 1 timeseries

            :param period: resampling period like "5min" or "3M" for 3 months.
            :param keys: list or single string of the list of prefix to be
            filtered.
        """
        self.period = period
        self.keys = keys
        self.name = name

    def fit(self, X, y=None):
        return self

    def transform(self, input_data):
        if not isinstance(input_data, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_data

        if isinstance(self.keys, list) and len(self.keys) > 0:
            indexes_list = [input_data.index[input_data.str.match(r"^"+k+".*")]
                            for k in self.keys]
            if self.name == "":
                self.name = self.keys[0] + "_x" + str(len(self.keys))
        else:
            indexes_list = input_data.index[
                           input_data.str.match(r"^"+self.keys+".*")]
            if self.name == "":
                self.name = self.keys + "_CP"

        output_series = input_data[indexes_list].resample(self.period).count()
        output_series.name = self.name.replace(" ", "_")

        return output_series
