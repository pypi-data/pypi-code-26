from .ohlc_feature_producer import FeatureProducerOHLC
from .typical_price import TypicalPriceFeatureProducer


class CCIFeatureProducer(FeatureProducerOHLC):
    """
    Produce the CCI (Commodity channel index) feature.

    Typically it's compared to +/-100, where cci > 100 means overbought and < -100 means oversold.
    """
    def __init__(self, period=20, feature_label='cci', abs_threshold=100):
        """

        :param period: The period for taking sma/mad for typical price
        :param feature_label: The name of feature column
        :param abs_threshold:
        The threshold to produce CCI relative value.
        If not given, the computed CCI valued will be produced directly. Otherwise, only values above abs_threshold or
        below - abs_threshold will be produced in the form of the difference between +/- abs_threshold
        """
        FeatureProducerOHLC.__init__(self, feature_label)
        self.period = period
        self.abs_threshold = abs_threshold  # TODO how we include the +/-100 threshold in the feature?

    def produce(self, df):

        def cci_scale(value):
            threshold = self.abs_threshold

            if abs(threshold) > value > - abs(threshold):
                return 0
            elif value > abs(threshold):
                return value - abs(threshold)
            else:
                return value + abs(threshold)

        result = df.copy()
        # make typical price first
        tp_producer = TypicalPriceFeatureProducer()
        tp = tp_producer.produce(result)['tp']

        tp_sma = tp.rolling(window=self.period).mean()
        tp_abs_sma_diff = (tp - tp_sma).abs()
        tp_mean_abs_devia = tp_abs_sma_diff.rolling(window=self.period).mean()

        cci_value = (tp - tp_sma) / (tp_mean_abs_devia * 0.015)

        if self.abs_threshold is not None:
            cci_value = cci_value.apply(cci_scale)

        result[self.feature_label] = cci_value
        return result
