import numpy as np
from pathlib import Path
from collections import Iterable


__all__ = ['load_data', 'cooker_move_sum', 'cook_data']


def load_data(path, sep='\t'):
    if not Path(path).exists():
        raise FileNotFoundError('File does not exist! path = ', path)
    with open(path, 'r') as f:
        for line in f.readlines():
            row = line[0: -1].split(sep)
            yield [int(x) for x in row]


def cook_data(data, params):
    """ Cooks data row by row.

    :param data: 2d matrix like data
    :param params: dict, of the following form:
        {
            'cooker': op func,
            'spices': tuple, option args
        }
    :return: iterable
    """
    cooker = params['cooker']
    spices = params['spices']
    for row in cooker(data, spices):
        yield row


def cooker_move_sum(rows, spices):

    if isinstance(spices, list):
        for row, opt in zip(rows, spices):
            yield _move_sum(row, *opt)
    else:
        for row in rows:
            yield _move_sum(row, *spices)


def _move_sum(row, k, step):
    m = (len(row) - k) // step + 1
    return [sum((row[i * step: i * step + k])) for i in range(m)]
