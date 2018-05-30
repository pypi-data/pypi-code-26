from .ohlc_feature_producer import FeatureProducerOHLC

class PercentChangeFeatureProducer(FeatureProducerOHLC):
    """
    Produce percent change feature.

    e.g.
    For series [1, 2, 3, 4, 5], produces [NaN, 1, 0.5, 0.33, 0.25]
    """
    def __init__(self, feature='close', feature_label='pct_change'):
        FeatureProducerOHLC.__init__(self, feature_label)
        self.feature = feature

    def produce(self, df):
        result = df.copy()
        result['%s_%s' % (self.feature, self.feature_label)] = result[self.feature].pct_change()
        return result
