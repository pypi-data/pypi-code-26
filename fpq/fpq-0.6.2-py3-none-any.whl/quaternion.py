#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from . import utils
from . import fp


def encode_quat_to_uint(q, *, dtype=np.uint64, encoder=fp.encode_fp_to_std_snorm):
    '''Encode Quaternions to unsigned integers.

    Args:
        q: Should be represented by four components of float, or an array of them.
        dtype: The type should be unsigned integer types.
        encoder: This is a function encodes a floating point to an unsigned integer.

    Returns:
        The resulting unsigned integers.
    '''
    assert (isinstance(q, np.ndarray) and (q.dtype.kind == 'f')), \
        '`dtype` of the argument `q` should be floating point types.'
    assert (dtype().dtype.kind == 'u'), \
        '`dtype` of the argument `dtype` should be unsigned integer types.'

    nbits_per_component = ((dtype().dtype.itemsize * 8) - 2) // 3

    max_abs_ind = utils.get_max_component_indices(np.fabs(q))
    sign = np.where(q[max_abs_ind] < 0., -1., 1.)
    remaining = sign[..., None] * utils.remove_component(q, indices=max_abs_ind)

    # [-1/sqrt(2), +1/sqrt(2)] -> [-1, +1]
    src_max = np.reciprocal(np.sqrt(q.dtype.type(2.)))
    src_min = -src_max
    remaining = utils.remap(remaining, src_min, src_max, q.dtype.type(-1.), q.dtype.type(1.))

    enc = encoder(remaining, dtype=dtype, nbits=nbits_per_component)

    return (dtype(max_abs_ind[-1]) << dtype(nbits_per_component * 3)) \
           | (enc[..., 0] << dtype(nbits_per_component * 2)) \
           | (enc[..., 1] << dtype(nbits_per_component)) \
           | enc[..., 2]


def decode_uint_to_quat(q, *, dtype=np.float64, decoder=fp.decode_std_snorm_to_fp):
    '''Decode unsigned integers to Quaternions.

    Args:
        q: Should be represented by uint, or an array of them.
        dtype: The type should be floating point types.
        decoder: This is a function decodes an unsigned integer to a floating point.

    Returns:
        The resulting Quaternions.
    '''
    assert (q.dtype.kind == 'u'), \
        '`dtype` of the argument `q` should be unsigned integer types.'
    assert (dtype().dtype.kind == 'f'), \
        '`dtype` of the argument `dtype` should be floating point types.'

    bits_per_component = ((q.dtype.itemsize * 8) - 2) // 3

    shifts = np.array([bits_per_component * 3,
                       bits_per_component * 2,
                       bits_per_component,
                       0], dtype=q.dtype)
    mask = np.invert(q.dtype.type(np.iinfo(q.dtype).max) << q.dtype.type(bits_per_component))
    masks = np.array([0x3, mask, mask, mask], dtype=q.dtype)

    temp = (...,) + (None,) * q.ndim
    components = (q >> shifts[temp]) & masks[temp]

    # Decoding for quaternion components.
    dec = decoder(components[1:4], dtype=dtype, nbits=bits_per_component)

    # [-1/sqrt(2), +1/sqrt(2)] -> [-1, +1]
    src_max = np.reciprocal(np.sqrt(dtype(2.)))
    src_min = -src_max
    dec = utils.remap(dec, dtype(-1.), dtype(1.), src_min, src_max)

    c0 = np.sqrt(dtype(1.) - np.square(dec[0]) - np.square(dec[1]) - np.square(dec[2]))
    c1 = dec[0]
    c2 = dec[1]
    c3 = dec[2]

    max_c = components[0]
    permutation = [i for i in range(1, q.ndim + 1)] + [0, ]
    return np.where(max_c == 0, (c0, c1, c2, c3),
                    np.where(max_c == 1, (c1, c0, c2, c3),
                             np.where(max_c == 2, (c1, c2, c0, c3), (c1, c2, c3, c0)))).transpose(permutation)
