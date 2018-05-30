from ..feature_producer import FeatureProducer
from datasource.price import get_historical


class FeatureProducerIndices(FeatureProducer):
    """
    This is the base class for indices feature producer.
    It can provide popular indices data.
    """
    def __init__(self, symbol, feature, feature_label):
        """
        :param str feature: Which feature of index to produce (e.g. close)
        :param str feature_label: The label you like for new feature.
        :param str symbol: symbol code for index
        """
        FeatureProducer.__init__(self, feature_label)
        self.feature = feature
        self.symbol = symbol

    def produce(self, df):
        result = df.copy()

        df_index = [str(s)[:10] for s in sorted(df.index.values)]   # use index of given df to determine period
        freq = 'daily'  # TODO determine freq based on index of given df
        sp500_data = get_historical(self.symbol, df_index[0], df_index[-1], freq)[self.feature]
        result[self.feature_label] = sp500_data

        return result
