import numpy as np
from scipy.sparse import lil_matrix, csc_matrix
import combinatorics
import multiindex
import f90_simulate


def simulated_parameters(n=10, m=3, degs=[1], dist=None, dist_par=None):

    # helper variables
    mn = m * n
    mm = m * np.arange(n)

    if (dist is None) or (dist_par is None):
        dist = np.random.normal
        dist_par = (0.0, 1.0 / np.sqrt(mn))

    degs = np.array(degs)
    # monomials with degree larger than n guaranteed 0
    degs = degs[degs <= n]
    # degrees greater than 0
    degs1 = degs[degs > 0]
    # degrees greater than 1
    degs2 = degs[degs > 1]
    max_deg = degs.max()

    p = combinatorics.binomial_coefficients(n, max_deg)
    q = m**np.arange(max_deg + 1)

    # model parameters
    f = {deg: dist(*dist_par, size=(mn, p[deg] * q[deg])) for deg in degs}
    if 0 in degs:
        f[0] = np.vstack([fi - fi.mean(0) for fi in np.split(f[0], n)])
    if 1 in degs:
        f[1] = np.vstack([fi - fi.mean(0) for fi in np.split(f[1], n)])
        f[1] = np.hstack([
            fj - fj.mean(1)[:, np.newaxis] for fj in np.split(f[1], n, axis=1)
        ])

    return f


def simulated_data(par, n, m, l=None, o=1.0):

    degs = np.sort(par.keys())
    k = degs.shape[0]

    max_deg = degs.max()
    p = combinatorics.binomial_coefficients(n, max_deg)[degs]
    q = m**np.arange(max_deg + 1)[degs]
    pq = p * q

    p_sum = p.sum()

    x_idx = [multiindex.get_multiindex(n=n, m=m, deg=deg) for deg in degs]
    x_idx = 1 + np.hstack([i.flatten() for i in x_idx])

    par = np.hstack([par[deg] for deg in degs])

    if l is None:
        l = int(o * np.prod(par.shape))

    return f90_simulate.simulate_data(
        par,
        degs,
        p,
        q,
        x_idx,
        n,
        m,
        p_sum,
        l,
        nm=n * m,
        pq_sum=(p * q).sum(),
        k=k,
        pdegs_sum=(p * degs).sum())
