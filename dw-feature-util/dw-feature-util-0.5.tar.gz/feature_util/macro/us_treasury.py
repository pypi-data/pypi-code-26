from ..feature_producer import FeatureProducer
from datasource.treasury import get_us_treasury_yield


class USTreasuryYieldFeatureProducer(FeatureProducer):
    """
    This produces US treasury yield data. 
    """

    def __init__(self, maturity='10y', feature_label='us_treasury'):
        """
        Keyword Arguments:
            maturity {str} -- [Maturity period e.g 1m, 10y] (default: {'10y'})
        """
        FeatureProducer.__init__(self, feature_label)
        self.maturity = maturity

    def produce(self, df):
        result = df.copy()

        df_index = [str(s)[:10] for s in sorted(df.index.values)]
        treasury_data = get_us_treasury_yield(
            df_index[0], df_index[-1], maturity=self.maturity)
        result['%s_%s' % (self.feature_label, self.maturity)] = treasury_data

        return result
