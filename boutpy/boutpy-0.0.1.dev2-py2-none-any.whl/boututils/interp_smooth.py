"""Functions for interpolation and smooth. """

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ['spline_smooth', 'smooth', 'interp', 'spline_interp']

__date__ = '06142017'
__version__ = '0.1.0'
__author__ = 'J.G. Chen'
__email__ = 'cjgls@pku.edu.cn'

import scipy.interpolate as si
import numpy as np
from matplotlib import docstring


def spline_smooth(x, y, w=None, index=None, sf=0.0001, **kwargs):
    """smooth 1-D profile by spline fitting.

    Parameters
    ----------
    x: (N,) array_like
        1-D array of independent input data. Must be increasing.
    y: (N,) array_like
        1-D array of dependent input data, of the same length as x.
    w: (N,) array_like, optional
        Weights for spline fitting. Must be positive.
        If None (default), weights are all equal.
        It is passed to scipy.interpolate.UnivariateSpline()
    index: 1-D int arry_like, optional
        Spline fitting by ignoring y[index], i.e.
        If weights ``w`` is None, then set ``w`` are all equal to 1
        EXCEPT that w[index] = 0
    sf: float, optional, default: 0.0001
        Smoothing factor
    All other keyword arguments are passed to:
        :func:`~scipy.interpolate.UnivariateSpline()`

    Returns
    -------
    ret: (N,) array_like
        1-D arry of smoothed data

    """

    # weight
    if w is None and index is not None:
        w = np.ones_like(x)
        w[index] = 0
    spl = si.UnivariateSpline(x, y, w=w, **kwargs)
    spl.set_smoothing_factor(sf)
    return spl(x)


def smooth(signal, wsize):
    """Smooth signal by averaging data in window size ``wsize``

    Parameters
    ----------
    signal: ndarray, list or tuple
        signal to be smoothed. Should be 1D ndarray, list or tuple.
    wsize: int
        window size to do the average.

    Returns
    -------
    nsignal: ndarray
        smoothed signal.
    None:
        when something goes wrong.

    Todo
    ----
    Signal can be 2D or multi-dimensions data. Use keyword axis to control
    how to smooth the signal.
    """

    nsignal = np.array(signal)
    size = nsignal.shape

    try:
        if len(size) != 1:
            raise TypeError
    except TypeError:
        print("TypeError: Only 1D array signal support")
        return None

    nsignal = np.convolve(nsignal, np.ones((wsize))/wsize, mode='same')
    return nsignal


@docstring.Appender(np.interp.__doc__)
def interp(x, xp, fp, left=None, right=None, period=None):
    """Revised version of np.interp() function for linear interpolation.

    check the range of x and xp, output the information if they are
    different.

    """

    if np.size(x) > 1 and ((x[0] != xp[0]) or (x[-1] != xp[-1])):
        print("WARNING: different x-coordinates:")
        print("     original: [{}, {}]".format(xp[0], xp[-1]))
        print("     after interpolation: [{}, {}]".format(x[0], x[-1]))
    elif np.size(x) == 1:
        print("WARNING: different x-coordinates:")
        print("     original: [{}, {}]".format(xp[0], xp[-1]))
        print("     after interpolation: {}".format(x))
    return np.interp(x, xp, fp, left=left, right=right, period=period)


def spline_interp(x, y, kind='cubic', range=[0, -1], smooth_factor=0.0001,
                  zoom=1):
    """Spline interpolation
    range[1] index point not included
    """
    print("need to add help doc")
    if len(x) != len(y):
        print("ERROR: mismatch size")
        return None
    if range[1] == -1:
        range[1] = len(y)
    if range[0] < 0 or range[1] < 0:
        print("only positive range supported")
        print("return None")
        return None

    print("smooth_factor :", smooth_factor)
    print("zoom factor   :", zoom)
    tmpx = np.linspace(x[range[0]], x[range[1]-1],
                       int(len(y[range[0]:range[1]])*zoom))
    tmpy = si.interp1d(x[range[0]:range[1]], y[range[0]:range[1]],
                       kind=kind)(tmpx)
    spl = si.UnivariateSpline(tmpx, tmpy)
    spl.set_smoothing_factor(smooth_factor)
    return np.concatenate((y[:range[0]], spl(x[range[0]:range[1]]),
                           y[range[1]:]))
