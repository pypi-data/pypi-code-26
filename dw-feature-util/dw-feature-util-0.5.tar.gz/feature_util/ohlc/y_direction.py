import numpy as np
from .ohlc_feature_producer import FeatureProducerOHLC


class DirectionFeatureProducer(FeatureProducerOHLC):
    """
    NOTE: This is a y feature. (A feature that should be the training target)

    Produce price moving direction feature. 1 for going up (stay still) and 0 for going down.
    """
    def __init__(self, lags=1, feature='close', feature_label='direction'):
        FeatureProducerOHLC.__init__(self, feature_label)
        self.lags = lags
        self.feature = feature

    def produce(self, df):
        result = df.copy()

        for i in range(self.lags):
            feature_shift = result[self.feature].shift(-(i + 1))
            feature_diff = feature_shift - result[self.feature]
            direction = feature_diff.apply(lambda x: 1 if x >= 0 else 0 if x < 0 else np.nan)

            label = 'Y_%s_%s_%d' % (self.feature, self.feature_label, i + 1)
            result[label] = direction

        return result
