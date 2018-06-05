"""Perform a linear regression fit. """

__all__ = ['linear_regression']

from numpy import mean


def linear_regression(x, y):
    """Simple linear regression of two variables

    Parameters
    ----------
    x, y : ndarray

    Returns
    -------
    tuple(a, b)
    a, b : float
        y = a + bx

    """

    if x.size != y.size:
        raise ValueError("x and y inputs must be the same size")

    mx = mean(x)
    my = mean(y)

    b = (mean(x*y) - mx*my) / (mean(x**2) - mx**2)
    a = my - b*mx

    return a, b
