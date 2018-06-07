from sklearn.base import TransformerMixin

class TSPolynomialAB(TransformerMixin):
    """Transforms a normalized series
       into polynomial function y = (1 - x^a)^b
    """
    def __init__(self, power_a=2, power_b=2):


class TSNormalize(TransformerMixin):
    """Normalize input series to arbitrary bounds
        The series is truncated to min and max interval.
    """
    def __init__(self, bound_min=-1, bound_max=-1):
        self.bound_min =  bound_min
        self.bound_max =  bound_max

    def fit(self, X, y=None):
        return self

    def transform(self, input_s):
        if not isinstance(input_s, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_s

        if self.bound_min < 0 or self.bound_max < 0:
            self.bound_min = input_s.min()
            self.bound_max = input_s.max()

        # minimize(bound_max, input_s)
        input_s[input_s > self.bound_max] = self.bound_max
        input_s[input_s < self.bound_min] = self.bound_min

        # normalize the series
        norm_s = (input_s - self.bound_min) / (self.bound_max - self.bound_min)

        return output_series
