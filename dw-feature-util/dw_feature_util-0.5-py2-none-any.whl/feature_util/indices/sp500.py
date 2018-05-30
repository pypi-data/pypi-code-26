from .indices_feature_producer import FeatureProducerIndices


class SP500IndexFeatureProducer(FeatureProducerIndices):
    def __init__(self, symbol='SPY', feature='close', feature_label='sp500'):
        FeatureProducerIndices.__init__(self, symbol, feature, feature_label)

