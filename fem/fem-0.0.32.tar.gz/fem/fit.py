import combinatorics
import multiprocessing as mp
from scipy.sparse.linalg import svds
import numpy as np
import f90_fit
from scipy.sparse import csc_matrix
import multiprocessing as mp


def fit(x, y, m_x, m_y, degs, max_iters=100, iters=None, return_all=True):
    # x: sum(p) by l
    # ------------------------------------
    # x1: x[i_x[0]:i_x[1], :] -- p[0] by l
    # ------------------------------------
    # x2: x[i_x[1]:i_x[2], :] -- p[1] by l
    # ------------------------------------
    # ...
    # ------------------------------------
    # i_x = np.insert(p.cumsum(), 0, 0)

    if x.shape[-1] != y.shape[-1]:
        print 'number of samples must be same for both x and y'
        return -1
    else:
        l = x.shape[1]

    n_x = x.shape[0] if len(x.shape) > 1 else 1
    n_y = y.shape[0] if len(y.shape) > 1 else 1

    ohx = one_hot(x, m=m_x, n=n_x, degs=degs)
    ohy = one_hot(y, m=m_y, n=n_y, degs=degs)

    degs = np.array(degs)
    k = degs.shape[0]

    max_deg = degs.max()
    p = combinatorics.binomial_coefficients(n_x, max_deg)[degs]
    q = m_x**np.arange(max_deg + 1)[degs]
    pq = p * q

    p_sum = p.sum()
    pq_sum = pq.sum()

    ohx_rank = np.linalg.matrix_rank(ohx.todense())
    ohx_svd = svds(ohx, k=ohx_rank)

    ohx_pinv = [ohx_svd[2].T, 1.0 / ohx_svd[1], ohx_svd[0].T]

    iters = 20

    par, disc = [], []

    for yi in y:

        res = f90_fit.fit(
            x,
            yi,
            ohx_pinv[0],
            ohx_pinv[1],
            ohx_pinv[2],
            q,
            p,
            m_y,
            max_iters,
            p_sum=p_sum,
            l=l,
            ohx_rank=ohx_rank,
            pq_sum=pq_sum,
            k=k,
            iters=iters)

        it = res[0]

        if return_all:
            par.append(res[1][:it - 1])
            disc.append(res[2][1:it - 1])
        else:
            par.append(res[1][it - 2].squeeze())
            disc.append(res[2][it - 2])

    return par, disc


def one_hot(x, n, m, degs):
    l = x.shape[-1]

    degs = np.array(degs)
    k = degs.shape[0]

    max_deg = degs.max()
    p = combinatorics.binomial_coefficients(n, max_deg)[degs]
    q = m**np.arange(max_deg + 1)[degs]
    pq = p * q

    p_sum = p.sum()

    i_ohx = np.insert(pq.cumsum(), 0, 0)

    data = np.ones(p_sum * l)
    stratifier = np.hstack(
        [i_ohx[i] + q[i] * np.arange(p[i]) for i in range(k)])
    indices = (x + stratifier[:, np.newaxis]).T.flatten() - 1
    indptr = p_sum * np.arange(l + 1)

    return csc_matrix((data, indices, indptr))
