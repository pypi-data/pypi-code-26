from ..feature_producer import FeatureProducer


class FeatureProducerOHLC(FeatureProducer):
    """
    This is the base class for OHLC feature producer.
    Given a dataframe with OHLC data, a producer instance will produce
    a new feature based on those data.
    """
