#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of the lite version of the SalvusMesher package intended to
produce meshes for AxiSEM3D. If you are looking for the full version head
over to http://mondaic.com.

:copyright:
    Copyright (C) 2016-2018 Salvus Development Team <www.mondaic.com>,
                            ETH Zurich
:license:
    GNU General Public License, Version 3 [academic use only]
    (http://www.gnu.org/copyleft/gpl.html)
"""
from __future__ import division, print_function
import numpy as np

from .helpers import load_lib

lib = load_lib()


def __lexsort_internal_loop(dim, points, loc, segstart, segend):
    lib.lexsort_internal_loop(
        points.shape[0],
        dim,
        points.shape[1],
        points,
        loc,
        segstart,
        segend,
        len(segstart))


def get_global_lexi(points, tolerance_decimals=8):
    """
    get global numbering scheme based on lexicographic sorting

    Note that this method does not preserve previously existing sorting for
    points that are readily unique.

    :param points: points in ndim dimensional space stored in array with shape
        (ndim, npoints)
    :type points: numpy array
    :param tolerance_decimals: accuracy to assume for two points to be equal
        after renormalization of coordinates
    :type tolerance_decimals: integer

    :returns: tupel of the global indices as numpy integer array and shape
        (npoint,) and the number of global points
    """

    # do not work inplace here:
    points = points.copy()

    # initialization:
    ndim, npoints = points.shape
    tolerance = 10. ** (- tolerance_decimals)
    seg_bnd = np.zeros(npoints + 1, dtype='bool')
    seg_bnd[[0, -1]] = True
    segstart = np.array([0])
    segend = np.array([npoints])

    # find maximum spread in all dimensions
    maxmax = np.max([np.ptp(points[dim, :]) for dim in np.arange(ndim)])

    # compute absolute tolerances
    tolerance *= maxmax

    # array to keep track of the reshuffling
    loc = np.arange(npoints)

    # sort lexicographically in all dimensions, where in higher iterations only
    # those points that are the same in lower dimensions (within tolerance) are
    # sorted. This is not only faster, but also ensures the functionality of
    # the floating point tolerance.
    for dim in np.arange(ndim):
        # sort in each segment
        __lexsort_internal_loop(dim, points, loc, segstart, segend)

        if dim < ndim - 1:
            # update segments of same points
            seg_bnd[1:-1] = np.logical_or(
                seg_bnd[1:-1], np.abs(np.diff(points[dim, :])) > tolerance)
            segments = np.where(seg_bnd)[0]

            # remove length 1 segments, as these don't need sorting
            segfilt = np.where(np.diff(segments) > 1)[0]
            segstart = segments[:-1][segfilt]
            segend = segments[1:][segfilt]

    # compute distance between neighbours:
    dist_square = ((points[:, 1:] - points[:, :-1]) ** 2).sum(axis=0)

    # generate global index
    global_index = np.zeros(npoints, dtype='int')
    global_index[1:] = (dist_square > tolerance ** 2).cumsum()

    # total number of distinct points
    nglob = global_index[-1] + 1

    # resort index to the original sorting of points
    sorted_global_index = np.zeros(npoints, dtype='int')
    sorted_global_index[loc] = global_index

    return sorted_global_index, nglob


def unique_points(points, return_point_ids=False, return_inverse=False,
                  tolerance_decimals=8):
    global_ids, nglobal = get_global_lexi(points.T, tolerance_decimals)
    unique_points, unique_point_ids, inverse_idx = np.unique(
        global_ids, return_index=True, return_inverse=True)

    retval = points[unique_point_ids, :], global_ids
    if return_point_ids:
        retval += unique_point_ids,
    if return_inverse:
        retval += inverse_idx,

    return retval


def compress_points_connectivity(points, connectivity, return_mask=False,
                                 tolerance_decimals=8):
    points, global_ids = unique_points(
        points, tolerance_decimals=tolerance_decimals)
    connectivity = global_ids[connectivity]

    # remove points, that are not in the connectivity
    mask = np.zeros(points.shape[0], dtype='bool')
    mask[connectivity.ravel()] = True
    point_id_map = np.zeros(points.shape[0], dtype='int')
    point_id_map[mask] = np.arange(mask.sum())
    connectivity = point_id_map[connectivity]
    points = points[mask, :]

    retval = points, connectivity
    if return_mask:
        retval += mask,
    return retval