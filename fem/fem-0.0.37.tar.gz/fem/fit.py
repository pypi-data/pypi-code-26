import multiindex
import combinatorics
from scipy.sparse.linalg import svds
import numpy as np
import f90_fit
from scipy.sparse import csc_matrix
import multiprocessing as mp


def mixed_radix_to_base_10(x, m):
    """x: digits, m: bases"""
    res = x[0]
    for i in range(1, len(x)):
        res *= m[i]
        res += x[i]
    return res


def one_hot(x, n, m, degs):

    if type(m) is int:
        m = np.repeat(m, n)
    elif len(m) != n:
        print 'm should be int or same as n'
        return

    l = x.shape[-1]

    degs = np.array(degs)
    k = len(degs)
    max_deg = degs.max()

    p = combinatorics.binomial_coefficients(n, max_deg)[degs]
    p_sum = p.sum()

    x_idx = [multiindex.get_multiindex(n, deg) for deg in degs]

    X = [x[i] for i in x_idx]
    M = np.array([m[i] for i in x_idx])

    for t in range(l):
        print 't', t
        for deg in degs:
            for xi, mi in zip(X[deg - 1][:, :, t], M[deg - 1]):
                print 1 + mixed_radix_to_base_10(xi - 1, mi)

    return x, x_idx, X, M

    # q = m**np.arange(max_deg + 1)[degs]
    # pq = p * q

    # i_ohx = np.insert(pq.cumsum(), 0, 0)

    # data = np.ones(p_sum * l)
    # stratifier = np.hstack(
    #     [i_ohx[i] + q[i] * np.arange(p[i]) for i in range(k)])
    # indices = (x + stratifier[:, np.newaxis]).T.flatten() - 1
    # indptr = p_sum * np.arange(l + 1)

    # return csc_matrix((data, indices, indptr))


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
        num = dict(zip(us, 1 + np.arange(m[i])))
        x[i, :] = [num[x[i, j]] for j in range(l)]

    x = x.astype(int)

    cat = [
        dict(zip(1 + np.arange(m[i]), us))
        for i, us in enumerate(unique_states)
    ]

    return x, m, cat


def new_fit(x, y, degs=[1]):

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

    return one_hot(x, n_x, m_x, degs)


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
