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
from __future__ import absolute_import, division, print_function

import copy
import numpy as np
import time

from ..models_1D import model
from ..skeleton import Skeleton

from .common import check_output_filename, get_discontinuities_hmax, \
    attach_model_parameters, compute_mesh_quality, print_mesh_info


def run_mesher_cartesian(inputs, output_filename, verbose=True,
                         overwrite_file=True, generate_plots=False,
                         write_mesh_to_file=True,
                         mesh_processing_callback=None):

    mode = "cartesian"
    __mesher_start = time.time()
    i = copy.deepcopy(inputs)

    # Couple things that are accessed quite a bit.
    ndim = 2 if i['mesh_type'] in ["AxiSEMCartesian", "Cartesian2D"] else 3
    is_axisem = i["mesh_type"] in ["AxiSEMCartesian"]

    # get the model parameters
    if verbose:
        print('Setting up background model and element sizes...')

    # Get background model.
    m = i["basic"]["model"]
    spline_order = i["advanced"]["model_spline_order"]
    mod = model.built_in(m, spline_order=spline_order) \
        if m in model.get_builtin_models() \
        else model.read(m, spline_order=spline_order)

    if write_mesh_to_file:
        output_filename = check_output_filename(output_filename, mod,
                                                overwrite_file, i)

    # get domain dimensions from the input
    ctg = i["cartesian%dD" % ndim] if not is_axisem \
        else i["cartesian2Daxisem"]

    min_z = ctg["min_z"]
    if is_axisem:
        if ctg["x"] > 0:
            c_dims = {"x": [0., ctg["x"]]}
        else:
            c_dims = {"x": [0., mod.scale / 1e3 - ctg["min_z"]]}
    else:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    c_dims["x"][0] *= 1e3
    if c_dims["x"][1] is None:
        c_dims["x"][1] = mod.scale
    else:
        c_dims["x"][1] *= 1e3

    if c_dims["x"][0] > c_dims["x"][1]:
        raise ValueError('min_x > max_x')

    if ndim == 3:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    # Convert to meters.
    min_z *= 1e3

    discontinuities, hmax = get_discontinuities_hmax(
        mod, i["basic"]["period"], i["advanced"]["elements_per_wavelength"],
        min_z, mode)

    # create the skeleton
    if verbose:
        print('Creating the skeleton...')

    # The refinement style depends on the dimension.
    rfg = i["refinement"] if 'refinement' in i else i["refinement3D"]

    if ndim == 2:
        horizontal_boundaries = (np.array([c_dims["x"][0]]) / mod.scale,
                                 np.array([c_dims["x"][1]]) / mod.scale)
    elif ndim == 3:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    sk, sk_info = Skeleton.create_cartesian_mesh(
        discontinuities, hmax, ndim,
        horizontal_boundaries=horizontal_boundaries,
        hmax_refinement=rfg["hmax_refinement"],
        refinement_style=rfg['refinement_style'],
        refinement_top_down=(not rfg["refinement_bottom_up"]),
        return_info_dict=True)

    # create the unstructured mesh
    if verbose:
        print('Creating the unstructured mesh...')

    m = sk.get_unstructured_mesh(scale=mod.scale)
    # Conserve memory.
    del sk

    if generate_plots:
        m.plot(show=False)
        m.plot_quality(quality_measure='equiangular_skewness')

    if i["advanced"]["simplex"]:
        conv_mode = {2: 'QuadToTri', 3: 'HexToTet40'}
        m.convert_element_type(conv_mode[ndim])

    # find outer boundaries
    m.find_side_sets()

    if is_axisem and len(mod.get_solid_fluid_boundaries()) > 0:
        def distance(points):
            z = points[:, -1]
            sfb = mod.get_solid_fluid_boundaries()
            sfb = sfb.reshape((len(sfb), 1))
            buff = np.abs(
                np.tile(z, (sfb.size, 1)) - np.tile(sfb, (1, len(z))))
            return np.min(buff, axis=0)

        m.find_side_sets_generic('solid_fluid_boundary', distance)

    # attach elastic parameters
    if verbose:
        print('attaching elastic parameters')

    z_centroid = m.get_element_centroid()[:, -1]
    z_node = m.points[:, -1]

    attach_model_parameters(i, mod, m, discontinuities, generate_plots, z_node,
                            z_centroid, verbose)
    m.attach_global_variable('reference_frame', 'cartesian')

    if verbose:
        print('Computing mesh quality...')
    cn, p_min, p_min_95p, p_min_max_z, dt, dt_min_z, max_edge_aspect_ratio, \
        max_equiangular_skewness = compute_mesh_quality(i, mod, z_centroid, m,
                                                        mode)

    # write to exodus
    if verbose:
        print('Writing mesh to file...')

    if write_mesh_to_file:
        comp_opts = ('gzip', 2) if i["advanced"]["compression"] else None
        m.write_exodus(output_filename, compression=comp_opts,
                       overwrite=overwrite_file)

    __mesher_end = time.time()
    runtime = __mesher_end - __mesher_start

    # print mesh info
    if verbose:
        print_mesh_info(i, mod, cn, p_min, p_min_95p, p_min_max_z, dt,
                        dt_min_z, m, max_edge_aspect_ratio,
                        max_equiangular_skewness, runtime, output_filename)

    return m, sk_info