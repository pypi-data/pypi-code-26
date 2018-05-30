from .ohlc_feature_producer import FeatureProducerOHLC
from .moving_average import SimpleMovingAverageFeatureProducer


class BollingerBandsFeatureProducer(FeatureProducerOHLC):
    """
    Produce BB (Bollinger Bands) feature.
    """

    def __init__(self, period=20, feature='close', feature_label='bb'):
        FeatureProducerOHLC.__init__(self, feature_label)
        self.period = period
        self.feature = feature

    def produce(self, df):
        result = df.copy()

        sma = result[self.feature].rolling(self.period).mean()
        std = result[self.feature].rolling(self.period).std()
        assert len(sma) == len(std)

        middle = sma
        upper = middle + (2.0 * std)
        lower = middle - (2.0 * std)

        result['%s_%d_upper' % (self.feature_label, self.period)] = upper
        result['%s_%d_middle' % (self.feature_label, self.period)] = middle
        result['%s_%d_lower' % (self.feature_label, self.period)] = lower

        return result
