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
import copy
import glob
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial.polynomial import Polynomial
import inspect
import os
from scipy.integrate import ode, cumtrapz, quad
from scipy.interpolate import InterpolatedUnivariateSpline
import warnings


# Most generic way to get the data directory.
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe()))), "data")

ELASTIC_PARAMETER_MAP = {
    (False, False): ['VP', 'VS', 'RHO'],
    (False, True): ['VP', 'VS', 'RHO', 'QMU', 'QKAPPA'],
    (True, False): ['VPV', 'VPH', 'VSV', 'VSH', 'ETA', 'RHO'],
    (True, True): ['VPV', 'VPH', 'VSV', 'VSH', 'ETA', 'RHO', 'QMU',
                   'QKAPPA']}

VELOCITY_MAP = {
    False: ['VP', 'VS'],
    True: ['VPV', 'VPH', 'VSV', 'VSH']}

VS_MAP = {
    False: ['VS'],
    True: ['VSV', 'VSH']}

VP_MAP = {
    False: ['VP'],
    True: ['VPV', 'VPH']}

SI_FACTOR = {'m': 1, 'km': 1000}

ELLIPSOIDS = {'GRS80': 1. / 298.257222101,
              'WGS84': 1. / 298.257223563,
              'MARS': 0.00589}

# https://www.physicsforums.com/threads/planets-and-suns-mean-angular-velocity.460887/  # NoQa
OMEGA = {'EARTH': 7.292115053925690e-05,
         'JUPITER': 1.773408215404907e-04,
         'MARS': 7.088218127178316e-05,
         'MERCURY': 1.240013441242619e-06,
         'MOON': 2.661699538941653e-06,
         'NEPTUNE': 1.083382527619075e-04,
         'PLUTO': -1.295641039282477e-05,
         'SATURN': 1.636246173744684e-04,
         'SUN': 2.865329607243705e-06,
         'URANUS': -1.041365902144588e-04}

GRAVITY_G = 6.67408e-11


def str2bool(s):
    """
    convert string to bool
    """
    return s.lower() in ['t', 'true', '1', 'y', 'yes']


class ConstInterpolator(object):

    def __init__(self, const):
        self.const = const

    def __call__(self, x):
        return np.ones(x.shape) * self.const


class model(object):
    """
    A class to handle the 1D background models
    """

    def __init__(self, name, model_type, anelastic, anisotropic, nregions,
                 discontinuities, is_fluid, elastic_parameters_fct, scale,
                 fref=1., moho_idx=None, moho_comp_idx=None):
        self.name = name
        self.model_type = model_type
        self.anelastic = anelastic
        self.anisotropic = anisotropic
        self.nregions = nregions
        self.discontinuities = discontinuities
        self.is_fluid = is_fluid
        self.elastic_parameters_fct = elastic_parameters_fct
        self.scale = scale
        self.fref = fref
        self.moho_idx = moho_idx
        self.moho_comp_idx = moho_comp_idx

        self.fluid_regions = np.where(is_fluid)[0]
        self.ellipticity_fct = None
        self.gravity_fct = None
        self.norms = None

    @property
    def available_elastic_parameters(self):
        return copy.deepcopy(
            ELASTIC_PARAMETER_MAP[(self.anisotropic, self.anelastic)])

    @staticmethod
    def get_builtin_models():
        """
        Get a list of builtin models that can be loaded by model name only.
        """
        model_files = glob.glob(os.path.join(DATA_DIR, "*.bm"))
        models = [os.path.split(m)[1].split('.')[0] for m in model_files]
        return models

    @classmethod
    def read(self, file_name, **kwargs):
        """
        A wrapper around the built_in() and external() constructors, determines
        the model type automatically

        :param file_name: path to the model file
        :type file_name: string
        """
        lines = _read_file(file_name)

        # check for some keywords that have to be in the polynomial or layered
        # files
        deck = (_get_value(lines, 'COLUMNS', default='__') == '__' and
                _get_value(lines, 'DISCONTINUITIES', default='__') == '__')
        model_type = 'deck' if deck else _get_value(lines, 'MODEL_TYPE',
                                                    default='layered')

        if model_type == 'poly':
            return self.polynomial(file_name, lines=lines, **kwargs)
        elif model_type == 'layered':
            return self.layered(file_name, lines=lines, **kwargs)
        elif model_type == 'deck':
            return self.deck(file_name, lines=lines, **kwargs)
        else:
            raise IOError('File format not recognized')

    @classmethod
    def built_in(self, model_name, fluid_tolerance=1e-10, **kwargs):
        """
        Create a 1D model from the predefined models. Call get_builtin_models()
        to find out which ones are available.

        :param model_name: name of the model
        :type model_name: string
        :param fluid_tolerance: maximum absolute value for the scaled vs to
            detect fluid
        :type fluid_tolerance: float
        """
        file_name = os.path.join(DATA_DIR, '%s.bm' % (model_name,))
        return self.read(file_name, fluid_tolerance=fluid_tolerance, **kwargs)

    @classmethod
    def polynomial(self, file_name, fluid_tolerance=1e-10, lines=None,
                   **kwargs):
        """
        Create a 1D model from a polynomial model file, somewhat similar to the
        MINEOS polynomial models, but different file format.

        :param file_name: the model file
        :type file_name: string
        :param fluid_tolerance: maximum absolute value for the scaled vs to
            detect fluid
        :type fluid_tolerance: float
        """
        if lines is None:
            lines = _read_file(file_name)

        # parse the keywords
        name = _get_value(lines, 'NAME')
        model_type = _get_value(lines, 'MODEL_TYPE')

        if not model_type == 'poly':  # pragma: no cover
            raise ValueError()

        fref = _get_value(lines, 'REFERENCE_FREQUENCY', float, default=1.)
        units = _get_value(lines, 'UNITS', default='km')

        anelastic = _get_value(lines, 'ANELASTIC', str2bool, default=False)
        anisotropic = _get_value(lines, 'ANISOTROPIC', str2bool, default=False)
        nregions = _get_value(lines, 'NREGIONS', int)
        discontinuities = np.array(
            _get_values(lines, 'DISCONTINUITIES', float), dtype='float')
        moho_idx = _get_value(lines, 'MOHO_IDX', int, default=1)
        moho_comp_idx = _get_value(lines, 'MOHO_COMP_IDX', int,
                                   default=moho_idx+1)
        max_poly_deg = _get_value(lines, 'MAX_POLY_DEG', int, default=3)
        scale = _get_value(lines, 'SCALE', float,
                           default=discontinuities.max())

        # scale to SI and radius = 1
        scale *= SI_FACTOR[units]
        discontinuities *= SI_FACTOR[units] / scale

        # make sure we start from the bottom
        resort = np.any(discontinuities != sorted(discontinuities))
        if resort:
            discontinuities.sort()

        if len(discontinuities) != nregions + 1:  # pragma: no cover
            raise ValueError(
                'NREGIONS and length of DISCONTINUITIES not compatible')

        discontinuities[0] = 0.
        discontinuities[-1] = 1.

        # parse elastic paramters
        elastic_parameters = {}
        for param in ELASTIC_PARAMETER_MAP[(anisotropic, anelastic)]:

            values = _get_values_ml(lines, param, nregions, float)

            if True in [len(v) > max_poly_deg + 1 for v in values]:
                raise ValueError(
                    'more coefficients than MAX_POLY_DEG for parameter %s' %
                    (param,))  # pragma: no cover

            if resort:
                values = values[::-1]

            if param not in ['QMU', 'QKAPPA', 'ETA']:
                # convert to SI and scale
                for i in range(nregions):
                    values[i] = np.array(values[i]) * SI_FACTOR[units] / scale
            elastic_parameters[param] = values

        # find the fluid regions
        is_fluid = np.zeros(nregions, dtype='bool')
        for vs in VS_MAP[anisotropic]:
            for iregion in range(nregions):
                is_fluid[iregion] = is_fluid[iregion] or (
                    len(elastic_parameters[vs][iregion]) == 1 and
                    abs(elastic_parameters[vs][iregion][0]) < fluid_tolerance)

        # setup the callable functions for elastic parameters
        elastic_parameters_fct = {}
        for param in ELASTIC_PARAMETER_MAP[(anisotropic, anelastic)]:
            elastic_parameters_fct[param] = []
            for iregion in range(nregions):
                elastic_parameters_fct[param].append(Polynomial(
                    elastic_parameters[param][iregion]))

        # initialize the model
        return self(name, model_type, anelastic, anisotropic, nregions,
                    discontinuities, is_fluid, elastic_parameters_fct, scale,
                    fref=fref, moho_idx=moho_idx, moho_comp_idx=moho_comp_idx)

    @classmethod
    def layered(self, file_name, disc_tolerance=1e-10, fluid_tolerance=1e-10,
                spline_order=3, lines=None):
        """
        Create a 1D model from a layered model file as introduced with AxiSEM
        1.2.

        :param file_name: the model file
        :type file_name: string
        :param disc_tolerance: maximum absolute value for detecting two layers
            as the same depth (after scaling).
        :type disc_tolerance: float
        :param fluid_tolerance: maximum absolute value for the scaled vs to
            detect fluid
        :type fluid_tolerance: float
        :param spline_order: maximum order of the spline interpolation. In
            regions with few layers the order will be adapted to nlayer - 1,
            i.e. for two nodes the interolation is linear.
        :type spline_order: int
        """
        if lines is None:
            lines = _read_file(file_name)

        # parse the keywords
        name = _get_value(lines, 'NAME', default=file_name.split('.')[0])
        model_type = _get_value(lines, 'MODEL_TYPE', default='layered')

        if not model_type == 'layered':  # pragma: no cover
            raise ValueError()

        fref = _get_value(lines, 'REFERENCE_FREQUENCY', float, default=1.)
        units = _get_value(lines, 'UNITS', default='km')

        anelastic = _get_value(lines, 'ANELASTIC', str2bool, default=False)
        anisotropic = _get_value(lines, 'ANISOTROPIC', str2bool, default=False)

        moho_idx = _get_value(lines, 'MOHO_IDX', int, default=1)
        moho_comp_idx = _get_value(lines, 'MOHO_COMP_IDX', int,
                                   default=moho_idx+1)

        columns = _get_values(lines, 'COLUMNS')
        columns = [c.upper() for c in columns]

        # some checks:
        if ('RADIUS' in columns) == ('DEPTH' in columns):  # pragma: no cover
            raise ValueError('need either depth or radius')

        for i in range(len(columns)):
            if columns[i] == 'QKA':
                columns[i] = 'QKAPPA'

        elastic_columns = [c for c in columns if c not in ['RADIUS', 'DEPTH']]
        if not sorted(ELASTIC_PARAMETER_MAP[(anisotropic, anelastic)]) == \
                sorted(elastic_columns):  # pragma: no cover
            raise ValueError(
                'column headers not compatibel with ANISOTROPIC and ANELASTIC')

        # assuming the data block to be read is indented by at least two spaces
        values = np.array(
            _get_values_ml(lines, 'COLUMNS', n=None, cast_function=float))

        # convert depth to radius
        if 'DEPTH' in columns:
            idx = columns.index('DEPTH')
            values[:, idx] = values[:, idx].max() - values[:, idx]
            columns[idx] = 'RADIUS'

        # make sure to start from the center
        idx_radius = columns.index('RADIUS')
        if values[-1, idx_radius] < values[0, idx_radius]:
            values = values[::-1, :]

        scale = values[-1, idx_radius]

        radii, idx_region, nregions, discontinuities = _find_discontinuities(
            values, idx_radius, scale, disc_tolerance)

        is_fluid = _find_fluid_regions(nregions, anisotropic, columns,
                                       idx_region, values, fluid_tolerance)

        elastic_parameters_fct = _setup_callables_spline(
            anisotropic, anelastic, values, columns, scale, nregions,
            idx_region, spline_order, radii)

        scale *= SI_FACTOR[units]

        # initialize the model
        return self(name, model_type, anelastic, anisotropic, nregions,
                    discontinuities, is_fluid, elastic_parameters_fct, scale,
                    fref=fref, moho_idx=moho_idx, moho_comp_idx=moho_comp_idx)

    @classmethod
    def deck(self, file_name, disc_tolerance=1e-10, fluid_tolerance=1e-10,
             spline_order=3, lines=None):
        """
        Create a 1D model from a 'deck' file format as used by Mineos and in
        the insight Science Team. Anisotropic files only.

        :param file_name: the model file
        :type file_name: string
        :param disc_tolerance: maximum absolute value for detecting two layers
            as the same depth (after scaling).
        :type disc_tolerance: float
        :param fluid_tolerance: maximum absolute value for the scaled vs to
            detect fluid
        :type fluid_tolerance: float
        :param spline_order: maximum order of the spline interpolation. In
            regions with few layers the order will be adapted to nlayer - 1,
            i.e. for two nodes the interolation is linear.
        :type spline_order: int
        """
        if lines is None:
            lines = _read_file(file_name)

        # parse the keywords
        name = lines[0].strip()

        anisotropic, fref, ifdeck = lines[1].split()

        model_type = 'deck'
        anelastic = True
        anisotropic = bool(anisotropic)
        ifdeck = bool(ifdeck)
        fref = float(fref)

        if not ifdeck:
            raise IOError('deck format files only')

        if not anisotropic:
            raise NotImplementedError('for now only anisotropic models')

        N, nic, noc = list(map(int, lines[2].split()[:3]))

        columns = ['RADIUS', 'RHO', 'VPV', 'VSV', 'QKAPPA', 'QMU', 'VPH',
                   'VSH', 'ETA']

        # some checks:
        if nic > noc:
            raise ValueError('nic > noc')

        idx_radius = 0
        values = np.array([l.split() for l in lines[3:]], dtype='float')

        scale = values[-1, idx_radius]

        radii, idx_region, nregions, discontinuities = _find_discontinuities(
            values, idx_radius, scale, disc_tolerance)

        is_fluid = _find_fluid_regions(nregions, anisotropic, columns,
                                       idx_region, values, fluid_tolerance)

        elastic_parameters_fct = _setup_callables_spline(
            anisotropic, anelastic, values, columns, scale, nregions,
            idx_region, spline_order, radii)

        try:
            nmoho = int(lines[2].split()[3])
            moho_idx = np.where(np.isclose(
                radii[nmoho-1], discontinuities[::-1], atol=1e-10,
                rtol=1e-10))[0][0]
        except Exception:
            warnings.warn('Moho Index not set in the file, defaulting to the '
                          'first disctontinuity')
            moho_idx = 1
        moho_comp_idx = moho_idx + 1

        # initialize the model
        return self(name, model_type, anelastic, anisotropic, nregions,
                    discontinuities, is_fluid, elastic_parameters_fct, scale,
                    fref=fref, moho_idx=moho_idx, moho_comp_idx=moho_comp_idx)

    def get_edgelengths(self, dominant_period=50., elements_per_wavelength=2.,
                        nsamp_min=100):
        """
        get maximum edge lengths ('hmax')

        :param dominant_period: dominant period to be propagated through the
            mesh in seconds
        :type dominant_period: float
        :param elements_per_wavelength: element size criterion: how many
            elements per dominant wavelength
        :type elements_per_wavelength: float
        :param nsamp_min: how many samples to use for finding the minium
            velocity in each region
        :type nsamp_min: integer
        """
        minimum_velocity = np.ones(self.nregions) * 1e30
        vmin_map = {True: VP_MAP, False: VS_MAP}

        for iregion in range(self.nregions):
            x = np.linspace(self.discontinuities[iregion],
                            self.discontinuities[iregion+1],
                            nsamp_min)
            for vmin in vmin_map[self.is_fluid[iregion]][self.anisotropic]:
                v = self.elastic_parameters_fct[vmin][iregion](x)
                if np.any(v < 0):  # pragma: no cover
                    raise ValueError('Negative Velocity?')
                minimum_velocity[iregion] = min(minimum_velocity[iregion],
                                                np.min(v))

        # compute maximum edge lengths
        maximum_edge_length = \
            minimum_velocity * dominant_period / elements_per_wavelength
        return maximum_edge_length

    def get_radial_mesh(self, dominant_period=50., elements_per_wavelength=2.,
                        nsamp_min=100, rmin=0., rmax=None):

        if rmax is None:
            rmax = self.scale

        # adapt discontinuities and hmax for min_radius
        idx1 = np.argmax(self.discontinuities > rmin / self.scale)
        idx2 = np.argmin(self.discontinuities < rmax / self.scale)
        discontinuities = np.concatenate([[rmin / self.scale],
                                          self.discontinuities[idx1:idx2],
                                          [rmax / self.scale]])

        hmax = self.get_edgelengths(
            dominant_period=dominant_period,
            elements_per_wavelength=elements_per_wavelength,
            nsamp_min=nsamp_min)[idx1-1:idx2]

        layer_thickness = np.diff(discontinuities)
        nelem = np.ceil(layer_thickness / hmax).astype('int')

        h = layer_thickness / nelem

        element_boundaries = np.concatenate(
            [discontinuities[0:1], discontinuities[0] +
             np.cumsum(h.repeat(nelem))])
        return element_boundaries

    def get_fluid_regions(self):
        """
        get inner and outer radius of fluid regions as a list of tuples
        """
        return [(self.discontinuities[iregion],
                 self.discontinuities[iregion+1]) for iregion in
                self.fluid_regions]

    def get_solid_fluid_boundaries(self, rmin=0, rmax=1.):
        """
        get radii of solid-fluid boundaries
        """
        if len(self.fluid_regions) == 0:  # pragma: no cover
            return np.array([])

        _fr = self.fluid_regions

        if len(self.fluid_regions) == 1:
            idx1 = _fr
            idx2 = _fr
        else:
            # some logics to not include fluid-fluid interfaces
            idx1 = np.r_[_fr[0], _fr[1:][np.diff(_fr) > 1]]
            idx2 = np.r_[_fr[:-1][np.diff(_fr) > 1], _fr[-1]]

        # collect upper and lower boundary of each fluid region, excluding
        # bottom and uppermost boundary
        _d = self.discontinuities
        sfb1 = _d[idx1][_d[idx1] > rmin]
        sfb2 = _d[idx2+1][_d[idx2+1] < rmax]

        return np.sort(np.r_[sfb1, sfb2])

    def get_is_fluid(self, radius):
        """
        get a boolean array for fluid regions (True = fluid)

        :param radius: radius
        :type radius: array of float
        """
        is_fluid = np.zeros(radius.shape, dtype='bool')
        for fr in self.get_fluid_regions():
            is_fluid[np.logical_and(radius < fr[1], radius > fr[0])] = True
        return is_fluid

    def get_vpmax(self, radius, scaled=True, region=None):
        """
        get the maximum p-wave velocity as a function of radius

        :param radius: radius at which the velocity should be evaluated
        :type radius: array of float
        """
        if region is None:
            region = np.digitize(radius, self.discontinuities) - 1
        v = np.zeros(radius.shape)
        for iregion in range(self.nregions):
            mask = region == iregion
            for vmax in VP_MAP[self.anisotropic]:
                v[mask] = np.maximum(
                    v[mask],
                    self.elastic_parameters_fct[vmax][iregion](radius[mask]))

        if scaled:
            v *= self.scale
        return v

    def get_vmin(self, radius, scaled=True, region=None):
        """
        get the minimum p- or s-wave velocity as a function of radius

        :param radius: radius at which the velocity should be evaluated
        :type radius: array of float
        """
        if region is None:
            region = np.digitize(radius, self.discontinuities) - 1
        v = np.zeros(radius.shape)
        vmin_map = {False: VS_MAP[self.anisotropic],
                    True: VP_MAP[self.anisotropic]}
        for iregion in range(self.nregions):
            mask = region == iregion
            for vmax in vmin_map[self.is_fluid[iregion]]:
                v[mask] = np.maximum(
                    v[mask],
                    self.elastic_parameters_fct[vmax][iregion](radius[mask]))
        if scaled:
            v *= self.scale
        return v

    def get_rho(self, radius, region=None, scaled=True):
        """
        get the density as a function of radius.

        :param radius: radius at which the density should be evaluated
        :type radius: float
        """
        if region is None:
            region = int(np.digitize(float(radius), self.discontinuities,
                                     right=True) - 1)

        rho = self.elastic_parameters_fct['RHO'][region](radius)

        if scaled:
            rho *= self.scale

        return rho

    def get_native_parameter(self, param, radius, region=None, scaled=True):
        """
        get a native parameter as a function of radius.

        :param param: parameter name
        :type radius: string
        :param radius: radius at which the density should be evaluated
        :type radius: float
        """
        if region is None:
            region = int(np.digitize(float(radius), self.discontinuities,
                                     right=True) - 1)

        p = self.elastic_parameters_fct[param][region](radius)

        if scaled and param not in ['QMU', 'QKAPPA', 'ETA']:
            p *= self.scale

        return p

    def _get_region(self, radius, raise_outside=True):
        region = np.digitize(radius, self.discontinuities, right=True) - 1
        # digitize does not include the lower boundary, so we need to add this
        # here to avoid problems exactly on the boundary
        region[radius == 0.] = 0

        if raise_outside:
            if np.any(region > len(self.discontinuities) - 2) or \
               np.any(region < 0):  # pragma: no cover
                raise ValueError('requesting parameter outside of the model')
        else:
            region[np.logical_or(region < 0,
                                 region > len(self.discontinuities) - 2)] = -1

        return region

    def _get_region_masks(self, region):
        return [region == iregion for iregion in range(self.nregions)]

    def get_elastic_parameter_list(self, parameter_names, radius,
                                   element_centroids=None, scaled=True,
                                   region=None, masks=None):
        """
        get elastic parameter as a function of radius. Same as
        get_elastic_parameter, but optimized for computing a whole list of
        parameters.
        """

        class Memoize:
            # memoization based on values of 'parameter_name' and 'scaled',
            # because 'radius' is to expensive to hash.

            def __init__(self, fn):
                self.fn = fn
                self.memo = {}

            def __call__(self, *args, **kwargs):
                key = (args[0], kwargs.get('scaled', True))
                if key not in self.memo:
                    self.memo[key] = self.fn(*args, **kwargs)
                return self.memo[key]

        get_elastic_parameter_memo = Memoize(self.get_elastic_parameter)

        if region is None:
            region = self._get_region(
                element_centroids if element_centroids is not None else radius)

        if masks is None:
            masks = self._get_region_masks(region)

        values = {}
        for p in parameter_names:
            values[p] = get_elastic_parameter_memo(
                p, radius, element_centroids=element_centroids, scaled=scaled,
                get_elastic_parameter=get_elastic_parameter_memo,
                region=region, masks=masks)
        return values

    def get_elastic_parameter(self, parameter_name, radius,
                              element_centroids=None, scaled=True,
                              get_elastic_parameter=None, region=None,
                              masks=None):
        """
        get elastic parameter as a function of radius

        :param parameter_name: name of the elastic parameter
        :type parameter_name: string
        :param radius: radius at which the velocity should be evaluated
        :type radius: array of float
        :param element_centroids: optionally provide the element centroids
            alongside with the radius to determine the region from which the
            parameter should be evaluated
        :type element_centroids: array of float of same shape as radius
        """
        if get_elastic_parameter is None:
            get_elastic_parameter = self.get_elastic_parameter

        if not self.anisotropic and parameter_name in ['VPH', 'VPV']:
            parameter_name = 'VP'  # pragma: no cover
        elif not self.anisotropic and parameter_name in ['VSH', 'VSV']:
            parameter_name = 'VS'  # pragma: no cover
        elif not self.anisotropic and parameter_name == 'ETA':
            return np.ones(radius.shape)  # pragma: no cover

        if not self.anelastic and parameter_name in ['QMU', 'QKAPPA']:
            return np.ones(radius.shape) * np.inf  # pragma: no cover

        kwargs = {'radius': radius,
                  'element_centroids': element_centroids,
                  'region': region}

        if parameter_name == 'g':
            return self.get_gravity(radius)

        elif parameter_name == 'dg':
            return self.get_gradient_gravity(radius, element_centroids)

        elif parameter_name in ['A', 'C11', 'C22']:
            rho = get_elastic_parameter('RHO', **kwargs)
            vph = get_elastic_parameter('VPH', **kwargs)
            return rho * vph ** 2

        elif parameter_name in ['C', 'C33']:
            rho = get_elastic_parameter('RHO', **kwargs)
            vpv = get_elastic_parameter('VPV', **kwargs)
            return rho * vpv ** 2

        elif parameter_name in ['L', 'C44', 'C55']:
            rho = get_elastic_parameter('RHO', **kwargs)
            vsv = get_elastic_parameter('VSV', **kwargs)
            return rho * vsv ** 2

        elif parameter_name in ['N', 'C66']:
            rho = get_elastic_parameter('RHO', **kwargs)
            vsh = get_elastic_parameter('VSH', **kwargs)
            return rho * vsh ** 2

        elif parameter_name in ['F', 'C13', 'C31', 'C23', 'C32']:
            eta = get_elastic_parameter('ETA', **kwargs)
            a = get_elastic_parameter('A', **kwargs)
            l = get_elastic_parameter('L', **kwargs)  # NoQa
            return eta * (a - 2 * l)

        elif parameter_name in ['C12', 'C21']:
            a = get_elastic_parameter('A', **kwargs)
            n = get_elastic_parameter('N', **kwargs)
            return a - 2 * n

        elif parameter_name in ['C14', 'C41', 'C15', 'C51', 'C16', 'C61',
                                'C24', 'C42', 'C25', 'C52', 'C26', 'C62',
                                'C34', 'C43', 'C35', 'C53', 'C36', 'C63',
                                'C45', 'C54', 'C46', 'C64', 'C56', 'C65']:
            return np.zeros(radius.shape)  # pragma: no cover

        elif parameter_name == 'XI':
            vsh = get_elastic_parameter('VSH', **kwargs)
            vsv = get_elastic_parameter('VSV', **kwargs)
            xi = np.empty_like(vsv)
            sl = vsv > 0
            xi[sl] = vsh[sl] ** 2 / vsv[sl] ** 2
            xi[np.logical_not(sl)] = 1.
            return xi

        elif parameter_name == 'PHI':
            vph = get_elastic_parameter('VPH', **kwargs)
            vpv = get_elastic_parameter('VPV', **kwargs)
            return vpv ** 2 / vph ** 2

        elif parameter_name == 'LAMBDA':
            if self.anisotropic:
                warnings.warn('using Voigt average lambda')
                # Babuska & Cara (1991), p. 190
                # Panning & Nolet (2008), eq B3
                C11 = get_elastic_parameter('C11', **kwargs)
                C33 = get_elastic_parameter('C33', **kwargs)
                C13 = get_elastic_parameter('C13', **kwargs)
                C44 = get_elastic_parameter('C44', **kwargs)
                C66 = get_elastic_parameter('C66', **kwargs)
                return (6 * C11 + C33 + 8 * C13 - 4 * C44 - 10 * C66) / 15.
            else:
                vp = get_elastic_parameter('VP', **kwargs)
                vs = get_elastic_parameter('VS', **kwargs)
                rho = get_elastic_parameter('RHO', **kwargs)
                return rho * (vp ** 2 - 2 * vs ** 2)

        elif parameter_name == 'MU':
            if self.anisotropic:
                warnings.warn('using Voigt average mu')
                # Babuska & Cara (1991), p. 190
                # Panning & Nolet (2008), eq B1
                C11 = get_elastic_parameter('C11', **kwargs)
                C33 = get_elastic_parameter('C33', **kwargs)
                C13 = get_elastic_parameter('C13', **kwargs)
                C44 = get_elastic_parameter('C44', **kwargs)
                C66 = get_elastic_parameter('C66', **kwargs)
                return np.abs(C11 + C33 - 2 * C13 + 6 * C44 + 5 * C66) / 15.
            else:
                vs = get_elastic_parameter('VS', **kwargs)
                rho = get_elastic_parameter('RHO', **kwargs)
                return rho * vs ** 2

        elif parameter_name == 'KAPPA':
            if self.anisotropic:
                warnings.warn('using Voigt average mu')
                # Al-Attar (2007), eq C.7
                C11 = get_elastic_parameter('C11', **kwargs)
                C33 = get_elastic_parameter('C33', **kwargs)
                C13 = get_elastic_parameter('C13', **kwargs)
                C66 = get_elastic_parameter('C66', **kwargs)
                return np.abs(C33 + 4 * C11 - 4 * C66 + 4 * C13) / 9.
            else:
                vs = get_elastic_parameter('VS', **kwargs)
                vp = get_elastic_parameter('VP', **kwargs)
                rho = get_elastic_parameter('RHO', **kwargs)
                return rho * (vp ** 2 - 4. / 3. * vs ** 2)

        elif parameter_name == 'VP' and self.anisotropic:
            warnings.warn('using Voigt average VP')
            mu = get_elastic_parameter('MU', **kwargs)
            lambd = get_elastic_parameter('LAMBDA', **kwargs)
            rho = get_elastic_parameter('RHO', **kwargs)
            return ((lambd + 2 * mu) / rho) ** 0.5

        elif parameter_name == 'VS' and self.anisotropic:
            warnings.warn('using Voigt average VS')
            mu = get_elastic_parameter('MU', **kwargs)
            rho = get_elastic_parameter('RHO', **kwargs)
            return (mu / rho) ** 0.5

        elif parameter_name == 'P1':
            _a = get_elastic_parameter('A', **kwargs)
            _f = get_elastic_parameter('F', **kwargs)
            _c = get_elastic_parameter('C', **kwargs)
            return _a - _f ** 2 * _c

        elif parameter_name == 'P2':
            _c = get_elastic_parameter('C', **kwargs)
            return 1. / _c

        elif parameter_name == 'P3':
            _f = get_elastic_parameter('F', **kwargs)
            _c = get_elastic_parameter('C', **kwargs)
            return _f / _c

        elif parameter_name == 'P4':
            _l = get_elastic_parameter('L', **kwargs)
            return 1. / _l

        elif parameter_name == 'P5':
            _n = get_elastic_parameter('N', **kwargs)
            return _n

        # if we arrive here, it should be a native parameter
        if parameter_name not in self.available_elastic_parameters:
            raise ValueError  # pragma: no cover

        parameter = np.zeros(radius.shape)

        if region is None:
            region = self._get_region(
                element_centroids if element_centroids is not None else radius)

        if masks is None:
            masks = self._get_region_masks(region)

        # evaluate interpolation functions
        for iregion in range(self.nregions):
            parameter[masks[iregion]] = self.elastic_parameters_fct[
                parameter_name][iregion](radius[masks[iregion]])

        if scaled and parameter_name not in ['QMU', 'QKAPPA', 'ETA']:
            parameter *= self.scale

        return parameter

    def compute_ellipticity(self, epsilon_surf='WGS84', nsteps=10000,
                            rtol=1e-15, r_0=1e-10, nsamp_per_layer=100,
                            order=3):

        if type(epsilon_surf) is str:
            epsilon_surf = ELLIPSOIDS[epsilon_surf]

        def clairaut_equation_first_order(r, y):

            epsilon, eta, xi = y
            # xi = g * r ** 2 / (4 * pi * G)
            rho = self.get_rho(r / self.scale)

            depsilon_dr = eta
            deta_dr = 6. / r ** 2 * epsilon - \
                2. * rho * r ** 2 / xi * (eta + epsilon / r)
            dxi_dr = rho * r ** 2

            return [depsilon_dr, deta_dr, dxi_dr]

        # build sampling for interpolating splines and integration
        r = np.concatenate([np.linspace(self.discontinuities[iregion],
                                        self.discontinuities[iregion+1],
                                        nsamp_per_layer, endpoint=False)
                            for iregion in range(self.nregions)])
        r = np.r_[r, np.array([1.])]
        r_in_m = r * self.scale

        # assume homogeneous density within the radius r_0 to get the starting
        # value for xi analytically
        r_0_in_m = self.scale * r_0
        xi_0 = self.get_rho(r_0_in_m) * r_0_in_m ** 3 / 3.

        # the solution is linear in the ellipticity in the center, so
        # 'shooting' as suggested by Dahlen & Tromp 1998 is trivial. Just
        # integrate once with epsilon[0] = 1. and then scale the result so that
        # epsilon[-1] matches the terminal condition (i.e. the ellipticity at
        # the surface).

        nr = len(r)
        epsilon = np.zeros(nr)
        epsilon[0] = 1.
        xi = np.zeros(nr)
        xi[0] = xi_0

        integrator = ode(clairaut_equation_first_order)
        integrator.set_integrator('dopri5', nsteps=nsteps, rtol=rtol)
        integrator.set_initial_value([epsilon[0], 0., xi[0]], r_0_in_m)

        # Do the actual integration, storing the ellipticity and the
        # gravitational potential
        for i in np.arange(nr - 1):
            integrator.integrate(r_in_m[i+1])

            if not integrator.successful():
                raise RuntimeError(
                    "Integration Error while intgrating Clairaut's equation")

            epsilon[i+1], _, xi[i+1] = integrator.y

        # scale to match surface ellipticity
        epsilon_0 = epsilon_surf / epsilon[-1]
        epsilon *= epsilon_0

        # setup an interpolation function (I think epsilon is C1, so this
        # should be fine).
        self.ellipticity_fct = InterpolatedUnivariateSpline(r, epsilon,
                                                            k=order, ext=3)

        gravitaty_acc = xi * 4 * np.pi * GRAVITY_G
        gravitaty_acc[1:] /= (r[1:] * self.scale) ** 2
        # for gravity use linear interpolation, because it is C0
        self.gravity_fct = InterpolatedUnivariateSpline(r, gravitaty_acc, k=1,
                                                        ext=3)

    def get_ellipticity(self, radius, compute_ellipticity_kwargs={}):
        """
        get the ellipticity as a function of radius.

        :param radius: radius at which the density should be evaluated
        :type radius: float
        """
        if self.ellipticity_fct is None:
            self.compute_ellipticity(**compute_ellipticity_kwargs)

        return self.ellipticity_fct(radius)

    def get_gravity(self, radius, compute_ellipticity_kwargs={},
                    get_mass_kwargs={}):
        """
        get the gravity as a function of radius.

        :param radius: radius at which the density should be evaluated
        :type radius: float
        """
        if self.gravity_fct is None:
            self.compute_ellipticity(**compute_ellipticity_kwargs)

        mass = self.get_mass(**get_mass_kwargs)
        g = np.zeros(len(radius))

        sl = radius < 1
        g[sl] = self.gravity_fct(radius[sl])

        sl = np.logical_not(sl)
        g[sl] = GRAVITY_G * mass / (radius[sl] * self.scale) ** 2
        return g

    def get_gravitational_potential(
         self, radius, compute_ellipticity_kwargs={}, get_mass_kwargs={},
         get_ith_moment_radius_kwargs={}):
        """
        get the gravitational potential as a function of radius.

        :param radius: radius at which the density should be evaluated
        :type radius: float
        """
        if self.gravity_fct is None:
            self.compute_ellipticity(**compute_ellipticity_kwargs)

        mass = self.get_mass(**get_mass_kwargs)
        phi = np.zeros(len(radius))

        sl = radius < 1
        phi[sl] = -(radius[sl] * self.scale * self.gravity_fct(radius[sl]) +
                    4 * np.pi * GRAVITY_G * self._get_ith_moment(i=1) -
                    4 * np.pi * GRAVITY_G * self._get_ith_moment_radius(
                        radius[sl], i=1, **get_ith_moment_radius_kwargs))

        sl = np.logical_not(sl)
        phi[sl] = - GRAVITY_G * mass / (radius[sl] * self.scale)
        return phi

    def get_gradient_gravity(self, radius, element_centroids=None, r_0=1e-10,
                             compute_ellipticity_kwargs={}):
        """
        Compute the derivative of the gravitational acceleration, needed for
        the operator H in Komatitsch & Tromp 2002b, eq 5. Is computed via the
        Poisson equation.

        :param radius: radius at which the density should be evaluated
        :type radius: float
        :param element_centroids: optionally provide the element centroids
            alongside with the radius to determine the region from which the
            the denty should be evaluated. Needed because the the gradient of
            the gravitational force is discontinuous at discontinuities of the
            density
        :type element_centroids: array of float of same shape as radius
        """
        if self.gravity_fct is None:
            self.compute_ellipticity(**compute_ellipticity_kwargs)

        rho = self.get_elastic_parameter('RHO', radius, element_centroids)

        g0 = self.gravity_fct(radius)

        # compute derivative of gravitational acceleration. near the center of
        # the Earth use analytical solution for homogeneous sphere
        g0_prime = np.zeros_like(radius)
        sl = radius > r_0
        g0_prime[sl] = (4 * np.pi * GRAVITY_G * rho[sl] -
                        2 * g0[sl] / (radius[sl] * self.scale))
        sl = np.logical_not(sl)
        g0_prime[sl] = 4. / 3. * np.pi * GRAVITY_G * rho[sl]

        return g0_prime

    def compute_norms(self, nsamp_per_layer=100):

        self.norms = {}

        average_density = 0.

        for iregion in range(self.nregions):
            r, centroid = self._get_radial_sampling(iregion, nsamp_per_layer)
            density = self.get_elastic_parameter('RHO', r, centroid)
            average_density += cumtrapz(r ** 2 * density, r)[-1] * 3.

        self.norms['DENSITY'] = average_density
        self.norms['RADIUS'] = self.scale
        self.norms['VELOCITY'] = self.scale * (np.pi * average_density *
                                               GRAVITY_G) ** 0.5
        self.norms['FREQUENCY'] = self.norms['VELOCITY'] / self.scale
        self.norms['TIME'] = 1. / self.norms['FREQUENCY']

    def get_mass(self, relative_error=1e-10):

        return self._get_ith_moment(i=2) * 4 * np.pi

    def get_moment_of_inertia(self, relative_error=1e-10):

        return self._get_ith_moment(i=4) * 8 / 3. * np.pi

    def _get_ith_moment(self, i=2, relative_error=1e-10):

        moment = 0.
        epsrel = relative_error / np.sqrt(self.nregions)

        def integral_kernel(r, region=None):
            return r ** i * self.get_native_parameter(
                'RHO', r / self.scale, region=region)

        for iregion in range(self.nregions):
            r1, r2 = self.discontinuities[[iregion, iregion+1]] * self.scale
            moment += quad(integral_kernel, r1, r2, args=(iregion,),
                           epsrel=epsrel)[0]

        return moment

    def _get_ith_moment_radius(self, radius, i=2, relative_error=1e-10,
                               nsamp_per_layer=100):

        # build sampling for interpolating splines and integration
        r = np.concatenate([np.linspace(self.discontinuities[iregion],
                                        self.discontinuities[iregion+1],
                                        nsamp_per_layer, endpoint=False)
                            for iregion in range(self.nregions)])
        r = np.r_[r, np.array([1.])]
        r_in_m = r * self.scale

        nr = len(r)

        moment = np.zeros(nr)
        epsrel = relative_error / np.sqrt(len(r))

        def integral_kernel(r):
            rho = self.get_rho(r / self.scale)
            return r ** i * rho

        # integrate along the radius
        for j in range(nr - 1):
            moment[j+1] = quad(integral_kernel, r_in_m[j], r_in_m[j+1],
                               epsrel=epsrel)[0]
            moment[j+1] += moment[j]

        moment_fct = InterpolatedUnivariateSpline(r, moment, k=1, ext=3)

        return moment_fct(radius)

    def _get_radial_sampling(self, iregion, nsamp_per_layer=100):
        r = np.linspace(
            self.discontinuities[iregion],
            self.discontinuities[iregion+1], nsamp_per_layer)

        centroid = np.ones(nsamp_per_layer) * \
            np.mean(self.discontinuities[iregion:iregion+2])

        return r, centroid

    def plot(self, nsamp_per_layer=10, figure=None, show=True,
             discontinuities=False):

        if figure is None:
            figure, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex=True)
        else:  # pragma: no cover
            ax1, ax2, ax3, ax4 = tuple(figure.axes)

        AXIS_MAP = {
            'VPV': ax1, 'VPH': ax1, 'VP': ax1,
            'VSV': ax2, 'VSH': ax2, 'VS': ax2,
            'ETA': None,
            'RHO': ax3,
            'QMU': ax4, 'QKAPPA': ax4}

        for param in self.available_elastic_parameters:
            if AXIS_MAP[param] is None:  # pragma: no cover
                continue

            p = np.zeros((self.nregions, nsamp_per_layer))
            x = np.zeros((self.nregions, nsamp_per_layer))
            for iregion in range(self.nregions):
                x[iregion, :], centroid = self._get_radial_sampling(
                    iregion, nsamp_per_layer)
                p[iregion, :] = self.get_elastic_parameter(
                    param, x[iregion, :], centroid)

            # scale to nicer numerical values
            if param not in ['QMU', 'QKAPPA', 'ETA']:
                p /= 1e3

            ax = AXIS_MAP[param]
            ax.plot(x.flatten() * self.scale / 1e3, p.flatten(),
                    label='%s - %s' % (self.name, param))
            ax.legend(loc='best')
            ax.set_xlim(0., self.scale / 1e3)

        if discontinuities:
            for ax in [ax1, ax2, ax3, ax4]:
                for d in self.discontinuities * self.scale / 1e3:
                    ax.axvline(d, color='r')

        ax4.set_yscale('log')
        for ax in [ax3, ax4]:
            ax.set_xlabel('Radius / km')
        for ax in [ax1, ax2]:
            ax.set_ylabel('velocity / km / s')
        ax3.set_ylabel('density / g / cm^3')
        ax4.set_ylabel('Q')

        if show:  # pragma: no cover
            plt.show()
        else:
            return figure

    def plot_vp_vs_profile(
         self, nsamp_per_layer=100, depth=False, rho=False, flat_earth=False,
         crust_zoom_depth_km=None, vlim_crust=(2.5, 8.), title=None, show=True,
         inset_axes_kwargs=None, figure=None, highlight_lvl=False,
         colormap={'VP': 'k', 'VS': 'r', 'RHO': 'g'},
         linestylemap={'VP': '-', 'VS': '-', 'RHO': '-'},
         discontinuities=False):

        if inset_axes_kwargs is None:
            inset_axes_kwargs = {}
        if 'width' not in inset_axes_kwargs:
            inset_axes_kwargs['width'] = '30%'
        if 'height' not in inset_axes_kwargs:
            inset_axes_kwargs['height'] = '30%'
        if 'loc' not in inset_axes_kwargs:
            inset_axes_kwargs['loc'] = 3

        if flat_earth:
            depth = True
            rho = False
            depth = False

        if figure is None:
            figure, ax = plt.subplots()
            axins = None
        else:  # pragma: no cover
            ax = figure.axes[0]
            axins = figure.axes[1] if len(figure.axes) == 2 else None

        if discontinuities:
            for _ax in [ax, axins]:
                for d in self.discontinuities * self.scale / 1e3:
                    ax.axhline(d, color='k')

        if crust_zoom_depth_km and axins is None:
            from mpl_toolkits.axes_grid1.inset_locator import inset_axes
            axins = inset_axes(ax, **inset_axes_kwargs)
            axins.yaxis.tick_right()
            axins.xaxis.tick_top()

        params = ['VP', 'VS']
        if rho:
            params += ['RHO']

        for param in params:
            p = np.zeros((self.nregions, nsamp_per_layer))
            x = np.zeros((self.nregions, nsamp_per_layer))
            for iregion in range(self.nregions):
                x[iregion, :], centroid = self._get_radial_sampling(
                    iregion, nsamp_per_layer)
                p[iregion, :] = self.get_elastic_parameter(
                    param, x[iregion, :], centroid)

            p = p.flatten() / 1e3
            if depth:
                xx = (1 - x.flatten()) * self.scale / 1e3
            else:
                xx = x.flatten() * self.scale / 1e3

            if flat_earth:
                mask = xx > 0
                p = self.scale / 1e3 / xx[mask] * p[mask]
                xx = - self.scale * np.log(xx[mask] / self.scale * 1e3) / 1e3

            ax.plot(p, xx, label='%s' % (param,),
                    color=colormap[param], linestyle=linestylemap[param])

            if crust_zoom_depth_km:
                axins.plot(p, xx, color=colormap[param],
                           linestyle=linestylemap[param])

            if highlight_lvl and param in ['VP', 'VS']:
                lvl_mask = np.logical_and(
                    np.abs(np.diff(xx)) > 0.,
                    np.diff(p) > 1e-5)
                where = np.where(lvl_mask)[0]
                for idx in where:
                    plt.axhspan(xx[idx], xx[idx+1], color=colormap[param],
                                alpha=0.3, lw=0.)

        if ax.legend_ is None:
            ax.legend(loc='best')

        if rho:
            ax.set_xlabel('velocity / [km / s],  density / [10^3 kg / m ^ 3]')
        else:
            ax.set_xlabel('velocity / [km / s]')

        ax.set_title(title if title is not None else self.name)

        if crust_zoom_depth_km:
            axins.set_xlim(*vlim_crust)
            if depth:
                axins.set_ylim(-crust_zoom_depth_km / 25, crust_zoom_depth_km)
                axins.invert_yaxis()
            else:
                r_km = self.scale / 1e3
                axins.set_ylim(r_km - crust_zoom_depth_km, r_km)

        if depth:
            ax.set_ylim(self.scale / 1e3, 0.)
            ax.set_ylabel('Depth / km')
        elif not flat_earth:
            ax.set_ylim(0., self.scale / 1e3 * 1.01)
            ax.set_ylabel('Radius / km')
        else:
            ax.set_ylim(xx.max(), 0.)
            ax.set_ylabel('Flat Earth Depth / km')

        if show:  # pragma: no cover
            plt.show()
        else:
            return figure

    def plot_ellipticity(self, nsamp=100, show=True,
                         compute_ellipticity_kwargs={}):

        figure = plt.figure()
        r = np.linspace(0., 1., nsamp)
        plt.plot(r * self.scale / 1e3, self.get_ellipticity(
            r, compute_ellipticity_kwargs=compute_ellipticity_kwargs))

        plt.xlabel('Radius / km')
        plt.ylabel('Ellipticity')

        if show:  # pragma: no cover
            plt.show()
        else:
            return figure

    def plot_gravity(self, nsamp=500, rmax=5., show=True,
                     compute_ellipticity_kwargs={}):

        figure, ax1 = plt.subplots()
        ax2 = ax1.twinx()

        r = np.linspace(0., rmax, nsamp)
        ax1.plot(r * self.scale / 1e3, self.get_gravity(
            r, compute_ellipticity_kwargs=compute_ellipticity_kwargs))

        ax2.plot(r * self.scale / 1e3, self.get_gravitational_potential(
            r, compute_ellipticity_kwargs=compute_ellipticity_kwargs))

        ax1.set_xlabel('Radius / km')
        ax1.set_ylabel('Gravitational Acceleration / [m / s ** 2]')
        ax2.set_ylabel('Gravitational Potential / [J / kg]')

        if show:  # pragma: no cover
            plt.show()
        else:
            return figure

    def plot_ellipticity_gravity(self, nsamp=100, log=False, show=True,
                                 compute_ellipticity_kwargs={}):

        figure, ax1 = plt.subplots()
        ax2 = ax1.twinx()

        r = np.linspace(0., 1., nsamp)

        elli = self.get_ellipticity(
            r, compute_ellipticity_kwargs=compute_ellipticity_kwargs)
        gravi = self.get_gravity(
            r, compute_ellipticity_kwargs=compute_ellipticity_kwargs)

        ax1.plot(r * self.scale / 1e3, elli * 1e3, 'k')
        ax2.plot(r * self.scale / 1e3, gravi, 'r')

        for tl in ax2.get_yticklabels():
                tl.set_color('r')

        ax1.set_xlabel('Radius / km')
        ax1.set_ylabel('Ellipticity * 1000')
        ax2.set_ylabel('Gravitational Acceleration / [m / s ** 2]', color='r')
        if log:
            ax1.set_yscale("log")
            ax2.set_yscale("log")

        plt.ylim(0, None)

        if show:  # pragma: no cover
            plt.show()
        else:
            return figure


def _read_file(file_name):
    with open(file_name) as fh:
        lines = fh.readlines()

    # remove comments and trailing whitespace
    lines = [l.split('#')[0].rstrip() for l in lines]

    # remove empty lines
    lines = [l for l in lines if not l == '']  # NoQa
    return lines


def _check_key(lines, key, default=None):
    count = sum(line.startswith(key) for line in lines)
    if count == 0 and default is not None:
        return default
    elif count == 0 and default is None:  # pragma: no cover
        raise ValueError('Key not found: %s' % (key,))
    elif count > 1:  # pragma: no cover
        raise ValueError('Key multiply defined: %s' % (key,))


def _get_value(lines, key, cast_function=None, default=None):
    # read key/value pair from the same line
    value = _check_key(lines, key, default)
    if value is None:
        value = next(line.split()[1] for line in lines if line.startswith(key))
        if cast_function:
            value = cast_function(value)
    return value


def _get_values(lines, key, cast_function=None, default=None):
    # read key/value pair from the same line
    values = _check_key(lines, key, default)
    if values is None:
        values = next(line.split()[1:] for line in lines
                      if line.startswith(key))
        if cast_function:
            values = [cast_function(i) for i in values]
    return values


def _get_values_ml(lines, key, n=1, cast_function=None, default=None):
    # read multiple values pair from n lines following the key
    values = _check_key(lines, key, default)
    if values is None:
        start = next(i for i, line in enumerate(lines)
                     if line.startswith(key)) + 1

        # if n is none, read until next empty or non indented line or until the
        # end of the file
        if n is None:
            end = next((start + i for i, line in enumerate(lines[start:])
                       if not line.startswith(' ')), None)
        else:
            end = start + n

        # check if the lines are indented
        if False in [line.startswith(' ') for line in lines[start:end]]:
            raise ValueError('Error reading Array Input for Key: %s' %
                             (key,))  # pragma: no cover

        values = [l.split() for l in lines[start:end]]

    if cast_function is None:  # pragma: no cover
        return values
    else:
        return [list(map(cast_function, v)) for v in values]


def _find_discontinuities(values, idx_radius, scale, disc_tolerance):
    radii = values[:, idx_radius] / scale
    radii[-1] = 1.
    idx = np.diff(radii) < disc_tolerance
    nregions = idx.sum() + 1
    idx_region = np.zeros((nregions, 2), dtype='int')
    idx_region[1:, 0] = np.where(idx)[0] + 1
    idx_region[:-1, 1] = np.where(idx)[0] + 1
    idx_region[-1, 1] = values.shape[0]

    discontinuities = np.zeros(nregions + 1)
    discontinuities[1:] = radii[idx_region[:, 1] - 1]

    return radii, idx_region, nregions, discontinuities


def _find_fluid_regions(nregions, anisotropic, columns, idx_region, values,
                        fluid_tolerance):
    # find the fluid regions
    is_fluid = np.zeros(nregions, dtype='bool')
    for vs in VS_MAP[anisotropic]:
        idx_vs = columns.index(vs)
        for iregion in range(nregions):
            idx1, idx2 = idx_region[iregion, 0], idx_region[iregion, 1]
            is_fluid[iregion] = is_fluid[iregion] or np.max(np.abs(
                values[idx1:idx2, idx_vs]) < fluid_tolerance)

    return is_fluid


def _setup_callables_spline(anisotropic, anelastic, values, columns, scale,
                            nregions, idx_region, spline_order, radii):
    # setup the callable functions for elastic parameters
    elastic_parameters_fct = {}
    for param in ELASTIC_PARAMETER_MAP[(anisotropic, anelastic)]:
        elastic_parameters_fct[param] = []
        idx_p = columns.index(param)

        if param not in ['QMU', 'QKAPPA', 'ETA']:
            # convert to SI and scale
            values[:, idx_p] /= scale

        for iregion in range(nregions):
            idx1, idx2 = idx_region[iregion, 0], idx_region[iregion, 1]

            # maximum order determined by the number of nodes provided
            order = min(spline_order, idx2 - idx1 - 1)

            if idx2 - idx1 == 2 and \
               values[idx1, idx_p] == values[idx1+1, idx_p]:
                elastic_parameters_fct[param].append(
                    ConstInterpolator(values[idx1, idx_p]))
            else:
                elastic_parameters_fct[param].append(
                    InterpolatedUnivariateSpline(
                        radii[idx1:idx2], values[idx1:idx2, idx_p],
                        k=order, ext=3))

    return elastic_parameters_fct