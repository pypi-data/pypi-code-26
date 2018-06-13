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

import getpass
import numpy as np
import os
import platform
import sys
import socket
import textwrap
import warnings

from .. import models_1D
from ..attenuation import LinearSolid


MAX_LINE_LENGTH = 80    # exodus default


def sizeof_fmt(num):
    """
    Handy formatting for human readable filesize.
    From http://stackoverflow.com/a/1094933/1657047
    """
    for x in ["bytes", "KB", "MB", "GB"]:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, "TB")


def check_output_filename(output_filename, mod, overwrite_file, i,
                          sw_mode=False):
    if not sw_mode:
        output_filename = output_filename\
            .replace("$mesh_type$", i["mesh_type"]) \
            .replace("$model_name$", mod.name)\
            .replace("$period$", str(int(i["basic"]["period"])))
    else:
        lmax = np.max(i["basic_sw"]["lmax_at_discontinuities"])
        output_filename = output_filename\
            .replace("$mesh_type$", i["mesh_type"]) \
            .replace("$model_name$", mod.name)\
            .replace("$period$", str(lmax))

    if not overwrite_file and os.path.exists(output_filename):
        raise ValueError("File '%s' already exists and overwriting is turned"
                         "off." % (output_filename))
    return output_filename


def get_discontinuities_hmax(mod, dominant_period=100.,
                             elements_per_wavelength=2, min_z=0,
                             mode='spherical'):
    if not 0. <= min_z / mod.scale < 1.:
        raise ValueError('min_z should be in [0, planet radius)')

    hmax = mod.get_edgelengths(dominant_period, elements_per_wavelength)

    idx = mod.discontinuities > min_z / mod.scale
    ndisc = idx.sum() + 2

    discontinuities_new = np.zeros(ndisc)
    discontinuities_new[1] = min_z / mod.scale
    discontinuities_new[-ndisc + 2:] = mod.discontinuities[idx]

    hmax_new = np.ones(ndisc - 1)
    hmax_new[-ndisc + 2:] = hmax[-ndisc + 2:]

    if not min_z == 0.0 and mode == 'spherical':
        discontinuities = discontinuities_new[:]
        hmax = hmax_new[:]
    else:
        discontinuities = discontinuities_new[1:]
        hmax = hmax_new[1:]

    # if no inner core, add a fake one to make sure the mesh has the inner cube
    if min_z == 0.0 and mode == 'spherical' and len(discontinuities) == 2:
        discontinuities_new = np.zeros(3)
        discontinuities_new[[0, 2]] = discontinuities
        discontinuities_new[1] = 0.15
        discontinuities = discontinuities_new
        hmax = np.ones(2) * hmax[0]

    return discontinuities, hmax


def attach_model_parameters(i, mod, m, discontinuities, generate_plots, z_node,
                            z_centroid, verbose, is_axisem=False,
                            z_centroid_1D=None, z_node_1D=None,
                            add_ocean=False, r_ocean_ref=None):

    if z_centroid_1D is None:
        z_centroid_1D = z_centroid
    if z_node_1D is None:
        z_node_1D = z_node

    region = mod._get_region(z_centroid_1D, raise_outside=False)

    parameters = i["advanced"]["model_parameters"] or \
        mod.available_elastic_parameters

    if "spherical" in i and i["spherical"]["gravity"]:
            parameters += ['g', 'dg']

    if i["advanced"]["velocity_model_representation"] == "element_nodes":
        masks = mod._get_region_masks(region)
        for _i in np.arange(m.nodes_per_element):
            z_i = z_node[m.connectivity[:, _i]]
            values = mod.get_elastic_parameter_list(
                parameters, z_i, region=region, masks=masks)

            for param in parameters:
                m.attach_field('%s_%d' % (param, _i), values[param])
        del masks

    elif i["advanced"]["velocity_model_representation"] == "elements":
        values = mod.get_elastic_parameter_list(parameters, z_centroid,
                                                region=region)
        for param in parameters:
            m.attach_field(param, values[param])

    elif i["advanced"]["velocity_model_representation"] == "nodes":
        if len(discontinuities) > 2:
            warnings.warn('nodal velocity model is continuous: using mean '
                          'values at discontinuities.')
        # average field at discontinuities (using the mean for now)
        # making sure not to evaluate outside the actual model
        eps = 1e-10
        z1 = discontinuities[0] + eps
        z2 = discontinuities[-1] - eps
        z_node_1D_1 = np.clip(z_node_1D - eps, z1, z2)
        z_node_1D_2 = np.clip(z_node_1D + eps, z1, z2)
        values1 = mod.get_elastic_parameter_list(parameters, z_node,
                                                 z_node_1D_1)
        values2 = mod.get_elastic_parameter_list(parameters, z_node,
                                                 z_node_1D_2)
        for param in parameters:
            m.attach_field(param, (values1[param] + values2[param]) / 2.)
        del values1
        del values2
    else:
        raise NotImplementedError

    if 'gravity_mesh' in i and i["gravity_mesh"]["add_exterior_domain"]:
        m.attach_field('external', (z_centroid_1D > 1.).astype('float'))
        m.attach_field('fluid',
                       mod.get_is_fluid(z_centroid_1D).astype('float'))
    elif add_ocean:
        fluid_mask = mod.get_is_fluid(z_centroid_1D) + (z_centroid_1D > 1.)
        m.attach_field('fluid', fluid_mask.astype('float'))
    else:
        m.attach_field('fluid',
                       mod.get_is_fluid(z_centroid_1D).astype('float'))

    # adding ocean parameters
    if add_ocean:

        ocean_mask = np.logical_and(
            z_centroid_1D > discontinuities[-1],
            z_centroid_1D < r_ocean_ref)

        vp_parameters = models_1D.VP_MAP[mod.anisotropic]

        if i["advanced"]["velocity_model_representation"] == "element_nodes":
            for _i in np.arange(m.nodes_per_element):
                for param in vp_parameters:
                    m.elemental_fields['%s_%d' % (param, _i)][ocean_mask] = \
                        i["ocean"]["ocean_layer_vp"]
                m.elemental_fields['RHO_%d' % _i][ocean_mask] = \
                    i["ocean"]["ocean_layer_density"]

        elif i["advanced"]["velocity_model_representation"] == "elements":

            for param in vp_parameters:
                m.elemental_fields[param][ocean_mask] = \
                    i["ocean"]["ocean_layer_vp"]
            m.elemental_fields['RHO'][ocean_mask] = \
                i["ocean"]["ocean_layer_density"]

        else:
            raise ValueError('ocean does not work with '
                             'velocity_model_representation "nodes"')

    if 'attenuation' in i and mod.anelastic and ('QMU' in parameters or
                                                 'QKAPPA' in parameters):
        if verbose:
            print('attaching attenuation parameters')

        if i["attenuation"]["auto_band"]:
            vmin = mod.get_vmin(z_centroid, scaled=False, region=region)
            f_max = 2 * m.compute_resolved_frequency(
                vmin, i["advanced"]["elements_per_wavelength"])[0]
            f_min = f_max / \
                10 ** LinearSolid.optimal_bandwidth(
                    i["attenuation"]["number_of_linear_solids"])
            if verbose:
                print('auto determined min/max period in s = %.1f, %.1f' % (
                    1 / f_max, 1 / f_min))
        else:
            f_min, f_max = i["attenuation"]["frequencies"]

        ls = LinearSolid.invert_linear_solids(
            Q=1., f_min=f_min, f_max=f_max,
            N=i["attenuation"]["number_of_linear_solids"],
            nfsamp=100, maxiter=1000, fixfreq=False, freq_weight=True,
            pl_f_ref=i["attenuation"]["power_law_reference_frequency"],
            alpha=i["attenuation"]["power_law_alpha"],
            ftol=1e-10)

        # attach freqeuncies
        m.attach_global_variable('f_min', float(f_min))
        m.attach_global_variable('f_max', float(f_max))
        m.attach_global_variable('f_ref', float(mod.fref))

        m.attach_global_variable(
            'nr_lin_solids',
            float(i["attenuation"]["number_of_linear_solids"]))
        for j in np.arange(i["attenuation"]["number_of_linear_solids"]):
            m.attach_global_variable('y_%d' % (j,), float(ls.y_j[j]))
        for j in np.arange(i["attenuation"]["number_of_linear_solids"]):
            m.attach_global_variable('w_%d' % (j,), float(ls.w_j[j]))

        if generate_plots:
            ls.plot()


def compute_mesh_quality(i, mod, z_centroid, m, mode, z_centroid_1D=None,
                         add_ocean=False):
    if z_centroid_1D is None:
        z_centroid_1D = z_centroid

    region = mod._get_region(z_centroid_1D, raise_outside=False)

    vp = mod.get_vpmax(z_centroid, scaled=False, region=region)
    vp[region == -1] = i["ocean"]["ocean_layer_vp"] / mod.scale if add_ocean \
        else np.inf
    m.attach_field('vp_dt', vp)
    cn = i["advanced"]["courant_number"]
    dt, dt_elem = m.compute_dt(vp, cn)
    # TODO sort this out in case there is a gravity mesh
    if not add_ocean:
        dt = float(np.min(dt_elem[region >= 0]))
    dt_min_z = z_centroid[np.argmin(dt_elem[region >= 0])]

    m.attach_global_variable('dt', dt)
    m.attach_field('dt', dt_elem)  # this is mainly for visualization

    m.attach_global_variable('model', mod.name)
    m.attach_global_variable('crdsys', mode)

    # store commandline that was used to create this mesh
    cmdl = 'python -m salvus_mesher_lite.interface ' + ' '.join(sys.argv[1:])
    # need to wrap it in case it is too long
    cmdll = textwrap.wrap(cmdl, MAX_LINE_LENGTH - 10)
    for _i, cmdl in enumerate(cmdll):
        m.attach_global_variable('cmdl %d' % (_i,), cmdl)

    # store input parameters
    # need to wrap it in case it is too long
    cmdll = textwrap.wrap(str(i).replace("'", ""), MAX_LINE_LENGTH - 10)
    for _i, cmdl in enumerate(cmdll):
        m.attach_global_variable('istr %d' % (_i,), cmdl)

    # store host, username and python version
    m.attach_global_variable('host', socket.gethostname())
    m.attach_global_variable('user', getpass.getuser())
    m.attach_global_variable('python version', platform.python_version())

    ear = m.compute_mesh_quality(quality_measure='edge_aspect_ratio')
    max_edge_aspect_ratio = np.max(ear)
    m.attach_field('edge_aspect_ratio', ear)

    es = m.compute_mesh_quality(quality_measure='equiangular_skewness')
    max_equiangular_skewness = np.max(es)
    m.attach_field('equiangular_skewness', es)

    vmin = mod.get_vmin(z_centroid, scaled=False, region=region)
    vmin[region == -1] = i["ocean"]["ocean_layer_vp"] / mod.scale \
        if add_ocean else np.inf
    p_min, p_min_elem = m.compute_resolved_frequency(
        vmin, i["advanced"]["elements_per_wavelength"])
    p_min = 1. / p_min
    p_min_elem = 1. / p_min_elem
    p_min_max_z = z_centroid[np.argmax(p_min_elem)]
    p_min_95p = np.percentile(p_min_elem, 95.)

    m.attach_global_variable('minimum_period', p_min)
    m.attach_field('minimum_period', p_min_elem)

    return cn, p_min, p_min_95p, p_min_max_z, dt, dt_min_z, \
        max_edge_aspect_ratio, max_equiangular_skewness


def print_mesh_info(i, mod, cn, p_min, p_min_95p, p_min_max_z, dt, dt_min_z, m,
                    max_edge_aspect_ratio, max_equiangular_skewness, runtime,
                    output_filename):
    info = [
        '=' * 78,
        'SUMMARY OF MESH PROPERTIES:',
        '',
        '  model name                       | %9s' % mod.name,
        '  dominant period input            | %9.2f s' %
        i["basic"]["period"] if "basic" in i else 'None',
        '  elements per wavelength          | %9.2f' %
        i["advanced"]["elements_per_wavelength"],
        '  Courant Number                   | %9.2f' % cn,
        '',
        '  resolved period (global max)     | %9.2f s' % p_min,
        '    location (z coordinate)        | %9.2f km' %
        (p_min_max_z * m.scale / 1e3),
        '  resolved period (percentile 95)  | %9.2f s' % p_min_95p,
        '  time step dt                     | %9.4f s' % dt,
        '    location (z coordinate)        | %9.2f km' %
        (dt_min_z * m.scale / 1e3),
        '  number of elements               | %9d' % m.nelem,
        '  number of points                 | %9d' % m.npoint,
        '  cost factor (nelem / dt)         |  %.2e' % (m.nelem / dt),
        '',
        '  max edge aspect ratio            | %9.2f' % max_edge_aspect_ratio,
        '  max equiangular skewness         | %9.2f' %
        max_equiangular_skewness,
        '=' * 78]

    info.append('GLOBAL VARIABLES:')
    for s in sorted(m.global_variables.items(), key=lambda x: x[0]):
        info.append('  %-27s| %9.5f' % s)
    info.append('=' * 78)

    info.append('ELEMENTAL FIELDS:')
    for s in sorted(m.elemental_fields.keys()):
        info.append('  %s' % s)
    info.append('=' * 78)

    info.append('NODAL FIELDS:')
    for s in sorted(m.nodal_fields.keys()):
        info.append('  %s' % s)
    info.append('=' * 78)

    info.append('SIDE SETS:')
    for s in sorted(m.side_sets.keys()):
        info.append('  %s' % s)
    info.append('=' * 78)

    info_str = '\n'.join(info)
    print(info_str)

    print("\nSUCCESSFULLY GENERATED MESH IN %g SECONDS." % runtime)

    if output_filename is not None:
        print("SAVED TO '%s' (%s)." % (
            output_filename, sizeof_fmt(os.path.getsize(output_filename))))


def get_dem(i, scale, lmax, fname, min_phi=None, max_phi=None, min_theta=None,
            max_theta=None):
    raise ValueError('This feature is not included in the free SalvusMesher version.')


def build_exterior_mesh(ncoarse, nelem_buffer, nelem_to_DBC, dr_basis,
                        nelem_top, refinement_factor,
                        buffer_layer_dr_fac=None, chunk=False, max_colat=None):
    raise ValueError('This feature is not included in the free SalvusMesher version.')


def mask_mesh(m, point_cloud, distance_in_km, surface=True):
    raise ValueError('This feature is not included in the free SalvusMesher version.')