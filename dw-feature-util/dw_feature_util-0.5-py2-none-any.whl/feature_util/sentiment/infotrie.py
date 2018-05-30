from ..feature_producer import FeatureProducer
import quandl


class InfotrieSentimentFeatureProducer(FeatureProducer):
    def __init__(self, symbol, feature_label='sent'):
        FeatureProducer.__init__(self, feature_label)
        self.symbol = symbol

    def produce(self, df):
        result = df.copy()
        sentiments = quandl.get("NS1/%s_US" % self.symbol, 
                                authtoken="ngQ3rwakuwx-hu_DYyur")
        df_index = [str(s)[:10] for s in sorted(df.index.values)]
        sentiments = sentiments.loc[df_index[0]: df_index[-1]]

        result["%s" % self.feature_label] = sentiments['Sentiment']
        result["%s_high" % self.feature_label] = sentiments['Sentiment High']
        result["%s_low" % self.feature_label] = sentiments['Sentiment Low']
        result["%s_vol" % self.feature_label] = sentiments['News Volume']
        result["%s_buzz" % self.feature_label] = sentiments['News Buzz']

        return result