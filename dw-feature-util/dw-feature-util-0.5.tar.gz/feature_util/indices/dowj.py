from .indices_feature_producer import FeatureProducerIndices


class DowJIndexFeatureProducer(FeatureProducerIndices):
    def __init__(self, symbol='DIA', feature='close', feature_label='dowj'):
        FeatureProducerIndices.__init__(self, symbol, feature, feature_label)

