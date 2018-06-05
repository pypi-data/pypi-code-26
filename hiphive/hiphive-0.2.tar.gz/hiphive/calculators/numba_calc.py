import numpy as np


def cluster_force_contribution_einsum(positions, prefactors, numbers,
                                      fc_tmp, fc, order,
                                      disps,
                                      cluster, f, F):
    fc = fc.reshape((3,)*order)
    for p, pf in zip(positions, prefactors):
        t = [fc, list(range(order))]
        for i, a in enumerate(cluster):
            if i == p:
                continue
            t.append(disps[a])
            t.append([i])
        F[cluster[p], :] += pf * np.einsum(*t)


try:
    import numba

    @numba.jit(nopython=True)
    def tvl(fc, v, order):
        """Contracts a 3-dim tensor of rank n with a 3-dim vector from the left
        """
        t = 3**(order-1)
        fc[0:t] *= v[0]
        fc[t:2*t] *= v[1]
        fc[2*t:3*t] *= v[2]
        fc[0:t] = fc[0:t] + fc[t:2*t] + fc[2*t:3*t]

    @numba.jit(nopython=True)
    def tvr(fc, v, order):
        for i in range(3**(order-1)):
            t = 3*i
            fc[i] = fc[t]*v[0]+fc[t+1]*v[1]+fc[t+2]*v[2]

    @numba.jit(nopython=True)
    def contraction(fc, d, cluster, pos, order, prefac, f):
        i = 0
        for l in range(pos):
            v = d[cluster[l], :]
            tvl(fc, v, order - i)
            i += 1
        for r in range(order - pos - 1):
            v = d[cluster[order - r - 1], :]
            tvr(fc, v, order - i)
            i += 1
        f[0] = fc[0] * prefac
        f[1] = fc[1] * prefac
        f[2] = fc[2] * prefac

    @numba.jit(nopython=True)
    def cluster_force_contribution_numba(positions, prefactors, numbers,
                                         fc_tmp, fc, order,
                                         disps,
                                         cluster, f, F):
        for i in range(numbers):
            pos = positions[i]
            prefac = prefactors[i]
            for j in range(3**order):
                fc_tmp[j] = fc[j]
            contraction(fc_tmp, disps,
                        cluster, pos, order, prefac, f)
            a = cluster[pos]
            F[a, 0] += f[0]
            F[a, 1] += f[1]
            F[a, 2] += f[2]

    cluster_force_contribution = cluster_force_contribution_numba

except ImportError:

    cluster_force_contribution = cluster_force_contribution_einsum
