#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np


def get_max_component_indices(x):
    '''Get the maximum component indices.'''
    ind1 = x.argmax(axis=x.ndim-1)
    ind2 = np.indices(ind1.shape)
    shape = (ind2.shape[0]+1,) + ind2.shape[1:]
    return tuple(np.append(ind2, ind1).reshape(shape))


def remove_component(x, *, indices):
    '''Removes a component at the specified index.'''
    ma = np.ma.array(x, mask=False)
    ma.mask[indices] = True
    shape = x.shape[:-1] + (x.shape[-1] - 1,)
    return ma.compressed().reshape(shape)


def remap(value, src_min, src_max, dst_min, dst_max):
    '''Maps values from [`src_min`, `src_max`]  to [`dst_min`, `dst_max`].

    Args:
        value: The incoming value to be converted.
        src_min: Lower bound of the value current range.
        src_max: Upper bound of the value current range.
        dst_min: Lower bound of the value target range.
        dst_max: Upper bound of the value target range.

    Returns:
        The resulting value.

    Examples:
    '''
    return (((value - src_min) / (src_max - src_min)) * (dst_max - dst_min)) + dst_min


def _can_express_norm(nbits, dtype):
    '''Can express normalized integers?'''
    return nbits <= (1 + np.finfo(dtype).nmant)
