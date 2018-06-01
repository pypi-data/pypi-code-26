import numpy as np


def binomial_coefficients(n, k):
    seq = np.empty(k + 1, dtype=int)
    seq[0] = 1
    for i in range(1, k + 1):
        seq[i] = seq[i - 1] * (n - i + 1) / i
    return seq
