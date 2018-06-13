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

from collections import defaultdict
import copy
import json
import numpy as np
from scipy.interpolate import RectSphereBivariateSpline
import time


from ..models_1D import model
from ..skeleton import Skeleton
from .. import elements as elem

from . import common as cm
from .common import check_output_filename, get_discontinuities_hmax, \
    compute_mesh_quality, print_mesh_info, build_exterior_mesh, mask_mesh


R_OCEAN_REF = 1.1


def run_mesher_spherical(inputs, output_filename, verbose=True,
                         overwrite_file=True, generate_plots=False,
                         write_mesh_to_file=True,
                         mesh_processing_callback=None, **kwargs):

    get_dem = kwargs.get('get_dem', cm.get_dem)
    attach_model_parameters = kwargs.get('attach_model_parameters',
                                         cm.attach_model_parameters)

    mode = "spherical"
    __mesher_start = time.time()
    i = copy.deepcopy(inputs)

    # Couple things that are accessed quite a bit.
    sphgrp = i['spherical'] if "spherical" in i else i['spherical2D']
    ndim = 2 if i['mesh_type'] in ["Circular2D", "AxiSEM"] else 3
    is_axisem = i["mesh_type"] in ["AxiSEM"]
    add_ocean = (
        'ocean' in i and not i["ocean"]["ocean_layer_style"] in
        ['none', 'loading'] and not i["ocean"]["bathymetry_file"] == '')
    add_ocean_loading = (
        'ocean' in i and not i["ocean"]["ocean_layer_style"] == 'none' and
        not i["ocean"]["bathymetry_file"] == '')
    add_exterior_mesh = "gravity_mesh" in i and \
        i["gravity_mesh"]["add_exterior_domain"]

    sw_mode = i["mesh_type"] in ["Globe3DSurfaceWaves",
                                 "SphericalChunk3DSurfaceWaves"]

    if add_ocean and add_exterior_mesh:
        if not i["ocean"]["ocean_layer_style"] == 'anisotropic_tripling':
            # @TODO this error msg does not seem to be up to date
            raise ValueError(
                'Cannot combine an extruded fluid ocean and the external '
                'domain. Use ocean_layer_style: "anisotropic_tripling" '
                'instead.')
        else:
            raise NotImplementedError

    # get the model parameters
    if verbose:
        print('Setting up background model and element sizes...')

    # Get background model.
    m = i["basic"]["model"] if not sw_mode else i["basic_sw"]["model"]
    spline_order = i["advanced"]["model_spline_order"]
    mod = model.built_in(m, spline_order=spline_order) \
        if m in model.get_builtin_models() \
        else model.read(m, spline_order=spline_order)

    if write_mesh_to_file:
        output_filename = check_output_filename(output_filename, mod,
                                                overwrite_file, i, sw_mode)

    min_z = sphgrp["min_radius"] * 1e3

    _p = i["basic"]["period"] if not sw_mode else 100.
    discontinuities, hmax = get_discontinuities_hmax(
        mod, _p, i["advanced"]["elements_per_wavelength"], min_z, mode)

    if sw_mode:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    # The refinement style depends on the dimension.
    rfg = i["refinement"] if 'refinement' in i else i["refinement3D"]

    if "chunk3D" in i:
        raise ValueError('This feature is not included in the free SalvusMesher version.')
    elif "chunk2D" in i:
        max_colat = np.array([i["chunk2D"]["max_colatitude"]])
    else:
        max_colat = None

    full_sphere = max_colat is None or np.all(max_colat == 180.0)
    inner_core = min_z == 0.0 and full_sphere

    if sw_mode and not add_exterior_mesh:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if is_axisem:
        min_colat = None
    else:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    anisotropic_refinement = "topography" in i and \
        not i["topography"]["anisotropic_refinement_style"] == 'none'

    if anisotropic_refinement and mod.moho_idx > 1:
        raise ValueError('Anisotropic refinement only works with single layer '
                         'crust in the 1D reference model')

    if anisotropic_refinement and add_ocean:
        if i["topography"]["anisotropic_refinement_style"] == 'doubling' \
           and i["ocean"]["ocean_layer_style"].startswith('anisotropic'):
            raise ValueError(
                'anisotropic_refinement_style "doubling" not compatible with '
                'ocean_layer_style "anisotropic_doubling" or '
                '"anisotropic_tripling"')

    if sw_mode:
        raise ValueError('This feature is not included in the free SalvusMesher version.')
    else:
        nelem_vertical = None
        max_nrefine = None

    if add_exterior_mesh:
        raise ValueError('This feature is not included in the free SalvusMesher version.')
    else:
        nelem_bottom_integer_multiple = None

    # create the skeleton
    if verbose:
        print('Creating the skeleton...')

    sk, sk_info = Skeleton.create_spherical_mesh(
        discontinuities, hmax, ndim, hmax_refinement=rfg["hmax_refinement"],
        max_colat=max_colat, min_colat=min_colat, axisem=is_axisem,
        full_sphere=full_sphere, inner_core=inner_core,
        refinement_style=rfg['refinement_style'],
        refinement_top_down=(not rfg["refinement_bottom_up"]),
        exclude_top_n_regions=int(anisotropic_refinement),
        return_info_dict=True,
        nelem_bottom_integer_multiple=nelem_bottom_integer_multiple,
        nelem_vertical=nelem_vertical, max_nrefine=max_nrefine)

    if "chunk3D" in i:
        raise ValueError('This feature is not included in the free SalvusMesher version.')
    elif ndim == 3:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if verbose:
        print('NEX: ', sk_info['nelem_top'])

    # load topography data
    if "topography" in i and i["topography"]["topography_file"]:
        raise ValueError('This feature is not included in the free SalvusMesher version.')
    else:
        surface_topo = None

    # load moho topography data
    if "topography" in i and i["topography"]["moho_topography_file"]:
        raise ValueError('This feature is not included in the free SalvusMesher version.')
    else:
        moho_topo = None

    if add_ocean or add_ocean_loading:
        raise ValueError('This feature is not included in the free SalvusMesher version.')
    else:
        bathymetry = None

    if anisotropic_refinement:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if add_exterior_mesh:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if add_ocean and 'anisotropic' in i["ocean"]["ocean_layer_style"]:

        raise ValueError('This feature is not included in the free SalvusMesher version.')

    # create the unstructured mesh
    if verbose:
        print('Creating the unstructured mesh...')

    m = sk.get_unstructured_mesh(scale=mod.scale)

    # add ocean by extruding the surface
    if add_ocean and i["ocean"]["ocean_layer_style"] == 'extrude':
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if add_ocean and i["ocean"]["refine_at_ocean_bottom"]:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if mesh_processing_callback is not None:
        mesh_processing_callback(m)

    # Figure out if a point cloud to mask the mesh is available.
    if "mesh_mask" in inputs and inputs["mesh_mask"]["filename"]:
        raise ValueError('This feature is not included in the free SalvusMesher version.')
    else:
        apply_mesh_mask = False

    # Conserve memory.
    del sk
    if anisotropic_refinement:
        raise ValueError('This feature is not included in the free SalvusMesher version.')
    if add_exterior_mesh:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if generate_plots:
        m.plot(show=False)
        m.plot_quality(quality_measure='equiangular_skewness')

    if i["advanced"]["simplex"]:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    # find outer boundaries
    if is_axisem and full_sphere:
        side_set_mode = 'spherical_full_axisem'
    else:
        full_str = {True: '_full', False: '_chunk_z'}
        side_set_mode = mode + full_str[full_sphere]

    m.find_side_sets(side_set_mode)

    if is_axisem and len(mod.get_solid_fluid_boundaries()) > 0:
        def distance(points):
            r = (points ** 2).sum(axis=1) ** 0.5
            sfb = mod.get_solid_fluid_boundaries()
            sfb = sfb.reshape((len(sfb), 1))
            buff = np.abs(
                np.tile(r, (sfb.size, 1)) - np.tile(sfb, (1, len(r))))
            return np.min(buff, axis=0)

        m.find_side_sets_generic('solid_fluid_boundary', distance)

    if add_ocean:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    # Fix side sets in case the mesh has been masked.
    if apply_mesh_mask:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if inner_core and 'r0' in m.side_sets:
        # for uneven nex, r0 is set even if the inner core is present
        m.side_sets.pop('r0')

    if add_exterior_mesh:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    # Rotate spherical chunk mesh.
    if "chunk3D" in i:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    # Add ellipticity.
    if "spherical" in i:
        if (i["spherical"]["ellipticity"] > 0. or i["spherical"]["gravity"]) \
           and not is_axisem:
            raise ValueError('This feature is not included in the free SalvusMesher version.')

    if ndim == 3 and i["spherical"]["ellipticity"] > 0. and not is_axisem:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if is_axisem:
        # ellipticity for AxiSEM
        # NOTE: For AxiSEM, the mesh cannot be stretched directly; instead,
        # it handles ellipticity by means of "particle relabelling". Here
        # we only need to dump the solution of the Clairaut equation.
        # always do this even without --add_ellipticity
        if verbose:
            print('computing ellipticity for axisem')
        # surface flattening will be specified in solver
        mod.compute_ellipticity(epsilon_surf=1.0)
        # make knots and coeffs the same length
        nknots = mod.ellipticity_fct.get_knots().shape[0] * 2
        knots = np.arange(nknots, dtype='float') / (nknots - 1)
        coeffs = mod.ellipticity_fct(knots)
        m.attach_global_variable('ellipticity', np.vstack((knots, coeffs)))

    topo_names = []
    if "topography" in i and i["topography"]["topography_file"]:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    # add moho topography
    if "topography" in i and i["topography"]["moho_topography_file"]:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    # add bathymetry
    if add_ocean:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    z_centroid_spherical = (m.get_element_centroid() ** 2).sum(axis=1) ** 0.5
    z_node_spherical = (m.points ** 2).sum(axis=1) ** 0.5

    # topography and moho topography
    if topo_names:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if add_ocean:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if add_ocean or add_ocean_loading:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    m.attach_field('hmin', m._hmin() * mod.scale)

    # attach elastic parameters
    if verbose:
        print('attaching elastic parameters')

    z_centroid = (m.get_element_centroid() ** 2).sum(axis=1) ** 0.5
    z_node = (m.points ** 2).sum(axis=1) ** 0.5

    attach_model_parameters(i, mod, m, discontinuities, generate_plots, z_node,
                            z_centroid, verbose, is_axisem,
                            z_centroid_spherical, z_node_spherical,
                            add_ocean=add_ocean, r_ocean_ref=R_OCEAN_REF)

    m.attach_global_variable('reference_frame', 'spherical')

    # add ellipticity
    if ndim == 3 and i["spherical"]["ellipticity"] > 0. and not is_axisem:
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    if verbose:
        print('Computing mesh quality...')
    cn, p_min, p_min_95p, p_min_max_z, dt, dt_min_z, max_edge_aspect_ratio, \
        max_equiangular_skewness = compute_mesh_quality(
            i, mod, z_centroid, m, mode, z_centroid_spherical,
            add_ocean=add_ocean)

    if ndim == 3:
        raise ValueError('This feature is not included in the free SalvusMesher version.')
    m.attach_global_variable('radius', float(mod.scale))

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