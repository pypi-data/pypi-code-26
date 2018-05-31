from ._data import *


__all__ = ['read_data', 'cook_data', 'read_row_indices', 'has_row_indices']


def read_data(path, sep='\t', dtype=int):
    """ Reads data.

    Note: All data elements are of the same data type.
    :param path: directory or single path or a list of paths
    :param sep: separator
    :param dtype: data type
    :return: iterable (each row of data)
    """
    for row in _read_data(path, sep, dtype):
        yield row


def read_row_indices(path):
    """ Reads row indices.

    Note: row indices file has postfix '.ri' and the same file name with data file.
    :param path: data path
    :return: iterable (row indices)
    """
    for row_index in _read_row_indices(path):
        yield row_index


def has_row_indices(path):
    """ Exams whether row index files exist.

    :param path: data path
    :return: True or False
    """
    return _has_row_indices(path)


def cook_data(data, cooker, spices=None):
    """ Cooks data.

    :param data: iterable rows
    :param cooker: cooker name
    :param spices: single tuple or a list of tuples
    :return: iterable rows
    """
    for row in _cook_data(data, cooker, spices):
        yield row
