"""Useful pickling functions.

WARNING! Remember to use `from __future__ import absolute_import`
to avoid naming conflicts with the `pickle` module from standard library.
"""
from __future__ import absolute_import

try:
    import cPickle as pickle
except Exception as ex:
    import pickle


def write_pickle(obj, filename, encoding='ASCII'):
    """Write an object to file as a pickle.

    No error handling is done by this function!

    Args:
        obj (any): Any serializable object.
        filename (str): Full path of filename, ideally to have `.pkl` extention.

    Returns:
        None
    """
    pickle.dump(obj,
                open(filename, 'wb'),
                protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle(filename, encoding='ASCII'):
    """Read an object from a pickle file.

    No error handling is done by this function!

    Args:
        filename (str): Full path of filename.

    Returns:
        any (obj): Object within the file. It can be of any type.
    """
    with open(filename, 'rb') as f:
        obj = pickle.load(f, encoding=encoding)

    return obj
