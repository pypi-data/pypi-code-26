"""Common Funtions. """

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ['get_yesno', 'get_nth', 'get_limits', 'get_input',
           'nearest', 'pycommand', 'sort_nicely', 'nrange',
           ]

__date__ = '03/10/2018'
__version__ = '0.1.1'
__author__ = 'J.G. Chen'
__email__ = 'cjgls@pku.edu.cn'

import sys
import select
import re

import numpy as np


def get_yesno(prompt="Yes?[y/N]: ", default=False, timeout=5):
    """Get yes/no from input, return Ture/False correspondingly.

    Parameters
    ----------
    prompt : str
        prompt string
    default : bool
        default if no input
    timeout : int
        return default value if no input after `timeout` second

    Returns
    -------
    ret : bool
        return True/False according to the input.
        if input is in ['y', 'Y', 'yes', 'Yes', 'YES', 'T', 'True'],
        return True, if option in ['n', 'N', 'no', 'No', 'NO', 'F', 'False'],
        return False, otherwise, return ``default``

    """

    # nicely change prompt
    if 'y/n' not in prompt.lower():
        prompt = prompt.split('?')[0] + '?[{}]: '.format(
            'Y/n' if default else 'y/N')

    # option = raw_input(prompt) or default
    # timeout in 5 second
    print(prompt)
    i, o, e = select.select([sys.stdin], [], [], timeout)
    if i:
        option = sys.stdin.readline().strip()
    else:
        return default

    if option in ['y', 'Y', 'yes', 'Yes', 'YES', 'T', 'True']:
        return True
    elif option in ['n', 'N', 'no', 'No', 'NO', 'F', 'False']:
        return False
    else:
        return default


def get_input(prompt='input', timeout=5):
    """Get input from stdin with timer

    Parameters
    ----------
    prompt : str
        prompt for input
    timeout : int
        timeout autometcically after ``timeout`` seconds

    Returns
    -------
    ret : str or None
        return input as str, None if no input

    """

    print(prompt)
    i, o, e = select.select([sys.stdin], [], [], timeout)
    if i:
        ret = sys.stdin.readline().strip()
    else:
        ret = None

    return ret


def get_nth(n_th, end, start=0, pad='const'):
    """Get the nth value in closed interval [start, end]

    Parameters
    ----------
    start, end : int
    n_th : scalar, 1D array-like of integer
    pad : str ['const'|'circle']
        if n_th > end-start+1:

            - pad='const': return the value at the nearest boundary
            - pad='circle': find the 'n_th value in period array
                [start, ..., end, ..., start, ..., end]

    Returns
    -------
    result : scalar or 1d-ndarray integer
        the `n_th` value in series 'start, start+1, ..., end'

    """

    if not (isinstance(end, int) and isinstance(start, int)
            and (np.array(n_th).dtype in ['int', 'int64'])):
        raise ValueError('parameters must be integer')
    nsize = np.abs(end - start) + 1

    result = []
    if isinstance(n_th, (tuple, list, np.ndarray)):
        if pad == 'circle':
            for i in n_th:
                result.append(start + i % nsize)
            result = np.array(result)
        else:
            for i in n_th:
                i = i if np.abs(i) < nsize else np.sign(i) * (nsize - (i > 0))
                if i < 0:
                    i += nsize
                result.append(start + i)
            result = np.array(result)
    else:
        if pad == 'circle':
            result = start + n_th % nsize
        else:
            n_th = (n_th if np.abs(n_th) < nsize
                    else np.sign(n_th) * (nsize - (n_th > 0)))
            if n_th < 0:
                n_th += nsize
            result = start + n_th
    return result


def get_limits(array):
    """Get the minium and maxium value of `array`

    Parameters
    ----------
    array : scalar, array-like,

    Returns
    -------
    vmin, vmax : float
        minium and maxium value of `array`.

    """
    try:
        vmin, vmax = np.array(array).min(), np.array(array).max()
    except:
        raise
        return None
    return np.asarray([vmin, vmax])


def nearest(array, target, value=False):
    """Find the element in `array` which is closest to target

    Parameters
    ----------
    array : array-like
    target : scalar|array-like
    value : bool, False by default
        if True, then return the data closest to the target

    Returns
    -------
    index : scalar, ndarray
    data : scalar, ndarray
    if `value` is True, return (index, data), return index (by default)
    otherwise.

    """
    if not(isinstance(array, (list, tuple, np.ndarray))):
        raise TypeError("Only 1d-list, tuple or 1d-ndarray supported!")
        return None
    if not(isinstance(target, (list, tuple, np.ndarray))):
        # scalar
        index = np.abs(array - target).argmin()
        data = array[index]
    else:
        # 1D array-like
        if len(np.array(array).shape) != 1:
            raise TypeError("Only 1d-list, tuple or 1d-ndarray supported!")
            return None
        index = np.asarray([np.abs(array - i).argmin() for i in target])
        data = np.asarray(array)[index]

    # return
    if value:
        return index, data
    else:
        return index


def nrange(start, stop, step, endpoint=True):
    """Return evenly spaced numbers over a specified interval except endpoint:
    interval [`start`, `start`+`step`, ..., `stop`]

    The endpoint `stop` of the the interval can optionally be excluded.

    Parameters
    ----------
    start : scalar
        The starting value of the sequence
    stop : scalar
        The end value of the sequence, unless `endpoint` is set to False.
    step : scale
        The spacing between samples.
    endpoint : bool, optional
        If True, `stop` is the last sample. Otherwise, it is not included.
        Default is True.

    Returns
    -------
    samples : ndarray
        Array of evenly spaced values.

        ``[start, start+step, ..., start+n*step, stop]`` or
        ``[start, start+step, ..., start+n*step]`` where `start+n*step < stop`
        (depending on wether `endpoint` is True or False).

    """
    samples = list(np.arange(start, stop, step))
    if endpoint and samples[-1] != stop:
        samples.append(stop)

    return np.array(samples)


def pycommand(default=None, lvars=None, gvars=None):
    """Run python command

    Parameters
    ----------
    default : str, optional, default: None
        default commands will be run first.
    lvars, gvars : dict, optional, default: None
        pass local and global vars to this function.

    Returns
    -------
    None

    """

    print("input python commands, or type 'q' to exit:")
    if default:
        for i in default.split(';'):
            i = i.lstrip()
            print(">>> " + i)
            exec(i)

    while True:
        command = raw_input(">>> ")
        try:
            exec(command)
        except Exception as E:
            if command in ['EOF', 'eof', 'exit', 'quit', 'q']:
                break
            print("  Error message:\n  " + str(E))
            print("Try again:")
            pass
    return None


def sort_nicely(l):
    """Sort the given list in the way that humans expect.

    Parameters
    ----------
    l : list, tuple

    Returns
    -------
    result : list

    Examples
    --------
    >>> a=['z20', 'z2', 'z10']
    >>> sort_nicely(a)
    ['z2', 'z10', 'z20']
    >>> a.sort()
    ['z10', 'z2', 'z20']

    """
    def tryint(s):
        """Convert to int."""
        try:
            return int(s)
        except:
            return s

    def alphanum_key(s):
        """Turn a string into a list of string and number chunks.

        "z23a" -> ["z", 23, "a"]

        """
        try:
            return [tryint(c) for c in re.split('([0-9]+)', s)]
        except:
            return [s]

    result = list(l[:])
    result.sort(key=alphanum_key)
    return result
