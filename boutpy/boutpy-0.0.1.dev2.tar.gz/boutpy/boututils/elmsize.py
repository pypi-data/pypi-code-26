#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Elmsize calculation. """

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ['elmsize']

__date__ = '09/13/2017'
__version__ = '0.1.1'
__author__ = 'J.G. Chen'
__email__ = 'cjgls@pku.edu.cn'

import numpy as np

from boutpy.boutdata.boutgrid import boutgrid
from boutpy.boututils.functions import get_nth

# TODO: create constant file
mu0 = 4.0e-7 * np.pi
e_charge = 1.6022e-19


def elmsize(dcp, var0, gridfile, xlim=None, ylim=None, yind=None, norm=1.0):
    """calculate elmsize.

    Parameters
    ----------
    dcp : 2D/3D array
        dc part of normalized perturbed var
    var0 : 2D array
        normalized equilibrium profile
    gridfile : str|dict
        path to gridfile or dict object of grid
    xlim : 2-elements list, optional, default: None
        x-index range for the calculation,
        using [0, peak of Grad **P0**] for circular geometry and
        [0, seperatrix] for divertor geometry by default.
    ylim : 2-elements list, optional, default: None
        y-index range for the calulation. whole range is used by default.
    yind : int, optional, default: None
        y-index for the 1D elm size calculation.
    norm : ['3f', '6f', float], optional, default: 1.0
        normalization factor for ``var0``.

        ['3f', '6f'] only work for ``var0`` is pressure.
        - '3f': in 3field code, total pressure normalized by 2*mu0/(Bbar*Bbar)
        - '6f': in 6field code, total pressure normalized by
            Nbar * density (m^3) * e * Tebar(eV)

    Returns
    -------
    ret : dict
    s1/2/3 : float
        1d/2d/3d elm size
    E_loss : float
        ELM energy loss in unit [J] if ``var0`` is pressure and the
        normalization factor ``norm`` is provided.
    E_total : float
        pedestal stored energy in unit [J] if ``var0`` is pressure and the
        normalization factor ``norm`` is provided.

    """

    dcp_size = dcp.shape
    var0_size = var0.shape
    nx, ny = var0_size
    assert var0.ndim == 2, "var0 must be 2D(x, y)"
    assert dcp.ndim >= 2, "dcp must be 2D(x, y) or 3D(x, y, t)"
    assert var0_size == dcp_size[:2], ("dcp should be same size with var0"
                                       "in first two dimensions")

    grid = boutgrid(gridfile)

    # get outer mid-plane index
    psin, yind_imp, yind_omp = grid.get_psin('omp', index=True)
    if xlim:
        xmin, xmax = get_nth(xlim, end=nx-1).astype(int)
    else:
        xmin = 0
        if grid.topology():
            # with x point
            xind_sep, _ = grid.get_xind(psin=1.0)
            xmax = xind_sep
        else:
            print("NOTE: using xind of peak position of P0 profile in grid!")
            xmax, _ = grid.get_peak_GradP0()

    if ylim:
        ymin, ymax = get_nth(ylim, end=ny-1).astype(int)
    else:
        ymin, ymax = 0, ny - 1

    assert xmin <= xmax
    assert ymin <= ymax

    print("radial domain: {}".format(psin[[xmin, xmax]]))
    print("x-index: [{}, {}]".format(xmin, xmax))
    print("y-index: [{}, {}]".format(ymin, ymax))

    if dcp.ndim == 2:
        mydcp = dcp[xmin:xmax + 1, ymin:ymax + 1, None]
    else:
        mydcp = dcp[xmin:xmax + 1, ymin:ymax + 1, :]
    myvar0 = var0[xmin:xmax + 1, ymin:ymax + 1]

    # data from grid
    dtheta = grid['dy'][xmin:xmax + 1, ymin:ymax + 1]         # poloidal angle
    psixy = grid['psixy'][xmin:xmax + 1, ymin:ymax + 1]
    Rxy = grid['Rxy'][xmin:xmax + 1, ymin:ymax + 1]
    Bp = grid['Bpxy'][xmin:xmax + 1, ymin:ymax + 1]
    hthe = grid['hthe'][xmin:xmax + 1, ymin:ymax + 1]

    if yind is None:
        yind = yind_omp

    dpsi = np.gradient(psixy, axis=0)

    Jacobian = hthe / Bp
    dV = Jacobian * dpsi * dtheta   # constant in z-direction

    # pedestal stored energy
    E0_3d = 2. * np.pi * np.sum(myvar0 * dV)
    E0_2d = np.sum(myvar0 * dV / Rxy)
    E0_1d = np.sum(myvar0[:, yind] * dpsi[:, yind] /
                   (Rxy[:, yind] * Bp[:, yind]))

    # energy loss
    dE_3d = 2. * np.pi * np.sum(mydcp * dV[..., None], axis=(0, 1))
    dE_2d = np.sum(mydcp * (dV / Rxy)[..., None], axis=(0, 1))
    dE_1d = np.sum(mydcp[:, yind, :] * dpsi[:, yind, None] /
                   (Rxy[:, yind, None] * Bp[:, yind, None]), axis=0)

    ret = {}
    # elm size
    ret['s1'] = - dE_1d / E0_1d
    ret['s2'] = - dE_2d / E0_2d
    ret['s3'] = - dE_3d / E0_3d

    if norm == '3f':
        print("WARNING: 'norm = 3f' noly for elmsize calculated by pressure")
        Bbar = grid['bmag']
        norm = Bbar * Bbar / (2.0 * mu0)
        print("pressure normalized by: {:.2f} Pa".format(norm))
    elif norm == '6f':
        print("WARNING: 'norm = 6f' noly for elmsize calculated by pressure")
        print("         the unit for density in the grid must be 10^20 m^-3")
        density = 1.e20     # unit for density profiles in grid
        Nbar = grid.get('Nixexp', 1.0)
        Tebar = grid.get('Te_x', 1.0)       # [eV]
        print("         Nbar = {:.2f} * {:.2e} m^-3".format(Nbar, density))
        norm = Nbar * density * e_charge * Tebar
        print("pressure normalized by: {:.2f} Pa".format(norm))
    else:
        assert isinstance(norm, (int, float)), (
            "normalization factor `norm` should be a float number")
        print("equilibrium profile normalized by: {:.2f}".format(norm))

    ret['E_loss'] = - dE_3d * norm     # energy loss, unit J
    ret['E_total'] = E0_3d * norm      # total energy, unit J

    return ret
