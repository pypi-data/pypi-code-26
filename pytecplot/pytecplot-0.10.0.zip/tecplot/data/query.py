from collections import namedtuple
from ctypes import byref, c_double, c_int32, c_int64

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from .. import layout
from ..tecutil import Index, IndexSet, lock


@lock()
def probe_at_position(x, y, z=None, nearest=False, starting_cell=None,
                      starting_zone=None, zones=None, dataset=None, frame=None):
    """Returns field values at a point in space.

    .. note::

        The position is taken according to the axis assignments of the `Frame`
        which may be any of the associated variables in the `Dataset` and not
        necessarily ``(X, Y, Z)``. See: `Cartesian3DFieldAxis.variable`.

    Parameters:
        x,y,z (`float`, *z* is optional): position to probe for field values.
        nearest (`bool`): Returns the values at the nearest node to the given
            position. Probe position must be inside the volume of the data
            being queried, otherwise this will return `None`.
        starting_cell (3-`tuple` of `integers <int>`, optional):
            The ``(i,j,k)``-index of the cell to start looking for the given
            position. This must be used with ``starting_zone``.
        starting_zone (`Zone <data_access>`, optional): The first zone to start
            searching. This is required only when ``starting_cell`` is
            specified.
        zones (`list` of `Zones <data_access>`, optional): Limits the search to
            the given zones. `None` implies searching all zones. (default:
            `None`)
        dataset (`Dataset`, optional): The `Dataset` to probe. (defaults to
            the active `Dataset`.)
        frame (`Frame`, optional): The `Frame` which determines the spatial
            variable assignment ``(X,Y,Z)``. (defaults to the active `Frame`.)

    Returns:
        `namedtuple <collections.namedtuple>`: ``(data, cell, zone)``:

            ``data`` (`list` of `floats <float>`)
                The values of each variable in the dataset at the given
                position.
            ``cell`` (3-`tuple` of `integers <int>`)
                ``(i,j,k)`` of the cell containing the given position.
            ``zone`` (`Zone <data_access>`)
                Zone containing the given position

    .. note:: Returns `None` if the position can't be probed.

        This method will return `None` if the position is outside the volume
        of the data being queried. This means one should capture the results
        in a single variable and test it against `None` before proceeding::

            result = tp.data.query.probe_at_position(1.0, 2.0, 3.0)
            if result is None:
                print('probe failed.')
            else:
                data, cell, zone = result

        Additionally, with Tecplot 360 versions 2018 R1 and later, this
        function will raise an exception if Tecplot 360 was interrupted via the
        GUI during the probe operation.
    """
    if __debug__:
        if frame and dataset and frame.dataset != dataset:
            msg = ('Dataset must be attached to the input Frame: {} != {}'.
                   format(repr(frame.dataset), repr(dataset)))
            raise TecplotValueError(msg)
        if (starting_cell is None) ^ (starting_zone is None):
            msg = 'starting_cell option requires an associated starting_zone'
            raise TecplotLogicError(msg)

    if dataset is None:
        if frame is None:
            frame = layout.active_frame()
        dataset = frame.dataset
    elif frame is None:
        frame = dataset.frame

    with frame.activated():
        if starting_cell is None:
            start_with_local_cell = False
            i, j, k = 0, 0, 0
            starting_zone_index = 0
        else:
            start_with_local_cell = True
            i, j, k = (x+1 for x in starting_cell)
            starting_zone_index = starting_zone.index

        allocd = []
        if zones is not None:
            zones = IndexSet(*zones)
            allocd.append(zones)

        data = (max(3, dataset.num_variables)*c_double)()

        try:
            result = _tecutil.ProbeAtPosition(
                x, y, z or 0,
                i, j, k,
                IJKPlanes.Volume.value,
                starting_zone_index+1,
                start_with_local_cell,
                data,
                zones,
                z is not None,
                False,
                nearest)
            success, i, j, k, plane, zone_index = result
        except TecplotSystemError as e:
            if 'Assertion' in str(e):
                raise
            success = False

        if not success:
            try:
                if _tecutil.InterruptCheck():
                    raise TecplotInterruptError()
            except AttributeError:
                pass  # InterruptCheck added to TecUtilChecked in SDK 2018.1
            return None

        cell = (Index(i-1), Index(j-1), Index(k-1))
        zone_index = Index(zone_index-1)

        for a in allocd:
            a.dealloc()

        ProbeResult = namedtuple('ProbeResult', ['data', 'cell', 'zone'])
        return ProbeResult(data[:], cell, dataset.zone(zone_index))


@lock()
def probe_on_surface(positions=((0,),(0,),(0,)), zones=None, variables=None,
                     probe_nearest=ProbeNearest.Position, obey_blanking=True,
                     num_nearest_nodes=20, tolerance=1e-5, dataset=None,
                     frame=None):
    """Returns field values at points on a surface closest the points given.

    .. note::

        The positions are processed according to the axis assignments of the
        `Frame` which may be any of the associated variables in the `Dataset`
        and not necessarily (but usually) ``(X, Y, Z)``. See:
        `Cartesian3DFieldAxis.variable`.

    Parameters:
        positions (2D `float` array): Array of points to probe dimensioned by
            ``(3, N)`` where the first dimension corresponds to ``(x, y, z)``.
            A 1D `float` array is accepted for single point probes, however
            this should be avoided when probing several positions as the
            internal algorithm is optimized for probing many positions at once.
        zones (`list` of `Zones <data_access>`, optional): Limits the search to
            the given zones. `None` implies searching all active relevant
            surface zones including surfaces of ordered volume zones. To search
            FE or polygonal volume boundaries, include the volume zones in this
            list. (default: `None`)
        variables (`list` of `Variables <Variable>`, optional): The variables
            within the dataset to probe. `None` implies all variables.
            (default: `None`)
        probe_nearest (`ProbeNearest`, optional): Probe at the nodal location
            (`ProbeNearest.Node`) or interpolate to nearest location on the
            surface (`ProbeNearest.Position`, default). The return parameter
            **cells_or_nodes** will be cells if set to `ProbeNearest.Position`
            (default), or nodes if set to `ProbeNearest.Node`.
        obey_blanking (`bool`, optional): Do not search blanked cells according
            the frame's style settings. (default: `True`)
        num_nearest_nodes (`integer <int>`, optional): Only consider surface
            cells that contain one of the closest ``N`` nodes to the probed
            position. For highly varying surfaces, the nearest cell may or may
            not contain the nearest nodes to the probe position and so this
            value should be increased accordingly, however doing so increases
            the search-space linearly. (default: 20)
        tolerance (`float`, optional): The percentage of the longest cartesian
            ``(x, y, z)`` dimension subtended by the polygons of the surface.
            This is used in several parts of the algorithm to find the nearest
            position on the surface zones and should be increased when probing
            imprecise nodal position data. (default: 1e-5)
        dataset (`Dataset`, optional): The `Dataset` to probe. (defaults to
            the active `Dataset`.)
        frame (`Frame`, optional): The `Frame` which determines the spatial
            variable assignment ``(X,Y,Z)``. (defaults to the active `Frame`.)

    Returns:
        `namedtuple <collections.namedtuple>`: ``(data, cells_or_nodes, planes,
        zone)``:

            ``data`` (`list` of `floats <float>`)
                Flattened `float` array which can be reshaped to ``(V, N)``
                where ``V`` is the number of variables returned (either the
                number of variables in the dataset or the length of
                **variables** input parameter) and ``N`` is the number of
                points probed.
            ``cells_or_nodes`` (`list` of `integers <int>`)
                The index to the cells (or nodes if `ProbeNearest.Node` was
                passed in to **probe_nearest**) containing the returned
                positions.
            ``planes`` (`list` of `IJKPlanes`)
                For ordered zones, these are the plane-orientations of the
                cells for each probed position.
            ``zones`` (`list` of `Zones <data_access>`)
                Zones containing the given positions.

    .. versionadded:: 2018.1
        Probe on surface requires Tecplot 360 2018 R1 or later.

    .. note:: The frame's plot type must be set to `PlotType.Cartesian3D`

        Probe on surface requires the spatial variables to be set according to
        the frame's style. This can be done by setting the plot type to
        `PlotType.Cartesian3D`. Example::

            tp.active_frame().plot_type = tp.constant.PlotType.Cartesian3D

        For probing on 2D data, use `probe_at_position()`.

    .. note:: Linear zones will always return nearest nodal values.

        If linear zones, which are ignored by default, are included in the
        **zones** parameter, the resulting values on that zone will always be
        nodal and no interpolation on the position will be done.

    .. note:: Irregular or jaggged surfaces may behave poorly.

        For performance reasons, this algorithm has the potential to miss the
        closest position on highly varying surfaces. This can be addressed by
        first increasing **num_nearest_nodes** to search more of the zones and
        then by increasing the **tolerance** to allow for imprecise position
        data.

    Example usage:

    .. code-block:: python
        :emphasize-lines: 14,24

        >>> from os import path
        >>> import numpy as np
        >>>
        >>> import tecplot as tp
        >>> from tecplot.constant import PlotType
        >>>
        >>> examples = tp.session.tecplot_examples_directory()
        >>> datafile = path.join(examples, 'SimpleData', 'F18.plt')
        >>> ds = tp.data.load_tecplot(datafile)
        >>> fr = tp.active_frame()
        >>> fr.plot_type = PlotType.Cartesian3D
        >>>
        >>> # probe a single point
        >>> res = tp.data.query.probe_on_surface((13.5, 4.0, 0.6 ))
        >>> print(res.data)
        (13.499723788684996, 3.9922783797612795, 0.49241572276992346,
        0.0018958827755862578, 0.07313805429221854, 0.997276718375976,
        0.06335166319722907)
        >>>
        >>> # probe multiple points
        >>> points = np.array([[13.5,  4.0, 0.6],  # just above starboard wing
        >>>                    [13.5, -4.0, 0.6]]) # just above port wing
        >>>
        >>> res = tp.data.query.probe_on_surface(points.transpose())
        >>> values = np.array(res.data).reshape((-1, len(points))).transpose()
        >>>
        >>> # print probed position and the result of the probe
        >>> for pt, v in zip(points, values):
        >>>     print(pt, v)
        [ 13.5   4.    0.6] [  1.34997238e+01   3.99227838e+00   4.92415723e-01
           1.89588278e-03   7.31380543e-02   9.97276718e-01   6.33516632e-02]
        [ 13.5  -4.    0.6] [  1.34997238e+01  -3.99227838e+00   4.92415723e-01
           1.89588278e-03   7.31380543e-02   9.97276718e-01   6.33516632e-02]
    """
    if __debug__:
        if frame and dataset and frame.dataset != dataset:
            msg = ('Dataset must be attached to the input Frame: {} != {}'.
                   format(repr(frame.dataset), repr(dataset)))
            raise TecplotValueError(msg)

    if dataset is None:
        if frame is None:
            frame = layout.active_frame()
        dataset = frame.dataset
    elif frame is None:
        frame = dataset.frame

    if not hasattr(positions[0], '__iter__'):
        positions = tuple(tuple([p]) for p in positions)

    nvariables = dataset.num_variables if variables is None else len(variables)

    with frame.activated():
        n = max(len(p) for p in positions)
        m = n * nvariables
        x = (c_double * n)(*[float(p) for p in positions[0]])
        y = (c_double * n)(*[float(p) for p in positions[1]])
        z = (c_double * n)(*[float(p) for p in positions[2]])
        v = (c_double * m)()
        cells_or_nodes = (c_int64 * n)()
        planes = (c_int32 * n)()
        zone_indices = (c_int32 * n)()

        zone_set = None if zones is None else IndexSet(zones)
        var_set = None if variables is None else IndexSet(variables)
        try:
            if not _tecutil.ProbeOnSurface(n, x, y, z, zone_set, var_set,
                                           ProbeNearest(probe_nearest).value,
                                           obey_blanking, num_nearest_nodes,
                                           tolerance, v, cells_or_nodes,
                                           planes, zone_indices):
                raise TecplotSystemError()
        finally:
            if zone_set is not None:
                zone_set.dealloc()
            if var_set is not None:
                var_set.dealloc()

        cells_or_nodes = tuple(cells_or_nodes)
        planes = tuple(IJKPlanes(i) for i in planes)
        zones = tuple(dataset.zone(i) for i in zone_indices)

        SurfaceProbeResult = namedtuple('SurfaceProbeResult',
            ['data', 'cells_or_nodes', 'planes', 'zones'])
        return SurfaceProbeResult(tuple(v), cells_or_nodes, planes, zones)
