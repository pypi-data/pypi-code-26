from .indices_feature_producer import FeatureProducerIndices


class NasdaqIndexFeatureProducer(FeatureProducerIndices):
    def __init__(self, symbol='QQQ', feature='close', feature_label='nasdaq'):
        FeatureProducerIndices.__init__(self, symbol, feature, feature_label)

