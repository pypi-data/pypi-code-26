import numpy as _np
import pandas as _pd
from sklearn.model_selection import LeaveOneOut as _LeaveOneOut
from sklearn.model_selection import PredefinedSplit as _PredefinedSplit
# from sklearn.model_selection import train_test_split


def eta(X, i):
    """
    Calculate the linear map of x_i on to X where
    x_i \in X for a set of i where i is over rows of X
    """

    if isinstance(X, _pd.DataFrame):
        X = X.values

    x = X[i, :].copy()
    Xtmp = _np.delete(X, (i), axis=0)
    # e = _np.sqrt(_np.linalg.norm(Xtmp.dot(x)))
    e = _np.sum(abs(Xtmp.dot(x.T)))

    return e


def _alleta(X):
    """
    Calculate the linear map of x_i on to X where
    x_i \in X for each i where i is over rows of X
    """

    m = X.shape[0]

    etax = []
    for i in range(m):
        etax.append(eta(X, i))

    return etax


def _include(X):
    """
    Given linear overlap of x on X what samples can be estimated
    to overlap better than noise.
    """

    etax = _alleta(X)

    s = _np.linalg.svd(X, compute_uv=False)
    s = s[-1]

    return etax >= s


def LOOCV_splitter(data):

    passed = [a and b for a, b in zip(_include(data.Y.T), _include(data.P.T))]
    loi = _np.argwhere(passed).T[0]
    fold = _np.ones(data.M)
    fold[passed] = loi
    fold[[not p for p in passed]] = -1

    # fold = range(data.M)
    splitter = _PredefinedSplit(fold)

    return splitter


def cv_filter_splitter(X, y=None, splitter=_LeaveOneOut(), reverse=False, **kwargs):

    s = _np.linalg.svd(X, compute_uv=False)
    s = s[-1]

    sy = 0
    pe = 1
    if y is not None:
        sy = _np.linalg.svd(y, compute_uv=False)
        sy = sy[-1]

    for train, test in splitter.split(X, y):
        e = eta(X, test)

        if y is not None:
            pe = eta(y, test)

        if reverse:
            if (e <= s) + (pe <= sy) < 2:
                yield train, test
        else:
            if (e >= s) and (pe >= sy):
                yield train, test
