from .ohlc_feature_producer import FeatureProducerOHLC


class SimpleMovingAverageFeatureProducer(FeatureProducerOHLC):
    """
    Produce simple moving average (SMA) feature.

    e.g.
    For series [1, 2, 3, 4, 5, 6, 7], a window 2 SMA produces [NaN, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
    """

    def __init__(self, period=5, feature='close', min_period=None, feature_label='sma'):
        FeatureProducerOHLC.__init__(self, feature_label)
        self.feature = feature
        self.period = period
        self.min_period = min_period

    def produce(self, df):
        result = df.copy()
        result['%s_%s_%d' % (self.feature, self.feature_label, self.period)] = \
            result[self.feature].rolling(
                window=self.period, min_periods=self.min_period).mean()
        return result


class ExponentialMovingAverageFeatureProducer(FeatureProducerOHLC):
    """
    Produce exponential moving average (EMA) feature.
    """

    def __init__(self, period=5, feature='close', min_period=0, adjust=True, feature_label='ema'):
        FeatureProducerOHLC.__init__(self, feature_label)
        self.feature = feature
        self.period = period
        self.min_period = min_period
        self.adjust = adjust

    def produce(self, df):
        result = df.copy()
        result['%s_%s_%d' % (self.feature, self.feature_label, self.period)] = \
            result[self.feature].ewm(
                span=self.period, min_periods=self.min_period, adjust=self.adjust).mean()
        return result
