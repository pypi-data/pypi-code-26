import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion, _transform_one
from sklearn.externals.joblib import Parallel, delayed

class FeatureUnion2DF(FeatureUnion):
    """Default scikit learn FeatureUnion does not contacenate 
       the different transformers output into a dataframe.

       That is what DFFeatureUnion does.

       inspired by Michele Lacchia:
       https://signal-to-noise.xyz/post/sklearn-pipeline/
    """
    def fit_transform(self, X, y=None, **fit_params):
        # non-optimized default implementation; override when a better
        # method is possible
        if y is None:
            # Unsupervised transformation
            return self.fit(X, **fit_params).transform(X)
        else:
            # Supervised transformation
            return self.fit(X, y, **fit_params).transform(X)

    def transform(self, X):
        tr_names = [str(tr_name) for tr_name, trans, weight in self._iter()]

        Xs = Parallel(n_jobs=self.n_jobs)(
            delayed(_transform_one)(trans, weight, X)
            for _, trans, weight in self._iter())

        N = 0
        for X, tr in zip(Xs, tr_names):
            # dataframe case
            if hasattr(X, "columns"):
                X.columns = [col+"_"+tr for col in X.columns]   
            elif hasattr(X, "name"):
                X.name = str(N)+"_"+tr
                N += 1

        return pd.concat(Xs, axis=1, join='inner')

