from sklearn.base import BaseEstimator, TransformerMixin

class TSPolynomialAB(BaseEstimator, TransformerMixin):
    """Transforms a normalized series
       into polynomial function y = (1 - x^a)^b
    """
    def __init__(self, power_a=2, power_b=2):
        self.power_a = power_a
        self.power_b = power_b

    def fit(self, X, y=None):
        return self

    def transform(self, input_s):
       return (1 - input_s**self.power_a)**self.power_b


class TSNormalize(BaseEstimator, TransformerMixin):
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


class TSInterpolation(BaseEstimator, TransformerMixin):
    """ Interpolate according to a new indew
        linearly with respect to time or number of samples

    """
    def __init__(self, new_index=None, period="5min", method="time"):
        """
            :param new_index: Final desired index
            :param period: Used period if no index is given
            :param method: default is 'time', points will be interpolated wrt
            time. Another possible value is 'linear' wrt to index number.
        """
        self.new_index = new_index 
        self.period = period
        self.method = method

    def fit(self, X, y=None):
        return self

    def transform(self, input_s):
        if not isinstance(input_s, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_s
        
        output_s = pd.Series(data=[np.nan for i in self.new_index],
                             index=self.new_index)


        # after new step this we'll get a timeseries full of NaN but with
        # the few original points that are going to be interpolated
        output_s = input_s.combine_first(output_s)
        output_s = output_s.interpolated(method=self.method)
        output_s = output_s.reindex(self.new_index, method='nearest')

        return output_series


