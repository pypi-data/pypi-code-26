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
import matplotlib.pyplot as plt
import numpy as np

from .connectivity import connectivity_2D
from .global_numbering import compress_points_connectivity
from .unstructured_mesh import UnstructuredMesh


class StructuredGrid2D(object):

    def __init__(self, x, y, mask=None, hmax=None, element_type=1):
        """
        x and y are coordinates of the points, mask is elementwise
        """
        self.x = x.copy()
        self.y = y.copy()

        self.nelem_lat = x.shape[0] - 1
        self.nelem_rad = x.shape[1] - 1

        if isinstance(hmax, float):
            self.hmax = \
                np.ones((self.nelem_lat, self.nelem_rad)) * hmax
        elif isinstance(hmax, np.ndarray):
            if hmax.shape == (self.nelem_lat, self.nelem_rad):
                self.hmax = hmax.copy()
            elif hmax.shape == (self.nelem_rad,):
                self.hmax = hmax.repeat(self.nelem_lat).reshape(
                    (self.nelem_rad, self.nelem_lat)).T
            else:
                raise ValueError('shape of hmax does not match')
        else:
            self.hmax = None

        if mask is None:
            self.mask = np.zeros(np.array(x.shape) - 1, dtype='bool')
        else:
            self.mask = mask.copy()

        if isinstance(element_type, int):
            self.element_type = np.ones((self.nelem_lat, self.nelem_rad),
                                        dtype='int') * element_type
        else:
            self.element_type = np.array(element_type)

    @classmethod
    def shell(self, r_inner, r_outer, nelem_lat, nelem_rad, min_colat=0.,
              max_colat=180., hmax=None):
        """
        generate a simple spherical structured grid
        """
        if not 0. < max_colat <= 180.:  # pragma:  no cover
            raise ValueError('max_colat needs to be in (0., 180.]')

        sg = StructuredGrid2D.rectangle(
            nelem_lat, nelem_rad, min_x=np.deg2rad(min_colat),
            max_x=np.deg2rad(max_colat), min_y=r_inner, max_y=r_outer,
            hmax=hmax)

        sg.x, sg.y = sg.y * np.sin(sg.x), sg.y * np.cos(sg.x)
        sg.element_type[:] = 0

        return sg

    @classmethod
    def shell_vertical_refine(self, r_inner, r_outer, nelem_lat, nelem_rad,
                              min_colat=0., max_colat=180., hmax=None, p1=0.6,
                              p2=0.8):

        if not 0. < max_colat <= 180.:  # pragma:  no cover
            raise ValueError('max_colat needs to be in (0., 180.]')

        sg = StructuredGrid2D.rectangle_vertical_refine(
            nelem_lat, nelem_rad, min_x=np.deg2rad(min_colat),
            max_x=np.deg2rad(max_colat), min_y=r_inner, max_y=r_outer,
            hmax=hmax, p1=p1, p2=p2)

        sg.x, sg.y = sg.y * np.sin(sg.x), sg.y * np.cos(sg.x)
        sg.element_type[:] = 0

        return sg

    @classmethod
    def shell_vertical_refine_doubling(self, r_inner, r_outer, nelem_lat,
                                       nelem_rad, min_colat=0., max_colat=180.,
                                       hmax=None, p1=0.65, p2=0.8):

        if not 0. < max_colat <= 180.:  # pragma:  no cover
            raise ValueError('max_colat needs to be in (0., 180.]')

        sg = StructuredGrid2D.rectangle_vertical_refine_doubling(
            nelem_lat, nelem_rad, min_x=np.deg2rad(min_colat),
            max_x=np.deg2rad(max_colat), min_y=r_inner, max_y=r_outer,
            hmax=hmax, p1=p1, p2=p2)

        sg.x, sg.y = sg.y * np.sin(sg.x), sg.y * np.cos(sg.x)
        sg.element_type[:] = 0

        return sg

    @classmethod
    def shell_radii(self, radius, nelem_lat, min_colat=0., max_colat=180.,
                    hmax=None):
        """
        generate a simple spherical structured grid with uneven radial spacing
        """
        if not 0. < max_colat <= 180.:  # pragma:  no cover
            raise ValueError('max_colat needs to be in (0., 180.]')

        sg = StructuredGrid2D.rectangle_y(
            radius, nelem_lat, min_x=np.deg2rad(min_colat),
            max_x=np.deg2rad(max_colat), hmax=hmax)

        sg.x, sg.y = sg.y * np.sin(sg.x), sg.y * np.cos(sg.x)
        sg.element_type[:] = 0

        return sg

    @classmethod
    def spherical_doubling_layer(self, r_inner, r_outer, nelem_lat,
                                 min_colat=0., max_colat=180., p1=0.5,
                                 hmax=None, flip_vertical=False):
        """
        generate a simple spherical structured grid
        nelem_lat is the element number on the inner side
        """
        if not 0. < max_colat <= 180.:  # pragma:  no cover
            raise ValueError('max_colat needs to be in (0., 180.]')

        sg = StructuredGrid2D.cartesian_doubling_layer(
            nelem_lat, min_x=np.deg2rad(min_colat),
            max_x=np.deg2rad(max_colat), min_y=r_inner, max_y=r_outer,
            hmax=hmax, p1=p1, flip_vertical=flip_vertical)

        sg.x, sg.y = sg.y * np.sin(sg.x), sg.y * np.cos(sg.x)
        sg.element_type[:] = 0
        sg.element_type[1::4, :] = 2
        sg.element_type[2::4, :] = 2

        return sg

    @classmethod
    def spherical_tripling_layer(self, r_inner, r_outer, nelem_lat,
                                 min_colat=0., max_colat=180., hmax=None,
                                 flip_vertical=False):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    @classmethod
    def spherical_axisem_tripling_layer(self, r_inner, r_outer, nelem_lat,
                                        min_colat=0., max_colat=180.,
                                        hmax=None, flip_vertical=False):
        """
        generate a simple spherical structured grid with tripling such that no
        element has a single point on the axis (needed for GLJ quadrature in
        AxiSEM)
        nelem_lat is the element number on the inner side, number of elements
        on the outer side is nelem * 3 - 2
        """
        if not 0. < max_colat <= 180.:  # pragma:  no cover
            raise ValueError('max_colat needs to be in (0., 180.]')

        sg = StructuredGrid2D.cartesian_axisem_tripling_layer(
            nelem_lat, min_x=np.deg2rad(min_colat),
            max_x=np.deg2rad(max_colat), min_y=r_inner, max_y=r_outer,
            hmax=hmax, flip_vertical=flip_vertical)

        sg.x, sg.y = sg.y * np.sin(sg.x), sg.y * np.cos(sg.x)
        sg.element_type[:] = 0
        sg.element_type[1::3, :] = 2
        sg.element_type[2::3, :] = 2

        return sg

    @classmethod
    def central_sphere_full(self, r_outer, nelem_lat, hmax=None):

        sg1 = self.central_sphere(r_outer, nelem_lat, full=True, hmax=hmax,
                                  left=False)
        sg2 = self.central_sphere(r_outer, nelem_lat, full=True, hmax=hmax,
                                  left=True)

        return sg1 + sg2

    @classmethod
    def central_sphere(self, r_outer, nelem_lat, full=False, hmax=None,
                       left=False):
        """
        generate a central mesh of a quarter or half circle
        nelem_lat is the element number along the latitude for the half circle
        returns two structured grids
        """
        if not nelem_lat % 2 == 0:  # pragma: no cover
            raise ValueError('nelem_lat should be even')

        if nelem_lat == 2:
            isqrt2 = 1. / np.sqrt(2)
            p = 0.4
            x_mesh = np.array([[0., 0.], [0.5, p]]) * r_outer
            y_mesh = np.array([[0., 0.5], [0., p]]) * r_outer
            x_mesh_buffer = \
                np.array([[0., isqrt2, 1.], [0., p, 0.5]]) * r_outer
            y_mesh_buffer = \
                np.array([[1., isqrt2, 0.], [0.5, p, 0.]]) * r_outer
        else:
            # set up parameters
            nelem_square = int(nelem_lat / 2)
            nelem_buffer = int(np.ceil(nelem_lat * (2. / np.pi - 0.5)))
            nelem_rad = nelem_buffer + nelem_square

            r_2 = (r_outer * nelem_square) / nelem_rad
            r_3 = (r_2 + r_outer) / 2. ** 1.5

            # build square
            x = np.linspace(0., r_2, nelem_square + 1)
            y = np.linspace(0., r_2, nelem_square + 1)

            x_mesh, y_mesh = np.meshgrid(x, y, indexing='ij')

            # deform square linearly with cosine boundaries on top and right
            dx = (1 - np.cos(x_mesh / r_2 * np.pi / 2.))
            dy = (1 - np.cos(y_mesh / r_2 * np.pi / 2.))

            x_mesh += -dx * dy * (r_2 - r_3)
            y_mesh += -dx * dy * (r_2 - r_3)

            # add buffer layer
            angle = np.linspace(0., np.pi / 2, nelem_square * 2 + 1)
            x_buffer = r_outer * np.sin(angle)
            y_buffer = r_outer * np.cos(angle)

            x_square_surf = np.concatenate((x_mesh[:, -1], x_mesh[-1, -2::-1]))
            y_square_surf = np.concatenate((y_mesh[:, -1], y_mesh[-1, -2::-1]))

            x_mesh_buffer = np.zeros((nelem_buffer + 1, nelem_square * 2 + 1))
            y_mesh_buffer = np.zeros((nelem_buffer + 1, nelem_square * 2 + 1))

            # linearly map between circle and outer later of the square
            for i in np.arange(nelem_buffer + 1):
                w1 = float(i) / nelem_buffer
                w2 = 1 - w1
                x_mesh_buffer[i, :] = w1 * x_square_surf + w2 * x_buffer
                y_mesh_buffer[i, :] = w1 * y_square_surf + w2 * y_buffer

        if full:
            x_mesh = np.concatenate((x_mesh.T[::-1, :], x_mesh.T[1:, :])).T
            y_mesh = np.concatenate((-y_mesh.T[::-1, :], y_mesh.T[1:, :])).T
            x_mesh_buffer = np.concatenate((x_mesh_buffer.T[:-1, :],
                                            x_mesh_buffer.T[::-1, :])).T
            y_mesh_buffer = np.concatenate((y_mesh_buffer.T[:-1, :],
                                            -y_mesh_buffer.T[::-1, :])).T
        element_type_buffer = np.ones(
            (x_mesh_buffer.shape[0] - 1, x_mesh_buffer.shape[1] - 1),
            dtype='int')
        element_type_buffer[0, :] = 2

        if left:
            x_mesh = -1 * x_mesh[:, ::-1]
            y_mesh = y_mesh[:, ::-1]
            x_mesh_buffer = -1 * x_mesh_buffer[:, ::-1]
            y_mesh_buffer = y_mesh_buffer[:, ::-1]
            element_type_buffer = element_type_buffer[:, ::-1]

        return (self(x_mesh, y_mesh, hmax=hmax, element_type=1),
                self(x_mesh_buffer, y_mesh_buffer, hmax=hmax,
                     element_type=element_type_buffer))

    @classmethod
    def rectangle(self, nelem_x, nelem_y, min_x=0., max_x=1., min_y=0.,
                  max_y=1., hmax=None):
        """
        generate a simple rectangular structured grid
        """
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    @classmethod
    def rectangle_vertical_refine(self, nelem_x, nelem_y, min_x=0., max_x=1.,
                                  min_y=0., max_y=1., hmax=None, p1=0.6,
                                  p2=0.8):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    @classmethod
    def rectangle_vertical_refine_doubling(self, nelem_x, nelem_y, min_x=0.,
                                           max_x=1., min_y=0., max_y=1.,
                                           hmax=None, p1=0.65, p2=0.8):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    @classmethod
    def rectangle_y(self, y, nelem_x, min_x=0., max_x=1., hmax=None):
        """
        generate a simple rectangular structured grid
        """
        x = np.linspace(min_x, max_x, nelem_x + 1)

        y_mesh, x_mesh = np.meshgrid(y, x)

        return self(x_mesh, y_mesh, hmax=hmax, element_type=1)

    @classmethod
    def cartesian_doubling_layer(self, nelem_x, min_x=0., max_x=1., min_y=0.,
                                 max_y=1., hmax=None, move_nodes=True, p1=0.5,
                                 apply_mask=True, flip_vertical=False):
        """
        generate a cartesian structured grid with doubling
        nelem_lat is the element number on the inner side
        """
        x = np.linspace(min_x, max_x, nelem_x * 2 + 1)
        y = np.linspace(min_y, max_y, 3)

        y_mesh, x_mesh = np.meshgrid(y, x)

        if move_nodes:
            y_mesh[2::4, 1] = min_y
            y_mesh[1::4, 1] = min_y + (max_y - min_y) * p1
            y_mesh[3::4, 1] = min_y + (max_y - min_y) * p1
            x_mesh[1::4, 0] += (max_x - min_x) / (nelem_x * 2.)
            x_mesh[3::4, 0] -= (max_x - min_x) / (nelem_x * 2.)

        # the mask works on element basis, hence the shape is 1 less in each
        # dimension than the coordinate arrays
        mask = np.zeros((nelem_x * 2, 2), dtype='bool')
        if apply_mask:
            mask[1::4, 0] = True
            mask[2::4, 0] = True

        if flip_vertical:
            x_mesh = -x_mesh + max_x + min_x
            y_mesh = -y_mesh + max_y + min_y

        return self(x_mesh, y_mesh, mask, hmax=hmax)

    @classmethod
    def cartesian_tripling_layer(self, nelem_x, min_x=0., max_x=1., min_y=0.,
                                 max_y=1., hmax=None, flip_vertical=False):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    @classmethod
    def cartesian_axisem_tripling_layer(self, nelem_x, min_x=0., max_x=1.,
                                        min_y=0., max_y=1., hmax=None,
                                        flip_vertical=False):
        """
        generate a cartesian structured grid with tripling such that no element
        has a single point on the axis (needed for GLJ quadrature in AxiSEM)
        nelem_lat is the element number on the inner side, number of elements
        on the outer side is nelem * 3 - 2
        """
        x = np.linspace(min_x, max_x, nelem_x * 3 - 1)
        y = np.linspace(min_y, max_y, 3)

        y_mesh, x_mesh = np.meshgrid(y, x)

        x_bottom = np.linspace(min_x, max_x, nelem_x + 1)

        y_mesh[2:-2:3, 1] = min_y
        x_mesh[2:-2:3, 1] = x_bottom[1:-1]
        # these points are not used (masked), but moving them as well to ensure
        # they are not present in the unique point set later on.
        x_mesh[2:-2:3, 0] = x_bottom[1:-1]

        x_mesh[3::3, 0] = x_bottom[1:-1]
        x_mesh[1::3, 0] = x_bottom[1:]

        # move the central nodes as well to avoid skewed elements
        x_center_l = (x_mesh[2:-2:3, 1] + x_mesh[2:-2:3, 2]) / 2.
        x_center_1 = x_center_l[:-1] + np.diff(x_center_l) / 3.
        x_center_2 = x_center_l[:-1] + np.diff(x_center_l) / 3. * 2.
        x_mesh[3:-2:3, 1] = x_center_1
        x_mesh[4:-2:3, 1] = x_center_2

        # the mask works on element basis, hence the shape is 1 less in each
        # dimension than the coordinate arrays
        mask = np.zeros((nelem_x * 3 - 2, 2), dtype='bool')
        mask[2:-2:3, 0] = True
        mask[4:-2:3, 0] = True
        mask[1, 0] = True
        mask[-2, 0] = True

        if flip_vertical:
            x_mesh = -x_mesh + max_x + min_x
            y_mesh = -y_mesh + max_y + min_y

        return self(x_mesh, y_mesh, mask, hmax=hmax)

    def add_mask(self, criterion):
        """
        add a mask to the structured grid according to the criterion evaluated
        at the element centroids.

        :param criterion: callback function with the signature criterion(x, y)
            which returns an array of bool, True for those elements that should
            be masked out.
        :type criterion: function
        """
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def nelem(self):
        return self.mask.size - self.mask.sum()

    def npoint(self):
        return self.x.shape[0] * self.x.shape[1]

    def get_element_centroid(self):
        xc = self.x.copy()
        xc = (xc[:-1, :] + xc[1:, :]) / 2
        xc = (xc[:, :-1] + xc[:, 1:]) / 2

        yc = self.y.copy()
        yc = (yc[:-1, :] + yc[1:, :]) / 2
        yc = (yc[:, :-1] + yc[:, 1:]) / 2

        return xc, yc

    def get_connectivity(self):
        connectivity = connectivity_2D(self.nelem_lat, self.nelem_rad)

        connectivity = \
            connectivity[np.logical_not(self.mask).T.flatten(), :]

        return connectivity

    def get_element_type(self):

        return self.element_type.T.flatten()[
            np.logical_not(self.mask).T.flatten()]

    def get_unstructured_mesh(self):
        points = np.empty((2, self.npoint()))
        points[0, :] = self.x.flatten()
        points[1, :] = self.y.flatten()

        points, connectivity = compress_points_connectivity(
            points.T, self.get_connectivity())

        return UnstructuredMesh(points, connectivity)


    def plot(self, **kwargs):
        """
        tolerance moves the colorscale slightly such that values at the
        boundary are included.
        """
        if kwargs.get('new_figure'):
            plt.figure()
        plt.axes().set_aspect('equal', 'datalim')
        cmap = kwargs.get('cmap')
        linewidths = kwargs.get('linewidths', 1.)
        mode = kwargs.get('mode')
        tolerance = kwargs.get('tolerance', 1e-3)
        edgecolor = kwargs.get('edgecolor', 'k')

        if mode in ['max_diag', 'max_edge']:
            vmin, vmax = 0., 1.25
        elif mode == 'element_type':
            vmin, vmax = 0., 3.
        else:
            vmin, vmax = None, None

        if mode is None:
            data = self.mask
            from .cm import cmap_white
            cmap = cmap_white

        elif mode == 'max_diag':
            h1 = ((self.x[1:, 1:] - self.x[:-1, :-1]) ** 2 +
                  (self.y[1:, 1:] - self.y[:-1, :-1]) ** 2) ** 0.5
            h2 = ((self.x[:-1, 1:] - self.x[1:, :-1]) ** 2 +
                  (self.y[:-1, 1:] - self.y[1:, :-1]) ** 2) ** 0.5
            data = np.maximum(h1, h2) / self.hmax / 2 ** 0.5

        elif mode == 'max_edge':
            h1 = ((self.x[1:, 1:] - self.x[:-1, 1:]) ** 2 +
                  (self.y[1:, 1:] - self.y[:-1, 1:]) ** 2) ** 0.5
            h2 = ((self.x[1:, 1:] - self.x[1:, :-1]) ** 2 +
                  (self.y[1:, 1:] - self.y[1:, :-1]) ** 2) ** 0.5
            h3 = ((self.x[:-1, :-1] - self.x[:-1, 1:]) ** 2 +
                  (self.y[:-1, :-1] - self.y[:-1, 1:]) ** 2) ** 0.5
            h4 = ((self.x[:-1, :-1] - self.x[1:, :-1]) ** 2 +
                  (self.y[:-1, :-1] - self.y[1:, :-1]) ** 2) ** 0.5
            data1 = np.maximum(h1, h2) / self.hmax
            data2 = np.maximum(h3, h4) / self.hmax
            data = np.maximum(data1, data2)

        elif mode == 'element_type':
            data = self.element_type

        else:  # pragma:  no cover
            raise ValueError('Invalid mode "%s"' % (mode,))

        if mode in ['max_edge', 'max_diag']:
            vmin += tolerance
            vmax += tolerance
            if cmap is None:
                from .cm import cmap_quality
                cmap = cmap_quality

        plt.pcolor(self.x, self.y, data, edgecolor=edgecolor, cmap=cmap,
                   linewidths=linewidths, vmin=vmin, vmax=vmax)

        if kwargs.get('colorbar'):
            plt.colorbar()

        if kwargs.get('scatter'):
            plt.scatter(self.x, self.y, s=50, c='r', marker='o')

        plt.xlabel('x')
        plt.ylabel('y')

        if kwargs.get('show'):  # pragma:  no cover
            plt.show()
        else:
            return plt.gcf()