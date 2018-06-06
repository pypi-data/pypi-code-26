import multiindex
import combinatorics
from scipy.sparse.linalg import svds
import numpy as np
from scipy.sparse import csc_matrix
from fortran_module import fortran_module


def one_hot(x, degs):

    x = np.array(x)
    dim = len(x.shape)

    if dim == 1:
        n = 1
        m = np.array([np.unique(x).shape[0]])
        l = x.shape[0]
    elif dim == 2:
        n = x.shape[0]
        m = np.array([np.unique(xi).shape[0] for xi in x])
        l = x.shape[1]

    degs = np.array(degs)
    k = len(degs)
    max_deg = degs.max()

    idx_len = combinatorics.binomial_coefficients(n, max_deg)[degs].sum()

    # x_idx = [multiindex.get_multiindex(n, deg) for deg in degs]
    idx = []
    for deg in degs:
        for i in multiindex.get_multiindex(n, deg):
            idx.append(i)

    mi = np.array([np.prod(m[i]) for i in idx])

    X = np.vstack(
        [combinatorics.mixed_radix_to_base_10(x[i], m[i]) for i in idx])

    stratifier = np.insert(mi.cumsum(), 0, 0)[:-1]

    data = np.ones(idx_len * l)
    indices = (X + stratifier[:, np.newaxis]).T.flatten()
    indptr = idx_len * np.arange(l + 1)

    return csc_matrix((data, indices, indptr)), idx


def categorize(x):

    dim = x.shape
    if len(dim) == 1:
        x = np.array([x])
    elif len(dim) == 2:
        x = np.array(x)
    else:
        print 'x should be 1- or 2-dimensional'
        return

    l = x.shape[1]

    unique_states = [np.sort(np.unique(xi)) for xi in x]

    m = np.array([len(us) for us in unique_states])

    for i, us in enumerate(unique_states):
        # if np.all(us == np.arange(1, m[i] + 1)):
        #     continue
        num = dict(zip(us, np.arange(m[i])))
        x[i, :] = [num[x[i, j]] for j in range(l)]

    x = x.astype(int)

    cat = [
        dict(zip(np.arange(m[i]), us)) for i, us in enumerate(unique_states)
    ]

    return x, m, cat


def discrete_fit(x, y, degs, iters, overfit):
    # x: sum(p) by l
    # ------------------------------------
    # x1: x[i_x[0]:i_x[1], :] -- p[0] by l
    # ------------------------------------
    # x2: x[i_x[1]:i_x[2], :] -- p[1] by l
    # ------------------------------------
    # ...
    # ------------------------------------
    # i_x = np.insert(p.cumsum(), 0, 0)

    x = np.array(x)
    y = np.array(y)

    if x.shape[-1] != y.shape[-1]:
        print 'number of samples must be same for both x and y'
        return
    else:
        l = x.shape[-1]

    x, m_x, cat_x = categorize(x)
    y, m_y, cat_y = categorize(y)

    n_x = x.shape[0]
    n_y = y.shape[0]

    x_oh, idx = one_hot(x, degs)

    x_oh_rank = np.linalg.matrix_rank(x_oh.todense())
    # x_oh_svd = svds(x_oh, k=min(x_oh_rank, n_x - 1))
    x_oh_svd = svds(x_oh, k=x_oh_rank)

    x_oh_pinv = [x_oh_svd[2].T, 1.0 / x_oh_svd[1], x_oh_svd[0].T]

    par, disc, it = fortran_module.discrete_fit(x, y, m_x, m_y,
                                                m_y.sum(), degs, x_oh_pinv[0],
                                                x_oh_pinv[1], x_oh_pinv[2],
                                                iters, overfit)

    idx_by_deg = [multiindex.get_multiindex(n_x, deg) for deg in degs]
    mi = np.array(
        [np.sum([np.prod(m_x[i]) for i in idx]) for idx in idx_by_deg])
    mi = np.insert(mi.cumsum(), 0, 0)

    par = {deg: par[:, mi1:mi2] for (mi1, mi2) in zip(mi[:-1], mi[1:])}

    disc = [d[1:it[i]] for i, d in enumerate(disc)]

    return par, disc


def fit(x, y, degs, iters=100, overfit=True):

    if x.dtype != 'float' and y.dtype != 'float':
        return discrete_fit(x, y, degs, iters, overfit)
