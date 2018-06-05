from sklearn.base import TransformerMixin


class DFColumSelect(TransformerMixin):

    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, input_df):
        return input_df[self.key]

