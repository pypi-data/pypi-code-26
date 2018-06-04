import numpy as _np
from .linear_model import _select_variables_from_prior, _fill_in_from_prior


def subset_optimizer(X, Y, prior, optimizer, **kwargs):

    if not isinstance(X, _np.ndarray):
        X = _np.array(X)

    if not isinstance(prior, _np.ndarray):
        Y = _np.array(Y)

    if not isinstance(prior, _np.ndarray):
        prior = _np.array(prior)

    optz = optimizer.set_params(**kwargs)

    # e = []
    n = Y.shape[1]
    A = _np.array([])
    for j in range(n):
        a_j = prior[j, :]
        y = Y[:, j]

        if not a_j.any():
            # ypred = _np.zeros(Y.shape[0])
            coef = a_j.copy()

        else:
            X_v = X[:, _select_variables_from_prior(a_j)]
            optz.fit(X_v, y)

            coef = _fill_in_from_prior(optz.coef_, a_j)
            # ypred = optz.predict(X_v)

        # e.append(mean_squared_error(y_true=y, y_pred=ypred))

        if j == 0:
            A = _np.hstack([A, coef])
        else:
            A = _np.vstack([A, coef])

    return A
