from .ohlc_feature_producer import FeatureProducerOHLC


class ForceIndexFeatureProducer(FeatureProducerOHLC):
    """
    This produces Force Index feature.
    """

    def __init__(self, period=13, feature='close', adjust=True, feature_label='fi'):
        FeatureProducerOHLC.__init__(self, feature_label)
        self.period = period
        self.feature = feature
        self.adjust = adjust

    def produce(self, df):
        result = df.copy()

        fi_1 = result[self.feature].diff() * result['volume']
        fi_period = fi_1.ewm(span=self.period, adjust=self.adjust).mean()

        result['%s_1' % self.feature_label] = fi_1
        result['%s_%d' % (self.feature_label, self.period)] = fi_period

        return result
