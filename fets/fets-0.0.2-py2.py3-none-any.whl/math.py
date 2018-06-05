
class TSPolynomialAB(TransformerMixin):
    """Transforms numerical values in bounds [min, max]
       into polynomial function y = (1 - x^a)^b
    """

    def __init__(self, bound_min, bound_max, power_a=2, power_b=2):
        self.bound_min =  bound_min
        self.bound_max =  bound_max

    def fit(self, X, y=None):
        return self

    def transform(self, input_series):
        if not isinstance(input_series, pd.Series):
            print("Input data is not a pd.Series (TODO throw)")
            return input_series

        output_series = min(bound_max, input_series)

        return output_series
