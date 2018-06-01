import numpy as np
import combinatorics

def get_multiindex(m, n, deg):

    mn = m * n

    if deg > n:
        return

    p = combinatorics.binomial_coefficients(n, deg)[-1]
    q = m**deg

    vars = np.empty((p, deg), dtype=int)
    var = np.arange(deg)
    vars[0] = var.copy()

    for i in range(1, p):

        idx = deg - 1
        var[idx] += 1
        while var[idx] + deg - idx > n:
            idx -= 1
            var[idx] += 1
        for idx in range(idx + 1, deg):
            var[idx] = var[idx - 1] + 1

        vars[i] = var.copy()

    return vars
