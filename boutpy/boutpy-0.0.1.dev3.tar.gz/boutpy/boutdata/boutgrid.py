"""Calculations based on data in netcdf grid.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ['boutgrid']

__date__ = '07162017'
__version__ = '0.1.0'
__author__ = 'J.G. Chen'
__email__ = 'cjgls@pku.edu.cn'

import numpy as np
import scipy.integrate as si
from collections import OrderedDict

from boutpy.boututils.fileio import file_import

# TODO: create constant file in cgs/SI units
mu0 = 4. * np.pi * 1e-7


class boutgrid(OrderedDict):
    """BOUT++ grid object based on netcdf grid.

    Attributes
    ----------
    yind_omp : int
        Yind of outer mid-plane
    yind_imp : int
        Yind of inner mid-plane
    nx, ny : int
        grid size
    psin : 2D array
        Normalized flux
    psin95 : float
        psin nearest to the 0.95
    psin_limit : 1D array
        [psin_min, psin_max]
    q : 1D array
        safety factor
    xind_psin95 : int
        xind of psin nearest to the 0.95

    Methods
    -------
    get_alpha(V0=0, pressure=None)
        Return local and global normalized pressure gradient.
    get_magnetic_shear(V0=0)
        Return local and global magnetic shear s.
    get_minor_r(method=1)
        Return minor radius.
    get_peak_GradP0()
        Return peak position of Gradient P0 at outer mid-plane.
    get_psin(yind=None, index=False, verbose=True)
        Get normalized psin from gridfile.
    get_xind(psin=0.95)
        Return xind of psin at outer mid-plane to the ``psin``.
    get_q(q95=False)
        Return Safety Factor q.
    get_volume(V0=0)
        Return volume enclosed by flux surface.
    surface_average(var, area=False)
        Perform surface average.
    topology()
        Check topology of the grid.

    """

    def __init__(self, gridfile):
        """Initiate grid object.

        Parameters
        ----------
        gridfile : str or dict
            name of grid file or dict of grid data

        """

        OrderedDict.__init__(self)

        try:
            if isinstance(gridfile, str):
                self.update(sorted(file_import(gridfile).items()))
            elif isinstance(gridfile, dict):
                self.update(sorted(gridfile.items()))
        except:
            print("ERROR: {} is not exists\n".format(gridfile))
            raise

        self.psin, self.yind_imp, self.yind_omp = self.get_psin(index=True)
        self.psin_limit = self.psin[[0, -1], self.yind_omp]
        self.xind_psin95, self.psin95 = self.get_xind(psin=0.95)
        self.q = self.get_q()
        self.nx, self.ny = self['Rxy'].shape

    def get_alpha(self, V0=0, pressure=None):
        r"""Return local and global normalized pressure gradient.

        local :math:`\alpha` [#1]_:

        .. math::

            \alpha = - \dfrac{2 \mu_0 q^2R_0}{B^2}\dfrac{dP_0}{dr}.

        global :math:`\alpha` [#2]_:

        .. math::

            \alpha = - \dfrac{2 \partial_\psi V}{(2\pi)^2}
                     \left(\dfrac{V}{2 \pi^2 R_0}\right)^{1/2}
                     \mu_0 \dfrac{dP}{d\psi}.

        in which the :math:`V` is the volume enclosed by the flux surface.

        In BOUT++ grid, it can be expressed as:

        .. math::

            V(\psi) &= \int_{0}^{\psi} \int_0^{2\pi} \int_0^{2\pi}
                      J(\psi, \theta) d\psi d\theta d\zeta \\
                    &= 2\pi \int_{0}^{\psi} \int_0^{2\pi}
                      J(\psi, \theta) d\psi d\theta \\
                    &= V_0 + 2\pi \int_{\psi_{in}}^{\psi} \int_0^{2\pi}
                      J(\psi, \theta) d\psi d\theta

        where the Jacobian is :math:`J(\psi, \theta) = J(x, y) = hthe/Bp`.
        The volume inside the inner boundary :math:`\psi_{in}` should be
        calculated separately:

        .. math::

            V_0 = 2\pi \int_{\psi_0}^{\psi_{in}} \int_0^{2\pi}
                 J(\psi, \theta) d\psi d\theta

        Parameters
        ----------
        V0 : float, optional, default: 0
            the volume inside the inner boundary :math:`\psi_{in}`. Generally,
            the grid excludes the core region. It should be calculated
            separately: generate new grid with :math:`\psi` range
            :math:`[\psi_0, \psi_{in}]` and then calculate :math:`V_0`.
        pressure : ndarray, optional, default: None
            1D/2D array, using this pressure to calculate the alpha,
            if ``pressure == None`` by default, using the pressure in the
            grid.

        Returns
        -------
        tuple(a_local, a_global)
        a_local, a_global : tuple of ndarray
            return local alpha and global alpha

        References
        ----------
        .. [#1] `P.W. Xi, et. al., Phys. Rev. Lett. 112, 085001 (2014);
               <https://doi.org/10.1103/PhysRevLett.112.085001>`_
        .. [#2] `R.L. Miller, et. al., Physics of Plasmas 5, 973 (1998);
               <http://dx.doi.org/10.1063/1.872666>`_

        """

        minor_r = self.get_minor_r()
        q = self.get_q()

        psixy = self['psixy'][:, self.yind_omp]
        B0 = self['Bxy'][:, self.yind_omp]
        R0 = self['rmag']

        if pressure is not None:
            shape = np.asarray(pressure).shape
            ndim = len(shape)
            if ndim == 2:
                assert shape == (self['nx'], self['ny'])
                P0 = pressure[:, self.yind_omp]
            elif ndim == 1:
                assert shape[0] == self['nx']
                P0 = pressure
            else:
                raise ValueError("The given pressure should be in shape "
                                 "({}, {}) or ({},)".format(
                                     self['nx'], self['ny'], self['nx']))
        else:
            P0 = self['pressure'][:, self.yind_omp]

        ddr_P0 = np.gradient(P0, minor_r)
        a_local = - 2 * mu0 * q**2 * R0 / (B0**2) * ddr_P0

        V = self.get_volume(V0=V0)
        ddpsi_P0 = np.gradient(P0, psixy)
        ddpsi_V = np.gradient(V, psixy)
        a_global = - 2 * ddpsi_V / ((2 * np.pi)**2) * \
            np.sqrt(V / (2 * np.pi**2 * R0)) * mu0 * ddpsi_P0

        return a_local, a_global

    def get_magnetic_shear(self, V0=0):
        r"""Return local and global magnetic shear s.

        local megnetic shear s [#3]_:

            .. math::

                s = \dfrac{r}{q}\dfrac{dp}{dr}

        global megnetic shear s [#4]_ [#5]_:

            .. math::

                s & = \dfrac{2V \partial_\psi q}{\partial_\psi V} \\
                  & = 2V \dfrac{\partial q(\psi)}{\partial V(\psi)} \\
                  & \approx \dfrac{r}{q}\dfrac{dp}{dr}

        in which the :math:`V` is the volume enclosed by the flux surface.

        Returns
        -------
        tuple(s_local, s_global)
        s_local, s_global : tuple of ndarray
            return local shear and global shear

        References
        ----------
        .. [#3] `P.W. Xi, et. al., Phys. Rev. Lett. 112, 085001 (2014);
               <https://doi.org/10.1103/PhysRevLett.112.085001>`_
        .. [#4] `R.L. Miller, et. al., Physics of Plasmas 5, 973 (1998);
               <http://dx.doi.org/10.1063/1.872666>`_
        .. [#5] `F.M. Levinton, et. al., Phys. Rev. Lett. 75, 4417 (1995);
               <https://doi.org/10.1103/PhysRevLett.75.4417>`_

        """

        # NOTE: in Xu's 2014 POP, the magnetic shear s
        #       using minor_r = Rxy[:, 32] to get local s.
        minor_r = self.get_minor_r()
        q = self.get_q()
        s_local = minor_r * np.gradient(q, minor_r) / q

        V = self.get_volume(V0=V0)

        s_global = 2 * V * np.gradient(q, V)

        return s_local, s_global

    def get_minor_r(self, method=1):
        r"""Retrun minor radius.

        Parameters
        ----------
        self : str or dict
            name of grid file or dict of grid data

        method : 1, 2, 3, optional, default: 1.
            method to calculate the minor radius.

            * ``method = 1``: :math:`r=(R_{xy}[:, omp] - R_{xy}[:, imp])/2`;
            * ``method = 2``: :math:`r=h_{\theta}=\dfrac{1}{|\nabla \theta|}`;
            * ``method = 3``: :math:`r = R_{xy}[:, omp] - R_0`.

        Returns
        -------
        minor_r : ndarray
            1D array of minor radius.

        """

        if method == 1:
            minor_r = (self['Rxy'][:, self.yind_omp] -
                       self['Rxy'][:, self.yind_imp]) / 2
        elif method == 2:
            minor_r = self['hthe'][:, self.yind_omp]
        elif method == 3:
            minor_r = self['Rxy'][:, self.yind_omp] - self['rmag']

        return minor_r

    def get_peak_GradP0(self, pressure=None):
        r"""Return peak position of Gradient P0 at outer mid-plane.

        Parameters
        ----------
        pressure : ndarray, optional, default: None
            1D/2D array, using this pressure to calculate the alpha,
            if ``pressure == None`` by default, using the pressure in the grid.

        Returns
        -------
        tuple(index, psin)
        index: int
            index of peak position of Gradient P0.
        psin: float
            psin of peak position of Gradient P0.

        """

        if pressure is not None:
            shape = np.asarray(pressure).shape
            ndim = len(shape)
            if ndim == 2:
                assert shape == (self['nx'], self['ny'])
                P0 = pressure[:, self.yind_omp]
            elif ndim == 1:
                assert shape[0] == self['nx']
                P0 = pressure
            else:
                raise ValueError("The given pressure should be in shape "
                                 "({}, {}) or ({},)".format(
                                     self['nx'], self['ny'], self['nx']))
        else:
            P0 = self['pressure'][:, self.yind_omp]

        gradP0 = np.gradient(P0, self.psin[:, self.yind_omp])

        xind = gradP0.argmin()

        return xind, self.psin[xind, self.yind_omp]

    def get_psin(self, yind=None, index=False, verbose=False):
        """Get normalized psi_n from gridfile

        .. math::

            \psi_n = \dfrac{\psi_{xy} - \psi_{axis}}{\psi_{bndry}
                     - \psi_{axis}}

        Parameters
        ----------
        yind : index of y-axis, string ``omp``, ``imp``
            by default the psi_n is a 2D array. when yind is specified,
            only 1D psi_n is calculated. for cbm grid serials, the psi_n
            is independent on the yind.
            ``omp``: get psi_n at outer mid-plane
            ``imp``: get psi_n at inner mid-plane
        index : bool, optional, default: False
            if ``index = True``, then return indices of both outer & inner
            mid-plane
        verbose : bool, optional, default: True
            output more information

        Returns
        -------
        psi_n :  1D or 2D array according to the yind option
        yind_imp, yind_omp : int
            y indices of inner & outer mid-plane
        If ``index = True``, then return tuple(psin, yind_imp, yind_omp),
        otherwise return ``psi_n`` by defualt.

        """

        try:
            x = np.r_[self['jyseps1_1'] + 1:self['jyseps2_1'] + 1,
                      self['jyseps1_2'] + 1:self['jyseps2_2'] + 1]
            yind_omp = x[self['Rxy'][-1, x].argmax()]
            yind_imp = x[self['Rxy'][-1, x].argmin()]
            try:
                assert yind_omp == x[self['Rxy'][0, x].argmax()]
                assert yind_imp == x[self['Rxy'][0, x].argmin()]
            except:
                print("WARNING:")
                print("    yind_omp/imp calculated by Rxy of "
                      "xind=0, -1 are different!!!")
                print("    xind=0: yind_omp/imp = {}/{}".format(
                    x[self['Rxy'][0, x].argmax()],
                    x[self['Rxy'][0, x].argmin()]))
                print("    xind=-1: yind_omp/imp = {}/{}".format(
                    x[self['Rxy'][-1, x].argmax()],
                    x[self['Rxy'][-1, x].argmin()]))
            if verbose:
                print("NOTE: outer midplane: yind = ", yind_omp)
                print("      inner midplane: yind = ", yind_imp)
            if yind is not None:
                if yind == "omp":
                    if verbose:
                        print("get psin at outer mid-plane")
                    yind = yind_omp
                elif yind == 'imp':
                    if verbose:
                        print("get psin at inner mid-plane")
                    yind = yind_imp
                else:
                    if not isinstance(yind, (tuple, list, np.ndarray)):
                        print("WARNING: value of *yind* is not recognized!!!!"
                              "\n         set to outer mid-plane!!")
                        yind = yind_omp
                    if verbose:
                        print("get psin at yind = ", yind)
                psi_n = ((self['psixy'][:, yind] - self['psi_axis']) /
                         (self['psi_bndry'] - self['psi_axis']))
            else:
                psi_n = ((self['psixy'] - self['psi_axis']) /
                         (self['psi_bndry'] - self['psi_axis']))
        except KeyError:
            print("KeyError: Check gridfile again")
            raise

        if index:
            if verbose > 1:
                print("      return tuple(psi_n, yind_imp, yind_omp)")
            return psi_n, yind_imp, yind_omp
        else:
            return psi_n

    def get_xind(self, psin=0.95):
        """Return xind of psin at outer mid-plane nearest to the ``psin``.

        Parameters
        ----------
        psin : float

        Returns
        -------
        tuple(xind, psin)
        xind : int
        psin : float

        """

        psin_omp = self.psin[:, self.yind_omp]

        if psin < psin_omp[0] or psin > psin_omp[-1]:
            print("WARNING: Target psin={} is outside the range {}"
                  .format(psin, self.psin_limit))

        xind = np.abs(psin_omp - psin).argmin()

        return xind, psin_omp[xind]

    def get_q(self, q95=False):
        r"""Return Safety Factor q.

        Safety Factor q:

        .. math::

            q = -\dfrac{\text{ShiftAngle}}{2\pi}

        Parameters
        ----------
        q95 : bool, optional, default: False
            return q at :math:`\psi_n = 0.95` if True.

        Returns
        -------
        q : scalar, nd-array
            1D array safety factor q if ``q95 = False`` by default,
            otherwise return q at :math:`\psi_n = 0.95`.

        """

        q = - self['ShiftAngle'] / (2 * np.pi)

        if q95:
            return q[self.xind_psin95]

        return q

    def get_Va(self):
        r"""Return Alfven Speed Va.
        """
        raise NotImplementedError

    def get_volume(self, V0=0):
        r"""Return volume enclosed by flux surface.

        Parameters
        ----------
        V0 : float, optional, default: 0
            the volume inside the inner boundary :math:`\psi_{in}`. Generally,
            the grid excludes the core region. It should be calculated
            separately: generate new grid with :math:`\psi` range
            :math:`[\psi_0, \psi_{in}]` and then calculate :math:`V_0`.

        """

        dpsi = np.gradient(self['psixy'], axis=0)
        hthe = self['hthe']
        dtheta = self['dy']
        Bp = self['Bpxy']
        Jacobian = hthe / Bp

        # volume enclosed by the flux surface
        V = np.zeros(self['nx'])
        for i in range(1, self['nx']):
            V[i] = V[i - 1] + np.sum(2 * np.pi * Jacobian[i, :] *
                                     dtheta[i, :] * dpsi[i, :])

        if V0 > 0:
            V += V0
        else:
            # TODO: check psixy[0] ? psi_axis
            print("WARNING: ignoring core region!")
            pass

        return V

    def surface_average(self, var, area=False, method=1):
        """ Perform surface average

        Parameters
        ----------
        var : ndarray
            3/4D variable in [x, y, z, [t]] order.
        area : bool, optional, default: False
            average by flux-surface area = (B/Bp)*dl*R*dz. By default,
            averages over poloidal angle such that surface_average(nu) = q.

        Notes
        -----
        This function is based on IDL function in
        BOUT_TOP/tools/idllib/surface_average.pro.

        """

        ndim = np.ndim(var)
        s = np.shape(var)

        dtheta = 2. * np.pi / float(self.ny)
        dl = np.sqrt(np.gradient(self['Rxy'], axis=1) ** 2
                     + np.gradient(self['Zxy'], axis=1) ** 2) / dtheta

        if area:
            dA = self['Bxy'] / self['Bpxy'] * self['Rxy'] * dl
            A = si.cumtrapz(dA, x=np.arange(self.ny), initial=0)
            theta = 2. * np.pi * A / A[:, -1:]
        else:
            # nu ~ r*Bt/(R*Bp)
            nu = dl * self['Btxy'] / (self['Bpxy'] * self['Rxy'])
            theta = si.cumtrapz(nu, x=np.arange(self.ny)*dtheta, initial=0)
            theta = 2. * np.pi * theta / theta[:, -1:]

        if ndim == 4:
            nx, ny, nz, nt = s
            result = np.zeros((nx, nt))
            for i in range(nt):
                result[:, i] = self.surface_average(
                    var[:, :, :, i].squeeze(), area=area)
        elif ndim == 3:
            nz = s[-1]
            result = si.trapz(var.mean(axis=2), x=theta) / (2. * np.pi)
        elif ndim == 2:
            result = si.trapz(var, x=theta) / (2. * np.pi)
        else:
            raise ValueError("var must be 2, 3 or 4D")

        return result

    def topology(self):
        """Return the number of xpoint and Check topology of grid.

        Returns
        -------
        nxpoint : int
            the number of xpoints

        References
        ----------
        process_grid.pro :
            BOUT_TOP/tools/tokamak_grid/gridgen
        BOUT++ Topology :
            BOUT++ user manual, section 11.1

        """

        nxpoint = 0

        if self['jyseps2_2'] - self['jyseps1_1'] == self['ny']:
            geo = "without xpoint, all flux surfaces are closed"
            assert self['ixseps1'] == self['ixseps2'] == self['nx']
        else:
            geo = None

        if self['jyseps2_1'] == self['jyseps1_2']:
            equilibrium = "SINGLE NULL (SND)"
            if geo is None:
                geo = "with one xpoint"
                nxpoint = 1
        else:
            if geo is None:
                geo = "with two xpoints"
                nxpoint = 2
            if self['ixseps1'] == self['ixseps2']:
                equilibrium = "CONNECTED DOUBLE NULL (CDND)"
            elif self['ixseps1'] < self['ixseps2']:
                equilibrium = "LOWER DOUBLE NULL (LDND)"
            else:
                equilibrium = "UPPER DOUBLE NULL (UDND)"

        print("#### The grid is {} equilibrium\n#### {}"
              .format(equilibrium, geo))
        return nxpoint
