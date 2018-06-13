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
from scipy.optimize import minimize


class LinearSolid(object):

    def __init__(self, y_j, w_j, Q, alpha=1., pl_f_ref=1., f_min=None,
                 f_max=None):
        if not len(y_j) == len(w_j):  # pragma: no cover
            raise ValueError('w_j and y_j not compatible in length')
        self.y_j = y_j
        self.w_j = w_j
        self.N = len(y_j)
        self.Q = Q
        self.alpha = alpha
        self.pl_f_ref = pl_f_ref
        self.f_min = f_min
        self.f_max = f_max

    def get_Q(self, w, exact=False):
        return self.q_linear_solid(self.y_j, self.w_j, w, exact=exact)

    @staticmethod
    def q_linear_solid(y_j, w_j, w, exact=False):
        # see van Driel et al 2014, eq 7 and 21
        Qls = np.ones_like(w)
        if exact:
            for _y_j, _w_j in zip(y_j, w_j):
                Qls += _y_j * w ** 2 / (w**2 + _w_j**2)

        Qls_denom = np.zeros_like(w)
        for _y_j, _w_j in zip(y_j, w_j):
            Qls_denom += _y_j * w * _w_j / (w**2 + _w_j**2)

        return Qls / Qls_denom

    @staticmethod
    def power_law_Q(Q, alpha, w, pl_f_ref=1.):
        return Q * (w / (2 * np.pi * pl_f_ref)) ** alpha

    @staticmethod
    def optimal_bandwidth(N):
        """
        bandwidth that results in about 1% error in fitting Q, see van Driel
        (2014), figure 4
        """
        if N == 1:
            return 0.0
        elif N == 2:
            return 0.8
        elif N == 3:
            return 1.7
        elif N == 4:
            return 2.5
        elif N == 5:
            return 3.2
        elif N == 6:
            return 3.9
        elif N > 6:
            # otherwise use linear extrapolation based on 5 and 6
            return (3.9 - 3.2) * (N - 6) + 3.9
        else:
            raise ValueError('N must be > 0')

    @classmethod
    def invert_linear_solids(self, Q=1., f_min=0.001, f_max=1., N=3,
                             nfsamp=100, maxiter=1000, fixfreq=False,
                             freq_weight=True,
                             pl_f_ref=1., alpha=0., ftol=1e-10, exact=False):

        """
        Parameters:
        Q:              clear
        f_min, fmax:    frequency band (in Hz)
        N:              number of standard linear solids
        nfsamp:         number of sampling frequencies for computation of the
                          misfit (log spaced in freqeuncy band)
        max_it:         number of iterations
        Tw:             starting temperature for the frequencies
        Ty:             starting temperature for the amplitudes
        d:              temperature decay
        fixfreq:        use log spaced peak frequencies (fixed)
        verbose:        clear
        freq_weight:    use frequency weighting to ensure better fit at high
                          frequencies
        w_ref:          reference angular frequency for power law Q
        alpha:          exponent for power law Q

        Returns:
        w_j:            relaxation frequencies, equals 1/tau_sigma in zener
                          formulation
        y_j:            coefficients of the linear solids, (Emmerich & Korn, eq
                          23 and 24)
        w:              sampling frequencies at which Q(w) is minimized
        q_fit:          resulting q(w) at these frequencies
        chil:           error as a function of iteration to check convergence,
                          Note that this version uses log-l2 norm!

        """
        # Set the starting test frequencies equally spaced in log frequency
        if (N > 1):
            w_j_test = np.logspace(np.log10(f_min), np.log10(f_max), N) * \
                2 * np.pi
        elif N == 1:
            w_j_test = np.array([(f_max * f_min)**.5 * 2 * np.pi])
        else:  # pragma: no cover
            raise ValueError('N needs to be >= 1')

        w_j_start = w_j_test.copy()

        # Set the sampling frequencies equally spaced in log frequency
        w = np.logspace(np.log10(f_min), np.log10(f_max), nfsamp) * 2 * np.pi

        # compute target Q from power law
        Q_target = self.power_law_Q(Q, alpha, w, pl_f_ref)

        # compute weights for linear frequency weighting
        if freq_weight:
            weights = w / np.sum(w) * nfsamp
        else:
            weights = np.ones_like(w)

        # initial weights y_j based on an empirical guess
        y_j_test = np.ones(N) * 6. / N

        def l2_error(Q_target, Qls, weights=1):
            # see van Driel et al 2014, eq 18
            lse = np.sum(np.log(Q_target / Qls) ** 2 * weights)
            lse /= len(Qls)
            lse = np.sqrt(lse)

            return lse

        def objective_function(x, N, w, Q_target, weights, w_j_start):
            y_j_test = x[:N] / Q
            # weight peak frequencies to make them same order of magnitude
            w_j_test = x[N:] * w_j_start
            q_fit = self.q_linear_solid(y_j=y_j_test, w_j=w_j_test, w=w,
                                        exact=exact)
            l2e = l2_error(Q_target=Q_target, Qls=q_fit, weights=weights)
            return l2e

        args = (N, w, Q_target, weights, w_j_test.copy())
        x0 = np.r_[y_j_test, np.ones(N)]
        bounds = [(1e-10, 1e10) for l in range(2 * N)]

        result = minimize(objective_function, x0, args, jac=False,
                          bounds=bounds,
                          options={'maxiter': maxiter,
                                   'maxfun': maxiter * 2 * N, 'disp': False,
                                   'ftol': ftol},
                          method='L-BFGS-B')

        y_j = result.x[:N] / Q
        w_j = result.x[N:] * w_j_start

        return self(y_j, w_j, Q, alpha, pl_f_ref, f_min, f_max)

    def plot(self, ffac=10., nfsamp=1000, errorlim=1.1, show=True, color='r',
             exact=True, **kwargs):

        fig = plt.figure()
        f_min = self.f_min / ffac
        f_max = self.f_max * ffac

        w = np.logspace(np.log10(f_min), np.log10(f_max), nfsamp) * 2 * np.pi

        Q_target = self.power_law_Q(self.Q, self.alpha, w, self.pl_f_ref)
        Qls = self.get_Q(w, exact=exact)

        plt.loglog(w / 2 / np.pi, Q_target, 'k')
        plt.loglog(w / 2 / np.pi, Qls, color)

        plt.xlim(f_min, f_max)

        for _w in self.w_j:
            plt.axvline(_w / 2 / np.pi, color=color, ls='--', zorder=10)

        plt.loglog(w / 2 / np.pi, Q_target * errorlim, color='gray', ls='--')
        plt.loglog(w / 2 / np.pi, Q_target / errorlim, color='gray', ls='--')

        plt.axvline(self.f_min, color='gray', ls='-')
        plt.axvline(self.f_max, color='gray', ls='-')

        plt.xlabel('frequency / Hz')
        plt.ylabel('Q')
        plt.title('Q approximated with %d linear solids' % (self.N,))

        if show:  # pragma: no cover
            plt.show()
        else:
            return fig