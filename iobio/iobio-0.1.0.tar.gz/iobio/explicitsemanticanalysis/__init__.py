# package for explicit semantic analysis
from iobio.qnorm import QNorm
from pandas import concat as pd_concat

class ReferenceCorrelation:
    def __init__(self,data,reference,quantile_normalize=True,min_variance=0,corr_method='pearson'):
        self.quantile_normalize = quantile_normalize

        data_index = data.index
        reference_index = reference.index
        shared = data.index.intersection(reference.index)
        self._data = data.loc[shared]
        self._reference = reference.loc[shared]

        data_index = self._data.var(1)[min_variance<self._data.var(1)].index
        reference_index = self._reference.var(1)[min_variance<self._reference.var(1)].index
        self._shared = data_index.intersection(reference_index)
        self._data = self._data.loc[self._shared].copy()
        self._reference = self._reference.loc[self._shared].copy()
        if quantile_normalize:
            qfit = QNorm().fit(self._reference)
            self._data = qfit.transform(self._data)
            self._reference = qfit.transform(self._reference)
        self._corr = pd_concat([self._data,self._reference],1).corr(method=corr_method).iloc[self._data.shape[1]:].reset_index(drop=True)
    @property
    def features_selected(self):
        return self._shared
    @property
    def reference_correlations(self):
        return self._corr.iloc[:,self._data.shape[1]:].copy()
    @property
    def data_correlations(self):
        return self._corr.iloc[:,0:self._data.shape[1]].copy()
    def correlate(data,reference):
        self.reference = reference
        self.qfit = QNorm().fit(self.reference)
        return
