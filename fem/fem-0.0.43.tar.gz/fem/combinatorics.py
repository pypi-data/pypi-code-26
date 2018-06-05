import numpy as np


def binomial_coefficients(n, k):
    seq = np.empty(k + 1, dtype=int)
    seq[0] = 1
    for i in range(1, k + 1):
        seq[i] = seq[i - 1] * (n - i + 1) / i
    return seq


def mixed_radix_to_base_10(x, m):
    """x: digits, m: bases"""
    res = x[0]
    for i in range(1, len(x)):
        res *= m[i]
        res += x[i]
    return res
