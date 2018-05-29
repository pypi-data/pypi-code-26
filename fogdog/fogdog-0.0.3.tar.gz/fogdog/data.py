from ._data import *


__all__ = ['read_data', 'cook_data', 'read_row_labels', 'has_row_labels']


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


def read_row_labels(path):
    """ Reads row labels.

    Note: row label file has postfix '.rl' and the same file name with data file.
    :param path: data path
    :return: iterable (row labels)
    """
    for row_label in _read_row_labels(path):
        yield row_label


def has_row_labels(path):
    """ Exams whether row label files exist.

    :param path: data path
    :return: True or False
    """
    return _has_row_labels(path)


def cook_data(data, cooker, spices=None):
    """ Cooks data.

    :param data: iterable rows
    :param cooker: cooker name
    :param spices: single tuple or a list of tuples
    :return: iterable rows
    """
    for row in _cook_data(data, cooker, spices):
        yield row
