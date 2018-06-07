#!python
"""Calculate growth rate

for more details using command:
    $ growthrate.py -h

OUTPUT:
    - file contains gamma info in config format: `db_path`/gamma_info_fit
    - figure: '`db_path`/`identity`_x{}y{}z{}[_s|_c].png|.eps'

TODO:
    - calculate frequency
    - change to function version

"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__author__ = 'J.G. Chen'
__email__ = 'cjgls@pku.edu.cn'
__version__ = '2.2.0'
__date__ = '10/14/2017'

import argparse
import os
import sys
import re

import numpy as np
import ConfigParser

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import rcParams, ticker

from boutpy.boutdata import collect
from boutpy.boututils import file_import, deriv
from boutpy.boututils.functions import get_nth
from boutpy.boututils.compare_inp import parser_config

plt.ion()   # turn on interactive mode

parser = argparse.ArgumentParser(
    description='Calculate the growth rate.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "dirs", nargs='*', default=['./'],
    help='Path to BOUT++ simulation data')
parser.add_argument(
    '-g', '--grid', nargs='?', help='Grid file name')
parser.add_argument(
    '-G', '--Global', action='store_true',
    help='choose peak position of rms to calculate the growth rate')
parser.add_argument(
    '-x', nargs='?', type=int,
    help='Index in x-axis to calculate the growth rate '
         '(default at peak rms)')
parser.add_argument(
    '-y', nargs='?', type=int,
    help='Index in y-axis to calculate the growth rate '
         '(default at outer mid-plane)')
parser.add_argument(
    '-d', '--data', action='store_true',
    help='Using data directory instead of case directory')
parser.add_argument(
    '-D', '--Database', nargs='?', default="db",
    help='specify directory name to store the figs & data')
parser.add_argument(
    '-t', '--time', nargs='?', default="-200,-1",
    help='Time range to calculate the growth rate')
parser.add_argument(
    '-o', '--output', nargs='?', default="gamma_info",
    help='Filename of output')
parser.add_argument(
    '-v', '--var', nargs='?', default='P',
    help='Variable lists, separate with comma')
parser.add_argument(
    '-c', '--check', nargs='?', default='ZPERIOD',
    help='Variable lists, to be checked in BOUT.inp,'
          'separate with comma, first one is the one scanned')
parser.add_argument(
    '-C', '--Case', action='store_false',
    help='store gamma info with options case sensitive')
parser.add_argument(
    '--savedb', action='store_false',
    help='save figures and gamma info')
parser.add_argument(
    '-i', '--info', action='store_true',
    help='Print more informations')
parser.add_argument(
    '-p', '--percent', nargs='?', type=float, default=0.25,
    help='Ignore percentage of both x-boundary to detect peak of rms')
parser.add_argument(
    '-k', '--kind', choices=['c', 'contourf', 's', 'surface', 'n', 'None'],
    default='s', help='plot type for 2D rms data')

args = parser.parse_args()

_mouse_pointer = None


def onclick(event):
    """Return (x, y) of mouse cursor

    Argument
    --------
    event: matplotlib.backend_bases.Event

    RETURN
    ------
    set value to global variable: _mouse_pointer
    """
    _mouse_pointer = np.array([event.xdata, event.ydata, event.x, event.y])
    print("onclick: ", _mouse_pointer)


if args.info:
    print("Python Version:\n\t{}".format(sys.version.split('\n')[0]))
    print("\t{}\n".format(sys.version.split('\n')[1]))
    print(args)

rcParams.update(
    {'font.size': 20,
     'legend.fontsize': 15,
     'legend.labelspacing': 0.1,
     'legend.frameon': False,
     'lines.linewidth': 2,
     'lines.markersize': 12,
     'savefig.bbox': 'tight'})

no_data = []    # for dirs without data
identity = ''

for idir in args.dirs:
    # check data file or BOUT.inp
    idir = os.path.realpath(idir)
    if not os.path.isdir(idir):
        continue
    if args.data:
        data_path = os.path.realpath(idir)
        idir = os.path.dirname(data_path)
        identity = data_path.split('/')[-1]  # identity of the case
    else:
        data_path = os.path.join(idir, 'data')
        identity = idir.split('/')[-1]       # identity of the case
    print("-" * 50)
    print('identity: ', identity)
    db_path = os.path.join(idir, args.Database)

    dump0 = os.path.join(data_path, 'BOUT.dmp.0.nc')
    BOUTinp = os.path.join(data_path, 'BOUT.inp')
    if not (os.path.exists(dump0) and os.path.exists(BOUTinp)):
        print("WARNING:\n\tNo data files or input file exists")
        if args.data:
            no_data.append(data_path)
        else:
            no_data.append(idir)
        continue

    dict_BOUTinp = parser_config(BOUTinp)
    timestep = float(dict_BOUTinp['TIMESTEP'])
    print("timestep: ", timestep)

    if not os.path.exists(db_path):
        os.makedirs(db_path)

    print('Calculating growth rate of {} ...'.format(identity))

    # check vars in BOUT.inp
    check_vars = (args.check).split(',')
    print("Check variables: \n\t{}".format(check_vars))
    try:
        svar = dict_BOUTinp[check_vars[0]]
        print("{} = {}".format(check_vars[0], svar))
    except:
        print(" please set the scanned var by -v option!")
        break

    for icvars in check_vars[1:]:
        try:
            print("{} = {}".format(icvars, dict_BOUTinp[icvars]))
        except:
            print("No var [{}] exists in BOUT.inp".format(icvars))
            break

    # import grid file
    if not args.grid:
        gridfile = os.path.join(data_path,
                                dict_BOUTinp['grid'].split('/')[-1])
        if not os.path.exists(gridfile):
            print("Failed to dectect the gridfile!!!!")
            break
    else:
        if args.grid.split('/')[-1] == dict_BOUTinp['grid'].split('/')[-1]:
            gridfile = args.grid
        else:
            raise ValueError("The grid is NOT the one used in simulation!!!")
    print("gridfile: {}".format(os.path.basename(gridfile)))
    try:
        g = file_import(gridfile)
    except:
        print("No grid file found!")
        no_data.append(idir)
        continue

    ymid = g['Rxy'][0, :].argmax()
    print("yind for outer mid-plane: ", ymid)
    nx = g['nx']
    if 0.45 > args.percent > 0:
        xstart = int(args.percent * nx)
        xend = nx - xstart
        print("WARNING: detect rms peak in xind = [{}, {}]"
              .format(xstart, xend))
    else:
        xstart = 0
        xend = nx

    # time range for growth rate calculation
    trange = [int(it)
              for it in re.split(';|,', args.time.replace(" ", ""))]
    [tl, tr] = trange
    dmp = file_import(dump0)
    tsize = len(dmp['t_array'])
    Tbar = np.float(dmp['Tbar'])
    print("t_array[-1] ", dmp['t_array'][-1])
    print("Tbar = {:.2e} s ".format(Tbar))

    tsize = tsize - 1   # NOTE: due to some dmp files lose lastest points.
    t_array = dmp['t_array']
    t = t_array[0:tsize]

    print("time range: {}".format(trange))
    tl, tr = get_nth(trange, end=tsize - 1)

    tend = tr
    psi_n = ((g['psixy'][:, ymid] - g['psi_axis'])
             / (g['psi_bndry'] - g['psi_axis']))

    varlist = args.var.split(',')
    if plt.get_fignums():
        plt.clf()
    fig, ax = plt.subplots(2, 2, figsize=[16, 9],
                           facecolor='w', sharex='col', num='growthrate')
    fig.canvas.set_window_title(identity)
    plt.suptitle('{} = {}'.format(check_vars[0], svar))
    ax = ax.flatten()
    plt.subplots_adjust(hspace=0.02, wspace=0.22, right=0.92)
    ax[3].yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1e'))

    for var in varlist:
        if args.Global:
            print('Collecting', var + '[:, :, :, 0:', tsize, '] !!!!')
            p = collect(var, path=data_path,
                        tind=[0, tsize - 1], info=args.info, shift=True)
            rmsp = p.std(axis=-2).squeeze()
            x = rmsp[xstart:xend, :, tr].argmax() % (xend - xstart) + xstart
            y = int(rmsp[xstart:xend, :, tr].argmax() / (xend - xstart))
        else:
            if args.y is None:
                # y position for growth rate, default: outer mid-plane
                y = ymid
            else:
                y = args.y

            print('Collecting', var + '[:, ', y, ', :, 0:', tsize, '] !!!!')
            p = collect(var, path=data_path, yind=[y, y],
                        tind=[0, tsize - 1], info=args.info, shift=True)
            # P[x, y, z, t]
            rmsp = p.std(axis=-2).squeeze()

            if args.x is None:
                x = rmsp[xstart:xend, tr].argmax() + xstart
            else:
                x = args.x

        # print 'save to {}_y{}_{}.npz'.format(var, y, identity)
        # np.savez('{}/{}_y{}_{}.npz'.format(db_path, var, y, identity),
        #      p=p, yind=y)

        # dcp = np.mean(p, axis = 3)
        # rmsp = np.sqrt(np.mean(p ** 2, axis = 3) - dcp ** 2)
        rmsp[..., 0] = rmsp[..., 1] # to avoid warning about log(0)

        mode_plot, = ax[3].plot(psi_n, rmsp[:, tr])
        point_1, = ax[3].plot(psi_n[x], rmsp[x, tr], 'r*')
        ax[3].grid('on')

        print("max rmsp at x = {}, psin = {}".format(x, psi_n[x]))
        print("dimensions of {}: {}".format(var, p.shape))
        # rmspt=mean(rmsp[:,x-10:x+10,0], axis=1)
        rmspt = rmsp[x, :]
        gamma = np.gradient(np.log(rmspt), timestep)
        print("Getting growth rate from x =", x, "and y =", y)
        print("Min growth rate is: {} \n".format(min(gamma)))
        print("\tfitting & plot ...")
        poly = np.polyfit(t[tl:tr + 1],
                          np.log(rmspt[tl:tr + 1]), 1, full=True)
        gamma_mean = np.mean(gamma[tl:tr + 1])
        try:
            print('length of T_array: ', len(t), rmspt.shape)
            line_rmsp, = ax[0].plot(t, np.log(rmspt), 'b-')
            line_fit, = ax[0].plot(t, t * poly[0][0] + poly[0][1], 'r-')
            point, = ax[0].plot([t[tl], t[tr]],
                                np.log([rmspt[tl], rmspt[tr]]), 'r*')
            ax[0].set_ylabel('log(rmsp)')
            ax[0].grid('on')

            line_gamma, = ax[2].plot(t[1:], gamma[1:], 'b-')
            ax[2].set_xlabel('$time/\\tau_A$')
            ax[2].set_ylabel('$\gamma/\omega_A$')
            ax[2].grid('on')

            if args.kind in ['c', 'contourf']:
                args.kind = 'c'
                print("plotting contourf fig of rms ...")
                p_tr = collect(var, path=data_path, shift=True,
                               tind=tr, info=args.info)
                rmsp_tr = p_tr.std(axis=-2).squeeze()
                ax[1].contourf(psi_n, range(g['ny']), rmsp_tr.transpose(), 30)
                ax[1].tick_params(which='both', color='w')
                ax[1].axhline(y, ls='--', color='w')
                # ax[1].set_xlabel('$\psi_n$')
                ax[1].set_ylabel('poloidal')
                ax[1].plot(psi_n[x], y, 'wx', ms=18, lw=2)

            elif args.kind in ['s', 'surface']:
                args.kind = 's'
                # ax[3].set_xticks(ax[1].get_xticks())
                ax[3].set_xlim(psi_n[0], psi_n[-1])
                ax[3].set_xlabel('$\psi_n$')
                ax[1].remove()
                ax[1] = fig.add_subplot(222, projection='3d')
                print("plotting surface fig of rms")
                p_tr = collect(var, path=data_path, shift=True,
                               tind=tr, info=args.info)
                rmsp_tr = p_tr.std(axis=-2).squeeze()
                X, Y = np.meshgrid(np.arange(g['ny']), psi_n)
                ax[1].plot_surface(
                    X, Y, rmsp_tr, cstride=1, rstride=2, lw=0, cmap='jet')
                ax[1].set_xlabel('poloidal', labelpad=20)
                ax[1].set_ylabel('$\psi_n$', labelpad=20)

            else:
                print("fig without plotting 2D rms")
                pass
            ax[1].set_title(r'${}_{{rms}}$, t = {}$\tau_A$'
                            .format(var, t[tr]))
        except:
            raise
            print(sys.exc_info())
            print("Error: No display")

        # test time trange
        while True:
            print("Averaged growth rate from ", tl, "to", tr)
            print("   gamma mean:\t", gamma_mean)
            print("   gamma fit:\t", poly[0][0])
            print("   residual:\t", poly[1][0])
            std_gamma = np.std(gamma[tl:tr + 1])
            print("   STD:\t\t", std_gamma)
            print("   STD/gamma(%):\t", std_gamma / gamma_mean * 100)
            print("   dir:\t", identity)
            print("\nInput trange for averaging growthrate:")

            try:
                trange = raw_input()
                if trange == '':
                    break
                trange = [int(it)
                          for it in re.split(';|,', trange.replace(" ", ""))]
                tl, tr = get_nth(trange, tsize - 1)
                if tr != tend:
                    mode_plot.remove()
                    mode_plot, = ax[3].plot(psi_n, rmsp[:, tr])
                    if args.x is None:
                        x = rmsp[xstart:xend, tr].argmax() + xstart
                    else:
                        x = args.x
                    print("max rmsp at x = {}, psin = {}".format(x, psi_n[x]))
                    # rmspt = mean(rmsp[:,x-10:x+10,0], axis=1)
                    rmspt = rmsp[x, :]
                    gamma = np.gradient(np.log(rmspt), timestep)
                    print("Getting growth rate from x =", x, "and y =", y)
                    print("Min growth rate is: {} \n".format(min(gamma)))

                poly = np.polyfit(t[tl:tr + 1], np.log(rmspt[tl:tr + 1]),
                                  1, full=True)
                gamma_mean = np.mean(gamma[tl:tr + 1])
                line_rmsp.remove()
                line_fit.remove()
                point.remove()
                line_gamma.remove()
                line_rmsp, = ax[0].plot(t, np.log(rmspt), 'b-')
                line_fit, = ax[0].plot(t, t * poly[0][0] + poly[0][1], 'r-')
                point, = ax[0].plot([t[tl], t[tr]],
                                    np.log([rmspt[tl], rmspt[tr]]), 'r*')
                line_gamma, = ax[2].plot(t[1:], gamma[1:], 'b-')

                if tr != tend:
                    tend = tr
                    point_1.remove()
                    point_1, = ax[3].plot(psi_n[x], rmsp[x, tr], 'r*')
                    ax[3].set_ylim(rmsp[:, tr].min() * 1.1,
                                   rmsp[xstart:xend, tr].max() * 1.1)
                    if args.kind in ['c', 'contourf']:
                        ax[1].clear()
                        print("plotting contourf fig of rms ...")
                        p_tr = collect(var, path=data_path, shift=True,
                                       tind=tr, info=args.info)
                        rmsp_tr = p_tr.std(axis=-2).squeeze()
                        ax[1].contourf(
                            psi_n, range(g['ny']), rmsp_tr.transpose(), 30)
                        ax[1].axhline(y, ls='--', color='w')
                        ax[1].set_xticklabels([])
                        ax[1].plot(psi_n[x], y, 'wx', ms=18, lw=2)

                    elif args.kind in ['s', 'surface']:
                        ax[1].clear()
                        print("plotting surface fig of rms")
                        p_tr = collect(var, path=data_path, shift=True,
                                       tind=tr, info=args.info)
                        rmsp_tr = p_tr.std(axis=-2).squeeze()
                        X, Y = np.meshgrid(np.arange(g['ny']), psi_n)
                        ax[1].plot_surface(
                            X, Y, rmsp_tr,
                            cstride=2, rstride=2, lw=0, cmap='jet')
                        ax[1].set_xlabel('poloidal', labelpad=20)
                        ax[1].set_ylabel('$\psi_n$', labelpad=20)

                    else:
                        print("fig without plotting 2D rms")
                        pass
                    ax[1].set_title(r'${}_{{rms}}$, t = {}$\tau_A$'.format(
                        var, t[tr]))

            except:
                raise
                print("INPUT ERROR!")
                break

        # time range set
        # tl, tr = get_nth([tl, tr], end=tsize - 1)

        ax[0].text(0.05, 0.7,
                   '$\gamma_{{fit}}$={:.4f}\nresidual={:.1e}\nTbar={:.2e}s'
                   .format(poly[0][0], poly[1][0], Tbar),
                   transform=ax[0].transAxes)
        ax[3].text(0.05, 0.6,
                   'rmsp, t={} $\\tau_A$\ny={}\nx={}\npsi={}'.format(
                       t[tr], y, x, psi_n[x]),
                   transform=ax[3].transAxes)
        ax[2].text(0.05, 0.8, '$\gamma_{{mean}}$={:.4f}\n$std/\gamma$={:.3f}%'
                   .format(gamma_mean, std_gamma / gamma_mean * 100),
                   transform=ax[2].transAxes)

        # fig: gamma <-- average over time range
        ax[2].plot([t[tl], t[tr]], [gamma[tl], gamma[tr]], 'r*')

        if args.savedb:
            plt.savefig('{}/{}_{}x{}y{}t{}_{}.png'.format(
                db_path, identity, var, x, y, t[tr], args.kind))
            plt.savefig('{}/{}_{}x{}y{}t{}_{}.eps'.format(
                db_path, identity, var, x, y, t[tr], args.kind))
            # store info
            info = ConfigParser.ConfigParser()
            if args.Case:
                # case sensetive, otherwise all in lower case
                info.optionxform = str
            info_file = os.path.join(db_path, args.output)
            info.read(info_file)
            if identity not in info.sections():
                info.add_section(identity)
            # scanned var and its value
            info.set(identity, check_vars[0], svar)
            info.set(identity, 'x', x)
            info.set(identity, 'y', y)
            info.set(identity, 'time', dmp['t_array'][-1])
            info.set(identity, 'Tbar', '{:.3e}'.format(Tbar))
            info.set(identity, 'tl', tl)
            info.set(identity, 'tr', tr)
            info.set(identity, 'gamma', '{:.4f}'.format(poly[0][0]))
            info.set(identity, 'residual', '{:.4f}'.format(poly[1][0]))
            info.set(identity, 'gamma_mean', '{:.4f}'.format(gamma_mean))
            info.set(identity, 'std_gamma', '{:.4f}'.format(std_gamma))
            info.set(identity, 'std_over_gamma', '{:.4f}'.format(
                std_gamma / gamma_mean))
            info.write(open(info_file, 'wb'))

    if 0:  # calculate alpha & q-factor

        Lbar = collect('Lbar', path=data_path)
        print("Lbar = ", Lbar)

        q = -g['ShiftAngle'] / (2 * np.pi)  # q factor
        # index of psi_n = 0.95
        psi95 = np.abs(psi_n[:, ymid] - 0.95).argmin()
        print(" index of psi95 = ", psi95)
        print(" psi95 = ", psi_n[psi95], psi_n[psi95 - 1])
        print(" q95 = ", q[psi95])

        print("collecting P0, B0 at outer mid-plane")
        B0 = collect('B0', path=data_path, yind=ymid)
        p0 = collect('P0', path=data_path, yind=ymid)

        alpha = -g['Rxy'][:, ymid] * \
            deriv(g['Rxy'][:, ymid], p0) * q**2 / B0**2
        max_alpha = alpha.max()
        print("max alpha = ", max_alpha)

plt.close('all')

if len(no_data) > 0:
    print("there are no data in directories of \n\t", sorted(no_data))
