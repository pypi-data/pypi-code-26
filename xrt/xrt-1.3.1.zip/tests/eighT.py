# -*- coding: utf-8 -*-
"""
Created on Fri Nov 06 13:02:19 2015

@author: konkle
"""
import numpy as np
import scipy.linalg as spl
import time

#k = 128*64
#rank = 256
k = 128
rank = 5


def get_matrix():
    ccr = np.random.random((k, rank)) - 0.5
    cci = np.random.random((k, rank)) - 0.5
    return ccr + 1j*cci


def solve(cE):
    start1 = time.time()
#    kwargs = dict()
    nn = cE.shape[0]
    kwargs = dict(eigvals=(nn-rank, nn-1))
    w, v = spl.eigh(cE, **kwargs)
    stop = time.time()
    print("k={0}; eigenvalue problem has taken {1} s".format(k, stop-start1))
    print('max w={0}, w.sum()={1}'.format(w.max(), w.sum()))
    print("shapes: w={0}, v={1}".format(w.shape, v.shape))
    print(w)

    rE = np.dot(np.dot(v, np.diag(w)), np.conj(v.T))
    print("diff source--decomposed = {0}".format(np.abs(cE - rE).sum()))
    return w, v


if __name__ == '__main__':
    cC = get_matrix()

    cC1 = np.dot(cC, cC.conjugate().T)
    w, v = solve(cC1)

    cC2 = np.dot(cC.conjugate().T, cC)
    w, v = solve(cC2)
