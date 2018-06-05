# Adapted from: https://stackoverflow.com/questions/37935920/quantile-normalization-on-pandas-dataframe
# Citing: https://en.wikipedia.org/wiki/Quantile_normalization
class QNorm:
    def __init__(self):
        return
    def fit(self,df):
        return _QNormFit(self,df.stack().groupby(df.rank(method='first').stack().astype(int)).mean())
    def fit_transform(self,df):
        return fit(df).transform(df)
class _QNormFit:
    def __init__(self,parent,df):
        self.qnorm = parent
        self.rank_mean = df
        return
    def transform(self,df):
        return df.rank(method='min').stack().astype(int).map(self.rank_mean).unstack()

