import numpy as _np
import pandas as _pd
from sklearn.linear_model import LinearRegression as _LinearRegression
# from sklearn.linear_model import lasso_path as  _lasso_path


_tol = _np.finfo(_np.float32).eps


def _select_variables_from_prior(prior, tol=_tol):

    selected_v = _np.abs(prior) > tol
    return _np.array(selected_v)


def _fill_in_from_prior(v, prior, tol=_tol):

    selected_v = _np.abs(prior) > tol

    tmp = _np.zeros(prior.shape)

    tmp[selected_v] = v

    return tmp


def subset_estimator(X, y, a_i, optimizer=_LinearRegression, tol=_tol, verbal=False, fit_intercept=False, **kwargs):

    if not isinstance(X, _np.ndarray):
        X = _np.array(X)
        if len(X.shape) == 1:
            X = X[_np.newaxis]

    if not isinstance(y, _np.ndarray):
        y = _np.array(y)
        if len(y.shape) == 0:
            y = y[_np.newaxis]

    if not isinstance(a_i, _np.ndarray):
        a_i = _np.array(a_i)

    optz = optimizer(fit_intercept=fit_intercept, **kwargs)

    if not (a_i > tol).any():

        optz.fit(_np.zeros(X.shape), _np.zeros(y.shape))

        # coef = a_i.copy()
        # coef = optz.coef_
    else:
        X_v = X[:, _select_variables_from_prior(a_i)]
        optz.fit(X_v, y)

        try:
            coef = _fill_in_from_prior(optz.estimator_.coef_.copy(), a_i)
            optz.estimator_.coef_ = coef.copy()
        except Exception as e:
            if verbal:
                print(e)

            coef = _fill_in_from_prior(optz.coef_.copy(), a_i)
            optz.coef_ = coef.copy()

        # coef = _fill_in_from_prior(optz.coef_, a_i)
        # optz.coef_ = coef

    return optz


def subset_estimator_all_variables(X, y, B, estimator=_LinearRegression, tol=_tol, **kwargs):

    if isinstance(y, _pd.Series):
        y = _pd.DataFrame(y).T

    estimators = {}
    for c, i in enumerate(y):

        wB = subset_estimator(X, y[i], B.loc[i], optimizer=estimator, **kwargs)
        estimators[i] = wB

    wB = _pd.DataFrame({k: v.coef_ for k, v in estimators.items()}, index=B.columns).T
    wB.index.name = "target"
    __ = wB.T.stack()
    __ = __[__ != 0]

    wB = __
    wB.name = "weight"

    return wB


def activity_estimator(prior, y, estimator=_LinearRegression, **kwargs):

    estimator = estimator(**kwargs)

    pr = prior.unstack(0).fillna(0).to_sparse(fill_value=0)

    estimator.fit(pr, y)

    return estimator
