from .ohlc_feature_producer import FeatureProducerOHLC


class TimeLagsFeatureProducer(FeatureProducerOHLC):
    """
    Produce time lags feature.
    Time lag of feature X traces the previous value of X several time points ago.

    e.g.
    If a stock has close prices of [1, 2, 3, 4, 5, 6, 7], then the 3 time lag of it will be:
    [NaN, NaN, NaN, 1, 2, 3, 4]
    """
    def __init__(self, lags=5, feature='close', feature_label='tlag'):
        """
        Create a new TimeLagsFeatureProducer.

        :param lags: How many previous times lags you want to produce.
        :param feature: On which feature to produce time lags
        """
        FeatureProducerOHLC.__init__(self, feature_label)
        self.lags = lags
        self.feature = feature

    def produce(self, df):
        result = df.copy()

        for i in range(self.lags):
            result['%s_%s_%d' % (self.feature, self.feature_label, i + 1)] = result[self.feature].shift(1 + i)

        return result

