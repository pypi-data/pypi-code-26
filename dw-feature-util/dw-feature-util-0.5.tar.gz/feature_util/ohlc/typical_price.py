from .ohlc_feature_producer import FeatureProducerOHLC


class TypicalPriceFeatureProducer(FeatureProducerOHLC):
    """
    Produce typical price feature.
    tp = (High + Low + Close) / 3
    """
    def __init__(self, feature_label='tp'):
        FeatureProducerOHLC.__init__(self, feature_label)

    def produce(self, df):
        result = df.copy()
        high = result['high']
        low = result['low']
        close = result['close']
        result[self.feature_label] = (high + low + close) / 3.0

        return result
