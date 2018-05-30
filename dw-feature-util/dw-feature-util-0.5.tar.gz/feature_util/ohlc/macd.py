from .ohlc_feature_producer import FeatureProducerOHLC
from .moving_average import ExponentialMovingAverageFeatureProducer


class MACDFeatureProducer(FeatureProducerOHLC):
    """
    Produce MACD feature.
    """

    def __init__(self, feature='close', fast_period=12, slow_period=26, signal_period=9, feature_label='macd'):
        FeatureProducerOHLC.__init__(self, feature_label)
        self.feature = feature
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def produce(self, df):
        result = df.copy()

        fast_ema_producer = ExponentialMovingAverageFeatureProducer(
            period=self.fast_period, feature=self.feature)
        slow_ema_producer = ExponentialMovingAverageFeatureProducer(
            period=self.slow_period, feature=self.feature)
        signal_ema_producer = ExponentialMovingAverageFeatureProducer(
            period=self.signal_period, feature='macd')

        ema_df = fast_ema_producer.produce(result)
        ema_df = slow_ema_producer.produce(ema_df)
        ema_df['macd'] = ema_df['%s_ema_%d' % (self.feature, self.fast_period)] - \
                         ema_df['%s_ema_%d' % (self.feature, self.slow_period)]
        ema_df = signal_ema_producer.produce(ema_df)
        ema_df['macd_hist'] = ema_df['macd'] - \
                              ema_df['macd_ema_%d' % self.signal_period]

        result[self.feature_label] = ema_df['macd']
        result['%s_signal' % self.feature_label] = ema_df['macd_ema_%d' %
                                                          self.signal_period]
        result['%s_hist' % self.feature_label] = ema_df['macd_hist']

        return result
