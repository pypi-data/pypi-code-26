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
from collections import OrderedDict
import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import os
from scipy.interpolate import RectBivariateSpline, LinearNDInterpolator, \
    CloughTocher2DInterpolator, RectSphereBivariateSpline
# from scipy.interpolate import SmoothSphereBivariateSpline, \
#     LSQSphereBivariateSpline
from scipy.spatial import cKDTree
from warnings import warn

from .connectivity import connectivity_2D, connectivity_3D

from .global_numbering import unique_points, compress_points_connectivity


from .models_1D import ELLIPSOIDS
from . import elements as elem


from .helpers import load_lib

lib = load_lib()


class UnstructuredMesh(object):

    def __init__(self, points, connectivity, element_type=1, scale=1.):

        self.points = points.copy()
        self.connectivity = connectivity.copy()

        if isinstance(element_type, int):
            self.element_type = np.ones(self.nelem, dtype='int') * element_type
        else:
            self.element_type = np.array(element_type)

        self.scale = scale
        self.tensorized = False

        self._reset()

    def _reset(self):
        self.elemental_fields = OrderedDict()
        self.nodal_fields = OrderedDict()
        self.global_variables = OrderedDict()
        self.global_strings = OrderedDict()
        self.global_arrays = OrderedDict()
        self.side_sets = OrderedDict()
        self.topography = OrderedDict()

    def __add__(self, other):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def copy(self):
        return self.__copy__()

    def __deepcopy__(self, memo):
        return self.__copy__()

    def __copy__(self):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    @property
    def nelem(self):
        '''
        Number of elements in the mesh.
        '''
        return self.connectivity.shape[0]

    @property
    def npoint(self):
        '''
        Number of points / nodes in the mesh
        '''
        return self.points.shape[0]

    @property
    def ndim(self):
        '''
        Number of space dimensions. For now either 2 or 3.
        '''
        return self.points.shape[1]

    @property
    def nodes_per_element(self):
        '''
        Number of nodes per element, e. g. 4 for Quads and 8 for Hex
        '''
        return self.connectivity.shape[1]

    @property
    def edges_per_element(self):
        '''
        Number of edges per element, e. g. 4 for Quads and 12 for Hex
        '''
        return len(elem.edges[self.ndim, self.nodes_per_element])

    def get_element_centroid(self):
        '''
        Compute the centroids of all elements on the fly from the nodes of the
        mesh. Usefull to determine which domain in a layered medium an element
        belongs to or to compute elemtal properties from the model.
        '''
        centroid = np.zeros((self.nelem, self.ndim))
        lib.centroid(self.ndim, self.nelem, self.nodes_per_element,
                     self.connectivity, self.points, centroid)
        return centroid

    def get_element_directions(self):
        '''
        compute vectors that point into the reference coordinate direction in
        the center of the element.
        '''
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def get_side_set(self, name):
        '''
        return side set as a python set
        '''
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def attach_global_variable(self, name, data):
        '''
        store global mesh variable.

        :param name: name of the variable
        :type name: string
        :param data: data to store
        :type data: float, string or numpy.ndarray
        '''
        if isinstance(data, str):
            self.global_strings[name] = data
        elif type(data) is float:
            self.global_variables[name] = data
        elif type(data) is np.ndarray:
            self.global_arrays[name] = data
        else:  # pragma: no cover
            raise TypeError(
                'Global Variables can only be float, string or numpy array.')

    def attach_field(self, name, data):
        '''
        store data on either the elements or the nodes (determined by the size
        of data).

        :param name: name of the field
        :type name: string
        :param data: data to store
        :type data: 1D numpy array, with size of either nelem or noint
        '''
        if data.size == self.npoint:
            self.nodal_fields[name] = data
        elif data.size == self.nelem:
            self.elemental_fields[name] = data
        else:  # pragma: no cover
            raise ValueError('Shape matches neither the nodes nor the '
                             'elements')

    def define_side_set(self, name, element_ids=None, side_ids=None,
                        side_set=None):
        '''
        define a set of edges (2D) or faces (3D) with a name.

        Either provide element_ids AND side_set, or only side_ids

        :param name: name of the side set
        :type name: string
        :param element_ids: element ids of the sides
        :type element_ids: 1D numpy integer array
        :param side_ids: side ids of the sides
        :type element_ids: 1D numpy integer array, same shape as element_ids
        :param side_set: set of tuples with element id and side id
        :type element_ids: set of tuples (int, int)
        '''
        if element_ids is not None and side_ids is not None:
            if not element_ids.shape == side_ids.shape:  # pragma: no cover
                raise ValueError('Shape mismatch')

        elif side_set is not None:
            element_ids, side_ids = np.asarray(list(side_set)).T
        else:  # pragma: no cover
            raise ValueError('provide the side set either as a python set or '
                             'two numpy arrays')

        self.side_sets[name] = (element_ids, side_ids)

    @property
    def nnodal_fields(self):
        return len(self.nodal_fields)

    @property
    def nelemental_fields(self):
        return len(self.elemental_fields)

    @property
    def nglobal_variables(self):
        return len(self.global_variables)

    @property
    def nglobal_strings(self):
        return len(self.global_strings)

    @property
    def nglobal_arrays(self):
        return len(self.global_arrays)

    @property
    def nside_sets(self):
        return len(self.side_sets)

    def rotate_coordinates(self, euler_angles):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def add_dem_2D(self, x, dem, y0=0., y1=np.infty, yref=None, kx=3, ky=1,
                   s=None, name=None):
        '''
        Add topography by vertically stretching the domain in the region [y0,
        y1] - points below y0 are kept fixed, points above y1 are moved as
        the DEM, points in between are interpolated.

        Usage: first call add_dem_2D for each boundary that is to be perturbed
            and finally call apply_dem to add the perturbation to the mesh
            coordinates.

        :param x: x coordinates of the DEM
        :type x: numpy array
        :param dem: the DEM
        :type dem: numpy array
        :param y0: vertical coordinate, at which the stretching begins
        :type y0: float
        :param y1: vertical coordinate, at which the stretching ends, can be
            infinity
        :type y1: float
        :param yref: vertical coordinate, at which the stretching ends
        :type yref: float
        :param kx: horizontal degree of the spline interpolation
        :type kx: integer
        :param ky: vertical degree of the spline interpolation
        :type ky: integer
        :param s: smoothing factor
        :type s: float
        '''
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def add_dem_3D(self, x, y, dem, z0=0., z1=np.infty, zref=None,
                   khorizontal=3, s=None, mode='cartesian', name=None):
        '''
        Add topography by vertically stretching the domain in the region [z0,
        z1] - points below z0 and above z1 are kept fixed, points in between
        are linearly interpolated.

        Usage: first call add_dem_3D for each boundary that is to be perturbed
            and finally call apply_dem to add the perturbation to the mesh
            coordinates.

        The DEM can be either structured or unstructured, this is determined
        from the shapes of x and y.

        See scipy.interpolate.RectBivariateSpline for structured Spline
        interpolation and scipy.interpolate.LinearNDInterpolator
        (khorizontal=1) or scipy.interpolate.CloughTocher2DInterpolator
        (khorizontal=3) for more information on the unstructured interpolation.

        :param x: x coordinates of the DEM (colatitude in spherical models in
            radians)
        :type x: numpy array, either 1D for structured data or 2D for
            unstructured data
        :param y: y coordinates of the DEM (longitude in spherical modes in
            radians)
        :type y: numpy array, either 1D for structured data or 2D for
            unstructured data
        :param dem: the DEM
        :type dem: numpy array
        :param z0: vertical coordinate, at which the stretching begins
        :type z0: float
        :param z1: vertical coordinate, at which the stretching ends, can be
            np.infty to just move all points above zref with the DEM
        :type z1: float
        :param zref: vertical coordinate, at which the stretching ends
        :type zref: float
        :param khorizontal: horizontal degree of the spline interpolation. For
            unstructured data either 1 or 3.
        :type khorizontal: integer
        :param s: smoothing factor
        :type s: float
        '''
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def add_ellipticity(self, ellipticity='WGS84'):
        '''
        Add ellipticity by radial stretching the domain.

        Usage: first call add_ellipticity and add_dem_2D/3D and finally call
        apply_dem to add the perturbation to the mesh coordinates.

        :parameter ellipticity: ellipticity as a function of radius
        :type ellipticity: string, float, array of floats or callback function
            to be called with the radius
        '''
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def apply_dem(self, names=None):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def find_side_sets(self, mode='cartesian', tolerance=1e-8):
        '''
        extract surfaces of a 3D box mesh. Needs to be called before appling
        the DEM or space mapping. Assuming 3D hexahedral meshes, where the
        surface elements are all quads or 2D quadrilateral meshes, where the
        surface elements are lines.
        '''
        if mode not in ['cartesian', 'spherical_full', 'spherical_chunk',
                        'spherical_chunk_z', 'spherical_full_axisem']:  # pragma: no cover  # NoQa
            raise ValueError('unkown side set mode %s' % mode)

        if mode == 'cartesian':
            dim_map = ['x', 'y', 'z']

            for dim in np.arange(self.ndim):
                for l, minmax in enumerate([np.min, np.max]):
                    def distance(points):
                        return np.abs(points[:, dim] - minmax(points[:, dim]))

                    name = '%s%d' % (dim_map[dim], l)
                    self.find_side_sets_generic(name, distance,
                                                tolerance=tolerance)

        if mode == 'spherical_full' or mode.startswith('spherical_chunk'):
            for l, minmax in enumerate([np.min, np.max]):
                # radial
                def distance(points):
                    r = (points ** 2).sum(axis=1) ** 0.5
                    return np.abs(r - minmax(r))

                name = 'r%d' % (l,)
                self.find_side_sets_generic(name, distance,
                                            tolerance=tolerance)

        if mode.startswith('spherical_chunk'):
            if self.ndim == 2:
                names = ('t',)
                idx_x = (0,)
                idx_z = (1,)
            elif self.ndim == 3:
                raise ValueError('This feature is not included in the free SalvusMesher version.')

            for l, minmax in enumerate([np.min, np.max]):
                for n, ix, iz in zip(names, idx_x, idx_z):
                    def distance(points):
                        c = np.arctan2(points[:, iz], points[:, ix])
                        return np.abs(c - minmax(c))

                    name = '%s%d' % (n, l)
                    self.find_side_sets_generic(name, distance,
                                                tolerance=tolerance)

        if mode == 'spherical_full_axisem':
            self.find_side_sets('spherical_full', tolerance)

            def distance(points):
                return np.abs(points[:, 0])

            name = 't0'
            self.find_side_sets_generic(name, distance, tolerance=tolerance)

    def find_side_sets_generic(self, name, distance, tolerance=1e-8,
                               attach_side_set=True):
        '''
        define side sets based on a callback function for the distance to that
        surface.
        '''
        # need to map the boundary elements to proper quads with correct node
        # ordering
        side_set_mask = elem.side_set_mask[(self.ndim, self.nodes_per_element)]

        # points on this boundary
        on_boundary_dim = distance(self.points) < tolerance

        # collect connectivity of this boundary
        masks = on_boundary_dim[self.connectivity[:, :]]

        # map to side definitions from exodus
        side_set_elems = []
        side_set_sides = []

        element_ids = np.arange(self.nelem)
        for i, qm in enumerate(side_set_mask):
            sl = np.all(masks == qm, axis=1)
            side_set_elems.append(element_ids[sl])
            side_set_sides.append(np.ones(sl.sum(), dtype='int') * i)

        side_set_elems = np.hstack(side_set_elems)
        side_set_sides = np.hstack(side_set_sides)

        if attach_side_set and len(side_set_elems) > 0:
            self.define_side_set(name, side_set_elems, side_set_sides)
        else:
            return side_set_elems, side_set_sides

    def find_surface(self, side_set_name='surface'):
        '''
        find the surface of the mesh, i.e. all element sides that don't touch
        another element
        '''
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def get_hierarchical_map(self, other, nneighbour=8,
                             check_other_is_refinement=True):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def convert_element_type(self, mode='QuadToTri', spherical=False,
                             r0_spherical=0., r1_spherical=0.,
                             tensor_node_locations=None):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def refine_locally(self, mask, refinement_level=1, hierarchical_map=None,
                       refinement_style='unstable', spherical=False,
                       r0_spherical=0., r1_spherical=0.):
        raise ValueError('This feature is not included in the free SalvusMesher version.')


    def extrude(self, offsets, scale=None, rotation=None, center=None):
        raise ValueError('This feature is not included in the free SalvusMesher version.')


    def extrude_side_set(self, side_set_elems, side_set_sides, offsets,
                         scale=None, rotation=None, center=None):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def apply_element_mask(self, mask, return_mask=False,
                           tolerance_decimals=8):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def split_nodes(self, nodes, elements):
        '''
        split the nodes and replace them in elements by the new node

        :param nodes: array of the nodes to be split
        :type name: numpy.ndarray of integer
        :param elements: list of arrays of the elements for each split node
        :type elements: list of numpy.ndarray of integer
        '''
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def map_to_sphere(self, min_longitude=0., max_longitude=20.,
                      min_colatitude=80., max_colatitude=100., min_radius=0.8,
                      max_radius=1.):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def compute_dt(self, vp, courant_number=1., min_gll_point_distance=1.,
                   fast=True):
        """
        estimate the time step based on the Courant criterion and the
        edgelengths of the elements.

        :param vp: scaled p-wave velocity for each element
        :type vp: array of float
        :param courant_number: Courant number
        :type courant_number: float
        """
        if fast:
            hmin = self._hmin()

        else:
            raise ValueError('This feature is not included in the free SalvusMesher version.')

        hmin *= min_gll_point_distance

        # for plotting
        dt_elem = courant_number * hmin / vp

        # actual dt
        dt = float(dt_elem.min())

        return dt, dt_elem

    def compute_resolved_frequency(self, vmin, elements_per_wavelength):
        """
        estimate the highest resolved frequency:
            vmin / hmax / elements_per_wavelength

        :param vmin: scaled minimum velocity for each element
        :type vmin: array of float
        :param elements_per_wavelength: number of elements needed to resolve
            one wavelength
        :type elements_per_wavelength: float
        """
        hmax = self._hmax()

        resolved_frequency = vmin / hmax / elements_per_wavelength

        return float(resolved_frequency.min()), resolved_frequency

    def compute_mesh_quality(self, quality_measure='edge_aspect_ratio',
                             **kwargs):
        """
        compute mesh quality
        :param quality_measure: one of 'edge_aspect_ratio' or
            'equiangular_skewness'
        :type quality_measure: string
        """
        if quality_measure == 'edge_aspect_ratio':
            hmin = self._hmin()
            hmax = self._hmax()

            quality = hmax / hmin

        elif quality_measure == 'hmax_over_hmax_in':
            hmax_in = kwargs.get('hmax_in')
            hmax = self._hmax()

            quality = hmax / hmax_in

        elif quality_measure == 'equiangular_skewness':
            angles = elem.angles[(self.ndim, self.nodes_per_element)]
            theta_e = elem.theta_e[(self.ndim, self.nodes_per_element)]

            theta_min = np.zeros(self.nelem)
            theta_max = np.zeros(self.nelem)
            theta_min[:] = np.inf

            theta = np.empty(self.nelem)
            for idx in angles:
                lib.angle(self.ndim, self.nelem, self.nodes_per_element,
                          idx[0], idx[1], idx[2], self.connectivity,
                          self.points, theta)

                theta_min = np.minimum(theta_min, theta)
                theta_max = np.maximum(theta_max, theta)

            quality = np.maximum((theta_max - theta_e) / (np.pi - theta_e),
                                 (theta_e - theta_min) / theta_e)

        else:  # pragma: no cover
            raise ValueError('Unknown quality measure %s' % (quality_measure))

        return quality

    def _hmin(self):
        hmin = np.empty(self.nelem)
        hmin[:] = np.inf
        edges = np.array(elem.edges[(self.ndim, self.nodes_per_element)])
        lib.hmin(self.ndim, self.nelem, self.npoint, edges.shape[0],
                 self.nodes_per_element, self.connectivity, edges, self.points,
                 hmin)
        return hmin

    def _hmax(self):
        hmax = np.zeros(self.nelem)
        edges = np.array(elem.edges[(self.ndim, self.nodes_per_element)])
        lib.hmax(self.ndim, self.nelem, self.npoint, edges.shape[0],
                 self.nodes_per_element, self.connectivity, edges, self.points,
                 hmax)
        return hmax

    def _jacobian_at_nodes(self):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def resort_elements_kdtree(self):
        """
        resort elements to increase likelihood that elements that are close in
        the connecivity array are also close in space
        """
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def write_exodus(self, filename, overwrite=True, title=None,
                     compression=None):
        """
        write mesh to exodus file

        :param filename: filename of the meshfile
        :type filename: string
        :param overwrite: overwrite if the file already exists
        :type overwrite: boolean
        :param title: title of the mesh, defaults to filename
        :type title: string
        :param compression: Turn on compression. Pass a tuple of
            ``(method, option)``, e.g. ``("gzip", 2)``. Slows down writing a
            lot but the resulting files are potentially much smaller.
        :type compression: tuple
        """
        from pyexodus import exodus
        is_pyexodus = True

        # remove file, if it exists
        if overwrite:
            try:
                os.remove(filename)
            # if the file does not exist, do nothing
            except OSError:
                pass

        if title is None:
            title = filename.split('.')[0]

        # add a default reference frame
        if 'reference_frame' not in self.global_strings:
            self.global_strings['reference_frame'] = 'cartesian'

        kwargs = {'mode': 'w', 'title': title, 'array_type': 'numpy',
                  'numDims': self.ndim, 'numNodes': self.npoint,
                  'numElems': self.nelem, 'numBlocks': 1, 'numNodeSets': 0,
                  'numSideSets': self.nside_sets}

        if is_pyexodus:
            kwargs['compression'] = compression

        e = exodus(filename, **kwargs)

        e.put_info_records(["%s = %s" % t for t in
                            self.global_strings.items()])

        if self.ndim == 2:
            e.put_coords(self.points[:, 0] * self.scale,
                         self.points[:, 1] * self.scale,
                         np.zeros(self.npoint))
        elif self.ndim == 3:
            raise ValueError('This feature is not included in the free SalvusMesher version.')

        name = elem.name[(self.ndim, self.nodes_per_element)]
        e.put_elem_blk_info(1, name, self.nelem, self.nodes_per_element, 0)

        if is_pyexodus:
            e.put_elem_connectivity(1, self.connectivity, shift_indices=1)
        # Memory intensive!
        else:  # pramga: no cover
            e.put_elem_connectivity(1, self.connectivity.ravel() + 1)

        # we store the variables in the results section of the exodus file,
        # hence need to define a time step
        e.put_time(1, 0.)

        # write global variables
        e.set_global_variable_number(self.nglobal_variables)
        for i, (name, data) in enumerate(sorted(self.global_variables.items(),
                                                key=lambda x: x[0])):
            e.put_global_variable_name(name, i + 1)
            e.put_global_variable_value(name, 1, data)

        # write elemental fields
        e.set_element_variable_number(self.nelemental_fields)
        for i, (name, data) in enumerate(sorted(self.elemental_fields.items(),
                                                key=lambda x: x[0])):
            e.put_element_variable_name(name, i + 1)
            e.put_element_variable_values(1, name, 1, data)

        # write nodal fields
        e.set_node_variable_number(self.nnodal_fields)
        for i, (name, data) in enumerate(sorted(self.nodal_fields.items(),
                                                key=lambda x: x[0])):
            e.put_node_variable_name(name, i + 1)
            e.put_node_variable_values(name, 1, data)

        # write side sets
        for i, (name, (elements, sides)) in enumerate(
             sorted(self.side_sets.items(), key=lambda x: x[0])):
            if elements.size > 0:
                e.put_side_set_params(i + 1, elements.size, 0)
                e.put_side_set(i + 1, elements + 1, sides + 1)
                e.put_side_set_name(i + 1, name)

        e.close()

        # reopen the file to attach global array variables
        if self.nglobal_arrays > 0:
            # make sure we can work with pyexodus as well as the legacy library
            # h5netcdf can't write the netcdf3 files!
            if is_pyexodus:
                import h5netcdf.legacyapi as netCDF4
            else:
                import netCDF4

            nc = netCDF4.Dataset(filename, 'a')

            def _put_global_array_to_exodus(var_name, var_data):
                dims = ()
                for i in np.arange(var_data.ndim):
                    dim_name = var_name + '_dim_%d' % i
                    nc.createDimension(dim_name, var_data.shape[i])
                    dims += (dim_name,)
                nc.createVariable(var_name, var_data.dtype, dims,
                                  zlib=compression is not None)
                nc[var_name][:] = var_data

            # write global arrays
            for i, (name, data) in enumerate(sorted(self.global_arrays.items(),
                                                    key=lambda x: x[0])):
                _put_global_array_to_exodus(name, data)

            nc.close()

    def write_obj_file(self, filename,
                       side_sets=['x0', 'x1', 'y0', 'y1', 'z0', 'z1']):
        '''
        Write the mesh to a wavefront OBJ file.

        Useful as it can be imported by essentially every 3D program. For a
        3D mesh it only writes the hull.
        '''
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def write_legacy_vtk(self, filename, volume=False,
                         side_sets=['x0', 'x1', 'y0', 'y1', 'z0', 'z1']):
        '''
        Write the mesh to a legacy vtk file, meant for visulization with the
        GUI. In 3D, only writes the hull.
        '''
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def write_vtp(self, filename,
                  side_sets=['x0', 'x1', 'y0', 'y1', 'z0', 'z1']):
        '''
        Write the mesh to a vtp file, meant for visulization with the
        GUI. In 3D, only writes the hull.
        '''
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def _build_side_set_connectivity(
       self, side_sets=['x0', 'x1', 'y0', 'y1', 'z0', 'z1']):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def write_xdmf_subcon_tensorized(self, filename):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def write_xdmf_polyline_tensorized(self, filename):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def write_h5_tensorized(self, filename):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def plot(self, show=True, linewidths=0.5, scatter=False, data=None,
             figure=None):
        if figure is None:
            figure = plt.figure()
        plt.axes().set_aspect('equal')

        if self.ndim == 2:
            patches = []

            for ielem in np.arange(self.nelem):
                points = self.points[self.connectivity[ielem, :]]
                points = points[elem.plot_line[(self.ndim,
                                                self.nodes_per_element)]]
                polygon = Polygon(points, closed=True, fill=None)
                patches.append(polygon)

            p = PatchCollection(patches, edgecolor='k', lw=linewidths,
                                facecolor='white')
            if data is not None:
                p.set_array(np.array(data))
                plt.colorbar(p, orientation="horizontal")
            plt.gca().add_collection(p)

            if scatter:
                plt.scatter(self.points[:, 0], self.points[:, 1], s=50, c='r')

            plt.xlim(self.points[:, 0].min(), self.points[:, 0].max())
            plt.ylim(self.points[:, 1].min(), self.points[:, 1].max())

        elif self.ndim == 3:
            ax = figure.gca(projection='3d')

            lid = elem.plot_line[(self.ndim, self.nodes_per_element)]
            for ielem in np.arange(self.nelem):
                p = self.points[self.connectivity[ielem, :]]
                ax.plot3D(
                    p[lid, 0], p[lid, 1], p[lid, 2],
                    color="b")

            if scatter:
                ax.scatter(self.points[:, 0], self.points[:, 1],
                           self.points[:, 2], s=50, c='r')

        else:  # pragma: no cover
            raise NotImplementedError()

        if show:  # pragma: no cover
            plt.show()
        else:
            return figure

    def plot_side_sets(self, show=True, linewidth=0.5, figure=None,
                       side_sets=None, color='b', linestyle='-'):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def plot_quality(self, quality_measure='edge_aspect_ratio', show=True,
                     hist_kwargs={}, compute_quality_kwargs={}):
        figure = plt.figure()

        quality = self.compute_mesh_quality(
            quality_measure, **compute_quality_kwargs)

        plt.hist(quality, **hist_kwargs)
        plt.title('max = %4.2f, min = %4.2f' % (quality.max(), quality.min()))
        plt.xlabel(quality_measure)
        plt.ylabel('frequency')

        if show:  # pragma: no cover
            plt.show()
        else:
            return figure