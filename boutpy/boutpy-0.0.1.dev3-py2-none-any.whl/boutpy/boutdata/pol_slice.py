"""Takes a 3D variable, and returns a 2D slice at fixed toroidal angle.

N sets the number of times the data must be repeated for a full torus,
e.g. n=2 is half a torus zangle gives the (real) toroidal angle of the result
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ['pol_slice', 'polslice']

import numpy as np

from boutpy.boutdata.boutgrid import boutgrid

def zinterp(var3d, yind, zind):
    """3points Polynomial Interpolation

    Parameters
    ----------
    var3d : 3d-array
        target 3d-array which has shape (nx, ny, nz)
    yind : 1d-array, scalar
        the basic y index, (ny, )
    zind : 2d-array
        target zind for interpolation, in shape (nx, n) if ny=1, or
        (nx, ny) if ny != 1.

    Returns
    -------
    var_interp : ndarray
        in shape (nx, n)

    """

    nx, n = zind.shape
    if not isinstance(yind, int):
        ny = np.asarray(yind).shape[1]
        assert ny == n
    z0 = np.floor(zind)

    z0 = z0.astype(int)
    # Make z0 between 0 and (nz-2)
    z0 = ((z0 % (nz - 1)) + (nz - 1)) % (nz - 1)

    # Get z+ and z-
    zp = (z0 + 1) % (nz - 1)
    zm = (z0 - 1 + (nz - 1)) % (nz - 1)

    dz = (zind - z0)

    # 3-Points Polynomial Interpolation
    var_interp = np.zeros([nx, n])
    for j in range(n):
        for i in range(nx):
            p = dz[i, j]
            iyind = yind if isinstance(yind, int) else j
            var_interp[i, j] = (
                0.5 * p * (p - 1.0) * var3d[i, iyind, zm[i, j]] +
                (1.0 - p * p) * var3d[i, iyind, z0[i, j]] +
                0.5 * p * (p + 1.0) * var3d[i, iyind, zp[i, j]])
    return var_interp


def polslice(var3d, gridfile, n=1, zangle=0.0, profile=None):
    """Return a 2D slice by interpolation.

    Parameters
    ----------
    var3d : 3D-array
        3D vars in [x, y, z] order
    gridfile : str | dict
        path to gridfile (srt) or dict data of grid (dict)
    n : int, optional, default: 1
        zperiod used in simulation
    zangle : float, optional, default: 0
        get result at toroidal angle ``zangle`` (in degree).
    profile : ndarray, optional, default: None
        equilibrium profile.

    Returns
    -------
    var2d : 2D-array
        value of poloidal cross-section at toroidal angle ``zangle``.

    """

    raise NotImplementedError("Double check required!")
    n = int(n)
    zangle = np.pi * float(zangle) / 180.0

    s = np.shape(var3d)
    if len(s) != 3:
        raise ValueError("pol_slice expects a 3D variable")

    nx, ny, nz = s

    # TODO: should be n * nz
    dz = 2. * np.pi / float(n * (nz - 1))

    # Open the grid file
    gf = boutgrid(gridfile)
    Rxy = gf['Rxy']
    Zxy = gf['Zxy']

    # Check the grid size is correct
    if [gf["nx"], gf["ny"]] != [nx, ny]:
        raise ValueError("Missmatched grid size: {} --> {}".format(
            [gf['nx'], gf['ny']], [nx, ny]))

    # Get the toroidal shift
    try:
        if "qinty" in gf.keys():
            zShift = gf['qinty']
            print("Using qinty as toroidal shift angle")
        else:
            zShift = gf["zShift"]
            print("Using zShift as toroidal shift angle")
    except:
        raise ValueError("ERROR: Neither qinty nor zShift found")

    var2d = np.zeros([nx, ny])

    ######################################
    # Perform 2D slice
    zind = (zangle - zShift) / dz

    # number of points between grid points: y & y + 1
    nskip = (np.abs(zShift[:, 1:] - zShift[:, :-1]) / dz - 1).max(axis=0)
    nskip = nskip.round().astype(int)

    ny_interp = int(np.sum(nskip)) + ny
    print("Number of poloidal points in output: ", ny_interp)
    var_interp = np.zeros([nx, ny_interp])
    rxy_interp = np.zeros([nx, ny_interp])
    zxy_interp = np.zeros([nx, ny_interp])

    # map original grid points
    ypos = np.append([0], nskip.cumsum()) + np.arange(ny)
    var_interp[:, ypos] = zinterp(var3d, np.arange(ny), zind)
    rxy_interp[:, ypos] = Rxy
    zxy_interp[:, ypos] = Zxy

    # map points between grid points
    dzi = (zind[:, 1:] - zind[:, :-1]) / (nskip + 1.)
    for y in range(ny - 1):
        y_yind = np.arange(nskip[y]).reshape(1, nskip[y])
        print(y, ypos[y] + 1)
        # zindex
        zi = zind[:, y].reshape(nx, 1) + y_yind * dzi[:, y][:, None]
        # weighting: (1, nskip[y])
        w = (y_yind + 1) / (nskip[y] + 1.0)
        var_interp[:, ypos[y] + 1:ypos[y + 1]] = (
            w * zinterp(var3d, y + 1, zi) +
            (1 - w) * zinterp(var3d, y, zi))
        if profile is not None:
            var_interp[:, ypos[y] + 1:ypos[y + 1]] += (
                w * profile[:, y + 1][:, None] +
                (1 - w) * profile[:, y][:, None])
        rxy_interp[:, ypos[y] + 1:ypos[y + 1]] = (w * Rxy[:, y + 1][:, None] +
                                                  (1 - w) * Rxy[:, y][:, None])
        zxy_interp[:, ypos[y] + 1:ypos[y + 1]] = (w * Zxy[:, y + 1][:, None] +
                                                  (1 - w) * Zxy[:, y][:, None])

    return rxy_interp, zxy_interp, var_interp


def pol_slice(var3d, gridfile, n=1, zangle=0.0):
    """data2d = pol_slice(data3d, 'gridfile', n=1, zangle=0.0)

    Parameters
    ----------
    var3d : 3D-array
        3D vars in [x, y, z [, t]] order
    gridfile : str
        path to gridfile
    n : int, optional, default: 1
        zperiod used in simulation
    zangle : float, optional, default: 0
        get result at toroidal angle ``zangle`` (in degree)

    Returns
    -------
    var2d : 2D-array
        value of poloidal cross-section at toroidal angle ``zangle``.

    """

    n = int(n)
    zangle = np.pi * float(zangle) / 180.

    s = np.shape(var3d)
    if len(s) != 3:
        raise ValueError("pol_slice expects a 3D variable")

    nx, ny, nz = s

    dz = 2. * np.pi / float(n * (nz - 1))

    # Open the grid file
    gf = boutgrid(gridfile)
    Rxy = gf['Rxy']
    Zxy = gf['Zxy']

    # Check the grid size is correct
    if [gf["nx"], gf["ny"]] != [nx, ny]:
        raise ValueError("Missmatched grid size: {} --> {}".format(
            [gf['nx'], gf['ny']], [nx, ny]))

    # Get the toroidal shift
    try:
        if "qinty" in gf.keys():
            zShift = gf['qinty']
            print("Using qinty as toroidal shift angle")
        else:
            zShift = gf["zShift"]
            print("Using zShift as toroidal shift angle")
    except:
        raise ValueError("ERROR: Neither qinty nor zShift found")

    var2d = np.zeros([nx, ny])

    ######################################
    # Perform 2D slice

    zind = (zangle - zShift) / dz
    z0 = np.floor(zind)
    print(z0.shape)
    z0 = z0.astype(int)
    p = zind - z0.astype(float)

    # Make z0 between 0 and (nz-2)
    z0 = ((z0 % (nz - 1)) + (nz - 1)) % (nz - 1)

    # Get z+ and z-
    zp = (z0 + 1) % (nz - 1)
    zm = (z0 - 1 + (nz - 1)) % (nz - 1)

    # There may be some more cunning way to do this indexing
    for x in np.arange(nx):
        for y in np.arange(ny):
            var2d[x, y] = 0.5 * p[x, y] * (p[x, y] - 1.0) * \
                var3d[x, y, zm[x, y]] + \
                (1.0 - p[x, y] * p[x, y]) * var3d[x, y, z0[x, y]] + \
                0.5 * p[x, y] * (p[x, y] + 1.0) * var3d[x, y, zp[x, y]]

    return var2d
