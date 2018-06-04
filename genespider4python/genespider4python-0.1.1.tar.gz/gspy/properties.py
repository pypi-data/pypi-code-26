import numpy as _np
from scipy.stats import chi2 as _chi2

_alpha = 0.01


class SNR:

    def __init__(self, X=None, E=None, df=None, s2=None, alpha=_alpha):
        "docstring"

        if X is not None:
            self.X = X

        if E is not None:
            self.E = E

        self.Sigma = _np.linalg.svd(self.X, compute_uv=False)

        if s2 is not None:
            if isinstance(s2, float) or isinstance(s2, int):
                s2 = [s2]

            self.s2 = s2

        self.alpha = alpha
        if df is None:
            df = _np.prod(X.shape)

        self._df = df

    def SNRmatrixspectra(self, s2=None, true=False):

        if s2 is None:
            s2 = self.s2[0]

        df = self._df

        chi2inv = _chi2.ppf(1 - self.alpha, df)

        SNR = []
        if true:
            ESigma = _np.linalg.svd(self.E, compute_uv=False)
            for S_n in self.Sigma:
                SNR.append(S_n / _np.max(ESigma))
        else:
            for S_n in self.Sigma:
                SNR.append(S_n / _np.sqrt(chi2inv * s2))

        SNR = _np.array(SNR)

        return SNR

    def SNRvectorspectra(self, S2=None, true=False):

        SNR = []
        if true:
            for i in self.X:
                SNR.append(_np.linalg.norm(self.X[i]) / _np.linalg.norm(self.E[i]))

        else:
            if S2 is None:
                if hasattr(self, "CVE"):
                    S2 = _np.diag(self.CVE)
                else:
                    raise ValueError("A vector 'S2' of variances must be supplied.")

            df = self._df
            df = df // self.X.shape[1]
            chi2inv = _chi2.ppf(1 - self.alpha, df)

            for i, x in enumerate(self.X):
                SNR.append(_np.linalg.norm(self.X[x]) / _np.sqrt(chi2inv * S2[i]))

        SNR = _np.array(SNR)

        return SNR

    def scaleVariance2SNR(self, SNR, n=None):
        """Scale the variance to match a wished SNR"""

        if n is None:
            n = min(self.X.shape)

        S_n = self.Sigma[n]
        df = self._df

        chi2inv = _chi2.ppf(1 - self.alpha, df)

        s2 = S_n**2 / (chi2inv * SNR**2)

        return s2
