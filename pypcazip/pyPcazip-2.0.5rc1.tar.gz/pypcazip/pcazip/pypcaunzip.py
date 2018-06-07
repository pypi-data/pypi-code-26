#!/usr/bin/python

from __future__ import absolute_import, print_function, division
from six.moves import range

import sys
import os.path as op
import logging as log

import numpy as np

import mdtraj as mdt
from MDPlus.analysis import pca
import warnings
#warnings.simplefilter('ignore')

#######################################################
# MAIN FUNCTION
#######################################################

def pcaunzip(args):

    if args.verbosity:
        if args.verbosity > 1:
            log.basicConfig(format="%(levelname)s: %(message)s", 
                            level=log.DEBUG)
        elif args.verbosity == 1:
            log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    if (args.compressed is None ):
        log.error('')
        log.error(
            'All or any of the mandatory command line arguments is missing. '
             + 'The correct usage of pyPcaunzip should be:')
        log.error(
            'pyPcaunzip -c|--compressed <compressed-file>,  [optional arguments]')
        log.error('')
        log.error('Type "pyPcaunzip -h" or "pyPcaunzip --help" '
                  + 'for further details.')
        log.error('')
        sys.exit(-1)

    # If no name is provided for the output file, the extension of the pcz file is just changed into .dcd.
    if not args.output:
        dir = op.dirname(args.compressed)
        base = op.basename(args.compressed)
        name = op.splitext(base)[0]
        args.output = op.join(dir, name + ".dcd")
        if op.isfile(args.output):
            log.error('Output file {} already exists - will not be'
                      + ' overwritten'.format(arg.output))
            exit(1)

    try:
        import netCDF4
        nonetCDF4 = False
    except ImportError:
        nonetCDF4 = True

    ext = op.splitext(args.output)[1].lower()
    if ext == '.ncdf' and nonetCDF4:
        log.error('netcdf4-python with the netCDF4 and HDF5 libraries must '
                  + 'be installed to write AMBER .ncdf files.\nSee '
                  + 'https://code.google.com/p/mdanalysis/wiki/netcdf')
        exit(1)

    log.info("PCAunzipping")
    pfile = pca.load(args.compressed)
    if ext == '.xtc':
        scalefac = 0.1 # Gromacs works in nanometers.
    else:
        scalefac = 1.0
    regularize=False
    if args.regularize:
        regularize=True
    with mdt.open(args.output, 'w') as f:
        for ts_index in range(pfile.n_frames):
            f.write(pfile.frame(ts_index, regularize=regularize) * scalefac)

