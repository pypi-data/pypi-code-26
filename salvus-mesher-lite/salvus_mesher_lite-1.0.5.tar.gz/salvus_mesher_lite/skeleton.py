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
from .structured_grid_2D import StructuredGrid2D
from .unstructured_mesh import UnstructuredMesh
from .global_numbering import compress_points_connectivity


class Skeleton(object):
    """
    A Skeleton is a collection of StructuredGrid2D or StructuredGrid3D objects.
    Points are hence not unique, but it provides functionality to convert to an
    unstructured mesh.
    """

    def __init__(self, subgrids):
        """
        Initialize a Skeleton from a list of StructuredGrid2D or
        StructuredGrid3D objects.
        """
        self.subgrids = list(subgrids)

        if isinstance(subgrids[0], StructuredGrid2D):
            self.ndim = 2
            sgtype = StructuredGrid2D
            self.nodes_per_element = 4
        else:
            raise TypeError

        for sg in subgrids:
            if not isinstance(sg, sgtype):
                raise TypeError

    @classmethod
    def create_cartesian_mesh(self, discontinuities, hmax, ndim=2,
                              horizontal_boundaries=None, hmax_refinement=1.5,
                              refinement_style='doubling',
                              refinement_top_down=True,
                              return_info_dict=False):
        """
        create a cartesian mesh, quads in 2D or Hex in 3D

        Note: using normalized coordinates here

        :param discontinuities: discontinuities to be respected by the mesh
            including top and bottom. Z is positive upwards, discontinuities
            should be sorted from bottom to to top.
        :type discontinuities: array of floats
        :param hmax: maximum elementsize between the discontinuities. Needs to
            be provided for all layers
        :type hmax: array of floats, length = len(discontinuities) - 1
        :param ndim: number of space dimensions
        :type ndim: integer
        :param horizontal_boundaries: horizontal boundaries of the domain,
            defaults to [0, 1]
        :type horizontal_boundaries: tuple of two numpy float arrays with shape
            (ndim)
        :param hmax_refinement: criterion (radial oversamping factor) for
            moving doubling_layers inwards to avoid small timestep. Smaller
            values = more aggressive.
        :type hmax_refinement: float
        :param refinement_style: refinement style to use, choices: "doubling",
            "tripling" and for 3D also "doubling_single_layer"
        :type refinement_style: string
        :param refinement_top_down: top down approach means minimizing number
            of elements at the surface at the cost of more elements at the
            bottom (default). If False, bottom up approach is used, that is
            minimizing number of elements at the bottom at the cost of more
            elements at the surface. Which one is more efficient depends on the
            velocity model and refinement style.
        :type refinement_top_down: boolean
        """

        if ndim not in [2, 3]:  # pragma: no cover
            raise ValueError("'ndim' needs to be 2 or 3'")

        if horizontal_boundaries is None:
            if ndim == 2:
                horizontal_boundaries = (np.array([0.]), np.array([1.]))
            elif ndim == 3:
                raise ValueError('This feature is not included in the free SalvusMesher version.')

        if ndim == 2:  # pragma: no cover
            if refinement_style not in ['doubling', 'tripling']:
                raise ValueError('invalid refinement_style')
            refinement_thickness = 1
        elif ndim == 3:
            raise ValueError('This feature is not included in the free SalvusMesher version.')

        if 'doubling' in refinement_style:
            refinement_factor = 2
        elif 'tripling' in refinement_style:
            refinement_factor = 3

        layer_thickness = np.diff(discontinuities)
        nelem_vertical = np.ceil(layer_thickness / hmax).astype('int')

        # estimate number of elements at the top and bottom
        nelem_top, nelem_bottom, nrefine = _estimate_nelem_nrefine(
            horizontal_boundaries, hmax, refinement_factor,
            refinement_top_down)

        # locate refinement layers
        refinement_layers, h_vertical, hmax_elem, element_boundaries = \
            _locate_refinement_layer(layer_thickness, nelem_vertical,
                                     nelem_top, nelem_bottom, discontinuities,
                                     horizontal_boundaries, hmax, nrefine,
                                     refinement_factor, ndim)

        # run a number of tests on the refinement layers
        refinement_layers, nrefine, nelem_bottom = _check_refinement_layer(
            refinement_layers, h_vertical, hmax_refinement,
            nelem_vertical, hmax_elem, nrefine, refinement_thickness,
            nelem_bottom, refinement_factor)

        # build index arrays of where to put simple and refinement layers
        simple_layers, refinement_fac = _build_index_arrays(
            element_boundaries, refinement_layers, nrefine,
            refinement_thickness, refinement_factor)

        # finally do the meshing
        subgrids = []

        if ndim == 2:
            # simple rectangle with varying radial h
            for i, ids in enumerate(simple_layers):
                sg = StructuredGrid2D.rectangle_y(
                    element_boundaries[ids[0]:ids[1]],
                    nelem_bottom[0] * refinement_fac[i],
                    min_x=horizontal_boundaries[0][0],
                    max_x=horizontal_boundaries[1][0],
                    hmax=hmax_elem[ids[0]:ids[1]-1])
                subgrids.append(sg)

            # refinement layers
            refinement_sg_map = {
                'doubling': StructuredGrid2D.cartesian_doubling_layer,
                'tripling': StructuredGrid2D.cartesian_tripling_layer}

            for d, i in enumerate(refinement_layers):
                sg = refinement_sg_map[refinement_style](
                    nelem_bottom[0] * refinement_factor ** d,
                    min_x=horizontal_boundaries[0][0],
                    max_x=horizontal_boundaries[1][0],
                    min_y=element_boundaries[i],
                    max_y=element_boundaries[i+1],
                    hmax=hmax_elem[i])
                subgrids.append(sg)

        elif ndim == 3:
            raise ValueError('This feature is not included in the free SalvusMesher version.')

        if return_info_dict:
            info_dict = {'nelem_top': nelem_top,
                         'nelem_bottom': nelem_bottom,
                         'element_boundaries': element_boundaries}
            return self(subgrids), info_dict
        else:
            return self(subgrids)

    @classmethod
    def create_cartesian_nonconforming_mesh(self, discontinuities, hmax,
                                            ndim=2, horizontal_boundaries=None,
                                            refinement_top_down=True,
                                            refinement_factor=2):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    @classmethod
    def create_spherical_mesh(
       self, discontinuities, hmax, ndim=2, max_colat=None, min_colat=None,
       full_sphere=False, inner_core=False, axisem=False, hmax_refinement=1.5,
       refinement_style='doubling', refinement_top_down=True,
       exclude_top_n_regions=0, return_info_dict=False,
       nelem_bottom_integer_multiple=None, nelem_vertical=None,
       max_nrefine=None):
        """
        create a cartesian or spherical mesh, quads in 2D or Hex in 3D

        Note: using normalized coordinates here

        :param discontinuities: discontinuities to be respected by the mesh
            including the surface (1.) and the center (0.)
        :type discontinuities: array of floats
        :param hmax: maximum elementsize between the discontinuities. Needs to
            be provided for all layers (including the center, even if it is not
            meshed)
        :type hmax: array of floats, length = len(discontinuities) - 1
        :param ndim: number of space dimensions
        :type ndim: integer
        :param min_colat:
        :type min_colat:
        :param max_colat:
        :type max_colat:
        :param full_sphere: make a full sphere (overwrites max_colat)
        :type full_sphere: bool
        :param inner_core: include the inner core (only for full_sphere true)
        :type inner_core: bool
        :param hmax_refinement: criterion (radial oversamping factor) for
            moving doubling_layers inwards to avoid small timestep. Smaller
            values = more aggressive.
        :type hmax_refinement: float
        :param refinement_style: refinement style to use, choices: "doubling",
            and "tripling" foe 2D, "doubling" only for 3D
        :type refinement_style: string
        :param refinement_top_down: top down approach means minimizing number
            of elements at the surface at the cost of more elements at the
            bottom (default). If False, bottom up approach is used, that is
            minimizing number of elements at the bottom at the cost of more
            elements at the surface. Which one is more efficient depends on the
            velocity model and refinement style.
            Bottom up likely won't work without inner core.
        :type refinement_top_down: boolean
        :param exclude_top_n_regions: design the mesh as usual but do not
            leave out the first n regions from the top. Meant to enable
            vertical refinements in the shallow layers
        :type exclude_top_n_regions: int
        :param nelem_vertical: optionally provide the number of elements in
            vertical direction for all layers and override hmax for the
            vertical.
        :type nelem_vertical: array of int, length = len(discontinuities) - 1
        :param max_nrefine: maximum number of refinement layers to be used
        :type max_nrefine: int
        """

        if ndim not in [2, 3]:  # pragma: no cover
            raise ValueError("'ndim' needs to be 2 or 3'")

        if inner_core and not full_sphere:
            raise ValueError('inner_core only possible with full_sphere')

        if max_colat is None or full_sphere:
            if ndim == 2:
                max_colat = np.array([180.])
            elif ndim == 3:
                raise ValueError('This feature is not included in the free SalvusMesher version.')

        if (min_colat is None or full_sphere) and not axisem:
            min_colat = -max_colat
        elif axisem:
            min_colat = np.array([0.])

        max_colat = np.array(np.deg2rad(max_colat)).reshape((ndim-1))
        min_colat = np.array(np.deg2rad(min_colat)).reshape((ndim-1))

        if ndim == 2:
            if refinement_style not in ['doubling', 'tripling']:  # pragma: no cover  # NoQa
                raise ValueError('invalid refinement_style')
            if refinement_style == 'tripling' and axisem:
                refinement_style = 'tripling_axisem'
            refinement_thickness = 1

        elif ndim == 3:
            raise ValueError('This feature is not included in the free SalvusMesher version.')

        if 'doubling' in refinement_style:
            refinement_factor = 2

        elif 'tripling' in refinement_style:
            refinement_factor = 3

        if nelem_bottom_integer_multiple is None:
            if ndim == 3 and refinement_factor == 2 and full_sphere:
                raise ValueError('This feature is not included in the free SalvusMesher version.')
            elif ndim == 2 and inner_core:
                nelem_bottom_integer_multiple = 8 if not axisem else 4
            else:
                nelem_bottom_integer_multiple = 1
        else:
            assert nelem_bottom_integer_multiple > 0
            if ndim == 3 and refinement_factor == 2 and full_sphere:
                raise ValueError('This feature is not included in the free SalvusMesher version.')

        layer_thickness = np.diff(discontinuities)
        if nelem_vertical is None:
            nelem_vertical = np.ceil(layer_thickness[1:] /
                                     hmax[1:]).astype('int')
        else:
            assert len(nelem_vertical) == len(discontinuities) - 2

        # estimate number of elements at the top and bottom
        nelem_top, nelem_bottom, nrefine = _estimate_nelem_nrefine(
            (min_colat, max_colat), hmax[1:], refinement_factor,
            refinement_top_down, nelem_bottom_integer_multiple, spherical=True,
            discontinuities=discontinuities[1:],
            h_icb=hmax[0], inner_core=inner_core, max_nrefine=max_nrefine)

        # locate refinement layers
        refinement_layers, h_vertical, hmax_elem, element_boundaries = \
            _locate_refinement_layer(
                layer_thickness[1:], nelem_vertical, nelem_top, nelem_bottom,
                discontinuities[1:], (min_colat, max_colat), hmax[1:],
                nrefine, refinement_factor, ndim, spherical=True)

        # run a number of tests on the refinement layers
        refinement_layers, nrefine, nelem_bottom = _check_refinement_layer(
            refinement_layers, h_vertical, hmax_refinement,
            nelem_vertical, hmax_elem, nrefine, refinement_thickness,
            nelem_bottom, refinement_factor)

        # build index arrays of where to put simple and refinement layers
        simple_layers, refinement_fac = _build_index_arrays(
            element_boundaries, refinement_layers, nrefine,
            refinement_thickness, refinement_factor)

        if exclude_top_n_regions > 0:
            idx = nelem_vertical.cumsum()[-exclude_top_n_regions-1]
            element_boundaries = element_boundaries[:idx+1]
            simple_layers = [sl for sl in simple_layers if sl[0] <= idx]
            if simple_layers[-1][0] == idx:
                # hence we are just on top of a refinement, so delete this
                # layer
                simple_layers = simple_layers[:-1]
            else:
                simple_layers[-1][1] = idx + 1

        # finally do the meshing
        subgrids = []

        if ndim == 2:
            # for axisem tripling need to correct for the missing 2 elements in
            # each refinement. This is not a rigorous treatment and might lead
            # to some unnecessary extra elements at the surface for meshes with
            # inner_core
            if 'axisem' in refinement_style:
                nelem_bottom = (np.ceil((nelem_bottom + 1.) /
                                        nelem_bottom_integer_multiple) *
                                nelem_bottom_integer_multiple).astype('int')

            def _ncorr(ref):
                if 'axisem' not in refinement_style:
                    return 0
                i = int(np.log(ref) / np.log(3.))
                n = 0
                for _i in range(i):
                    n = 3 * n + 2
                return n

            # simple rectangle with varying radial h
            for i, ids in enumerate(simple_layers):
                sg = StructuredGrid2D.shell_radii(
                    element_boundaries[ids[0]:ids[1]],
                    nelem_bottom[0] * refinement_fac[i] -
                    _ncorr(refinement_fac[i]),
                    min_colat=np.rad2deg(min_colat[0]),
                    max_colat=np.rad2deg(max_colat)[0],
                    hmax=hmax_elem[ids[0]:ids[1]-1])
                subgrids.append(sg)

            # refinement layers
            refinement_sg_map = {
                'doubling': StructuredGrid2D.spherical_doubling_layer,
                'tripling': StructuredGrid2D.spherical_tripling_layer,
                'tripling_axisem':
                    StructuredGrid2D.spherical_axisem_tripling_layer}

            for d, i in enumerate(refinement_layers):
                sg = refinement_sg_map[refinement_style](
                    element_boundaries[i],
                    element_boundaries[i+1],
                    nelem_bottom[0] * refinement_factor ** d -
                    _ncorr(refinement_factor ** d),
                    min_colat=np.rad2deg(min_colat[0]),
                    max_colat=np.rad2deg(max_colat)[0],
                    hmax=hmax_elem[i])
                subgrids.append(sg)

            if inner_core:

                if min_colat[0] == -np.deg2rad(180.):
                    sgs = StructuredGrid2D.central_sphere(
                        discontinuities[1], nelem_bottom[0] / 4, full=True,
                        hmax=hmax[0])
                    subgrids += [_ for _ in sgs]

                    sgs = StructuredGrid2D.central_sphere(
                        discontinuities[1], nelem_bottom[0] / 4, full=True,
                        left=True, hmax=hmax[0])
                    subgrids += [_ for _ in sgs]
                else:
                    sgs = StructuredGrid2D.central_sphere(
                        discontinuities[1], nelem_bottom[0] / 2, full=True,
                        hmax=hmax[0])
                    subgrids += [_ for _ in sgs]

        elif ndim == 3:
            raise ValueError('This feature is not included in the free SalvusMesher version.')

        if return_info_dict:
            info_dict = {'nelem_top': nelem_top,
                         'nelem_bottom': nelem_bottom,
                         'element_boundaries': element_boundaries}
            return self(subgrids), info_dict
        else:
            return self(subgrids)

    @classmethod
    def create_spherical_nonconforming_mesh(self, discontinuities, hmax,
                                            ndim=2, max_colat=None,
                                            min_colat=None, full_sphere=False,
                                            inner_core=False, axisem=False,
                                            refinement_top_down=True,
                                            refinement_factor=2):
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def add_mask(self, criterion):
        """
        add a mask to the structured grid according to the criterion evaluated
        at the element centroids.

        :param criterion: callback function with the signature criterion(x, y)
            for 2D and criterion(x, y, z) for 3D which returns an array of
            bool, True for those elements that should be masked out.
        :type criterion: function
        """
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    def nelem(self):
        nelem = 0
        for sg in self.subgrids:
            nelem += sg.nelem()
        return nelem

    def npoint(self):
        npoint = 0
        for sg in self.subgrids:
            npoint += sg.npoint()
        return npoint

    @property
    def hmax(self):
        return np.concatenate([sg.hmax[np.logical_not(sg.mask.mask)] for sg in
                               self.subgrids])

    def get_points_connectivity_elementtype(self):
        # build the set of unique global points
        points = np.empty((self.ndim, self.npoint()))
        start = 0
        for sg in self.subgrids:
            npoint = sg.npoint()
            points[0, start:start+npoint] = sg.x.ravel()
            if self.ndim > 1:
                points[1, start:start+npoint] = sg.y.ravel()
            if self.ndim > 2:
                points[2, start:start+npoint] = sg.z.ravel()
            start += npoint

        # build connectivity
        connectivity = np.zeros((self.nelem(), self.nodes_per_element),
                                dtype='int')
        element_type = np.zeros(self.nelem(), dtype='int')
        start = 0
        npoint = 0
        for sg in self.subgrids:
            nelem = sg.nelem()
            connectivity[start:start+nelem, :] = sg.get_connectivity() + npoint
            element_type[start:start+nelem] = sg.get_element_type()
            npoint += sg.npoint()
            start += nelem

        points, connectivity = compress_points_connectivity(
            points.T, connectivity)

        return points, connectivity, element_type

    def get_unstructured_mesh(self, scale=1.):
        points, connectivity, element_type = \
            self.get_points_connectivity_elementtype()
        m = UnstructuredMesh(points, connectivity, scale=scale)
        m.attach_field('element_type', element_type)
        return m

    def plot(self, show=True, **kwargs):
        cmap = kwargs.get('cmap')
        linewidths = kwargs.get('linewidths')
        mode = kwargs.get('mode')

        fig = plt.figure()
        plt.axes().set_aspect('equal', 'datalim')

        if self.ndim == 2 and mode in ['max_diag', 'max_edge'] \
           and cmap is None:
            from .cm import cmap_quality
            cmap = cmap_quality

        for sg in self.subgrids:
            sg.plot(cmap=cmap, linewidths=linewidths, mode=mode)

        if self.ndim == 2 and mode in ['max_diag', 'max_edge']:
            plt.colorbar(ticks=[0., 0.25, 0.5, 0.75, 1., 1.25])
            plt.title('Quality measure: %s' % mode)

        if show:  # pragma no cover
            plt.show()
        else:
            return fig


def _check_refinement_layer(refinement_layers, h_vertical, hmax_refinement,
                            nelem_vertical, hmax_elem, nrefine,
                            refinement_thickness, nelem_bottom,
                            refinement_factor):

    refinement_layers_ref = np.zeros(len(refinement_layers)) - 1
    # avoid refinement layer in very thin layers
    h_vertical_elem = h_vertical.repeat(nelem_vertical)
    # vertical oversampling before the refinement
    fac = hmax_elem / h_vertical_elem

    # avoid refinement directly at the surface
    refinement_layers = np.clip(refinement_layers, 0,
                                len(h_vertical_elem) - refinement_thickness)

    # avoid refinement directly at the bottom
    def check_bottom(refinement_layers, nrefine, nelem_bottom):
        if np.any(refinement_layers < refinement_thickness):
            refinement_layers = refinement_layers[1:]
            nrefine -= 1
            nelem_bottom *= refinement_factor
        return refinement_layers, nrefine, nelem_bottom

    # need to do this before the loop, to move the refinement out of the domain
    # instead of the vertical oversampling preferebly
    refinement_layers, nrefine, nelem_bottom = check_bottom(
        refinement_layers, nrefine, nelem_bottom)

    # to be strict, we need to iterate over the next few steps to
    # be on the save side (e.g. when there are multiple thin layers)
    # stopping condition is that refinement_layers remains unchanged
    # after checking for all criteria

    while True:
        for d in np.arange(nrefine):
            try:
                crit = fac[:refinement_layers[d]+1][::-1]
                idx = next(
                    i for i, f in enumerate(crit)
                    if np.all(crit[i:i+refinement_thickness] <
                              hmax_refinement))
                refinement_layers[d] = refinement_layers[d] - idx
            except StopIteration:  # pragma: no cover
                raise ValueError(
                    'Did not succeed on avoiding vertical oversampling. '
                    'Try using a larger value of hmax_refinement.')

        # if multiple refinements are required at the same radius (e.g. due
        # to a strong contrast at a discontinuity), move them towards the
        # bottom if refinement layers are multiple elements high, we need
        # to seperate them by n elements
        for i in np.arange(refinement_thickness):
            refinement_layers[:-1] -= \
                (np.diff(refinement_layers[::-1]) == -i).cumsum()[::-1]

        # make sure we have not moved them to far
        refinement_layers, nrefine, nelem_bottom = check_bottom(
            refinement_layers, nrefine, nelem_bottom)

        if np.all(refinement_layers == refinement_layers_ref):
            break

        refinement_layers_ref = refinement_layers.copy()

    return refinement_layers, nrefine, nelem_bottom


def _build_index_arrays(element_boundaries, refinement_layers, nrefine,
                        refinement_thickness, refinement_factor):
    # build index arrays of where to put simple and refinement layers
    nelem_z_tot = len(element_boundaries)
    all_layers = np.concatenate([[-1], refinement_layers, [nelem_z_tot]])
    simple_layers = []
    refinement_fac = []
    for d in np.arange(nrefine + 1):
        if all_layers[d+1] - all_layers[d] > refinement_thickness:
            simple_layers.append([all_layers[d] + 1, all_layers[d+1] + 2 -
                                  refinement_thickness])
            refinement_fac.append(refinement_factor ** d)

    # the uppermost layer is not below a refinement
    simple_layers[-1][1] += refinement_thickness - 1

    return simple_layers, refinement_fac


def _estimate_nelem_nrefine(horizontal_boundaries, hmax, refinement_factor,
                            refinement_top_down,
                            nelem_bottom_integer_multiple=1, spherical=False,
                            discontinuities=None, h_icb=None,
                            inner_core=False, max_nrefine=None):

    # estimate number of elements at the bottom
    nelem_bottom = \
        (horizontal_boundaries[1] - horizontal_boundaries[0]) / hmax[0]

    # estimate number of elements at the top this should be the maximum of
    # horizontal elements over all depths
    hb0 = np.tile(horizontal_boundaries[0], (len(hmax), 1))
    hb1 = np.tile(horizontal_boundaries[1], (len(hmax), 1))
    hm = np.tile(hmax, (len(horizontal_boundaries[0]), 1)).T

    # in the spherical case, the horizontal_boundaries are in radians
    if spherical:
        nelem_bottom *= discontinuities[0]
        disc = np.tile(discontinuities[1:],
                       (len(horizontal_boundaries[0]), 1)).T
        # for spherical models, take the top of each layer to estimate
        # nelem_top
        nelem_top = np.max((hb1 - hb0) / hm * disc, axis=0)
    else:
        nelem_top = np.max((hb1 - hb0) / hm, axis=0)

    if inner_core:
        # number of elements on the outer side of the innermost
        # discontinuity needs to be large enough as well
        nelem_icb = (horizontal_boundaries[1] - horizontal_boundaries[0]) / \
            h_icb * discontinuities[0]

        nelem_bottom = np.maximum(nelem_bottom, nelem_icb)

    nelem_bottom = (np.ceil(
        nelem_bottom / float(nelem_bottom_integer_multiple)) *
        nelem_bottom_integer_multiple).astype('int')
    nelem_top = np.ceil(nelem_top)

    # estimate number of refinement layers
    nrefine = np.log(nelem_top / nelem_bottom) / np.log(refinement_factor)

    if refinement_top_down:
        # rounding down = top down
        nrefine = np.max(np.floor(nrefine).astype('int'))
        if max_nrefine is not None:
            nrefine = min(nrefine, max_nrefine)

        # top down approach, leads to increase in nelem_bottom
        nelem_bottom = (np.ceil(
            nelem_top / refinement_factor ** nrefine)).astype('int')

        # still needs to be a multiple of nelem_bottom_integer_multiple
        nelem_bottom = (np.ceil(
            nelem_bottom / float(nelem_bottom_integer_multiple)) *
            nelem_bottom_integer_multiple).astype('int')

    else:
        # rounding up = bottom up
        nrefine = np.max(np.ceil(nrefine).astype('int'))
        if max_nrefine is not None and nrefine > max_nrefine:
            nelem_bottom *= refinement_factor ** (nrefine - max_nrefine)
            nrefine = min(nrefine, max_nrefine)

    nelem_top = (nelem_bottom * refinement_factor ** nrefine).astype('int')

    return nelem_top, nelem_bottom, nrefine


def _locate_refinement_layer(layer_thickness, nelem_vertical, nelem_top,
                             nelem_bottom, discontinuities,
                             horizontal_boundaries, hmax, nrefine,
                             refinement_factor, ndim=2, spherical=False):

    h_vertical = layer_thickness / nelem_vertical

    element_boundaries = np.concatenate(
        [discontinuities[0:1], discontinuities[0] +
         np.cumsum(h_vertical.repeat(nelem_vertical))])

    h_horizontal = \
        (horizontal_boundaries[1] - horizontal_boundaries[0]) / \
        nelem_bottom

    if spherical:
        h_horizontal = np.outer(h_horizontal, element_boundaries[1:])

    # at discontinuities use the minimum of hmax on both sides
    hmax_elem = hmax.repeat(nelem_vertical)
    hmax_min = hmax_elem.copy()
    hmax_min[:-1] = np.minimum(hmax_min[1:], hmax_min[:-1])

    # for ndim we have to adapt array sizes
    hmax_min = np.tile(hmax_min, (ndim-1, 1))

    if not spherical:
        h_horizontal = np.tile(h_horizontal.reshape((ndim-1, 1)),
                               (1, nelem_vertical.sum()))

    refinement_layers = np.zeros(nrefine, dtype='int')
    for d in np.arange(nrefine):
        refinement_layers[d] = np.min(np.argmax(
            h_horizontal / hmax_min / refinement_factor ** d > 1, axis=1))

    return refinement_layers, h_vertical, hmax_elem, element_boundaries