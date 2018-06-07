#!/usr/bin/python
'''
Module including functionality that allows to elaborate and extract useful 
information from pcz files.						
'''

from __future__ import absolute_import, print_function, division

import sys
import logging as log

import numpy as np
import math

import mdtraj as mdt
from MDPlus.analysis import pca
import tempfile

def pczdump(args):

    listLong = ['--input', '--evec', '--fluc', '--evals', '--avg', '--coll', 
                '--proj', '--info', '--verbosity', '--output', '--rms', 
                '--anim' ]
    listShort = ['-i', '-e', '-f', '-l', '-a', '-c', '-p', '-n', '-v', '-o', 
                 '-r']

    numArgs = 0
    for i in range(1, len(sys.argv)):
        if (sys.argv[i] in listShort and 
            listLong[listShort.index(sys.argv[i])] in sys.argv):
            log.error('Please, use either the long or the short form of '
                      + 'an option but never both! Try again!')
            sys.exit(-1)

    listUniqOpts = ['--evec', '--fluc', '--evals', '--avg', '--coll', 
                    '--proj', '--info', '--rms', '--anim', '-e', '-f',
                    '-l', '-a', '-c', '-p', '-n', '-r', '-m']
    for i in range(1, len(sys.argv)):
        if sys.argv[i] in listUniqOpts:
            numArgs += 1
            if numArgs == 2:
                log.error('Please ask for an option at a time from pyPczdump. '
                          + 'You have currently been asking for more than one '
                          + 'option! Try again!''')
                sys.exit(-1)

    if args.verbosity:
        if args.verbosity > 1:
            log.basicConfig(format="%(levelname)s: %(message)s", 
                            level=log.DEBUG)
        elif args.verbosity == 1:
            log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    if (args.input is None):
        log.error('')
        log.error('All or any of the mandatory command line arguments is '
                  + 'missing. The correct usage of pypczdump should be:')
        log.error('pyPczdump -i|--input <input-file> [optional arguments]')
        log.error('')
        log.error('Type "pyPczdump -h" or "pyPczdump --help" for further '
                  + 'details.')
        log.error('')
        sys.exit(-1)

    try:
        pcz_instance = pca.load(args.input)
    except IOError:
        exit(1)
    if args.evec is not None:
        if int(args.evec) == 0:
            log.error('pyPczdump used 1-based indexing, not zero-based.')
            sys.exit(-1)
        e = pcz_instance.evecs[int(args.evec) - 1]
        if args.output is not None:
            np.savetxt(args.output, np.column_stack((e,)))
        else:
            log.info("Values of eigenvector %d follow:\n" % int(args.evec))
            for i in e:
                print(i)

    elif args.proj is not None:
        if '-' in args.proj:
            p1 = int(args.proj[:args.proj.index('-')])
            p2 = int(args.proj[args.proj.index('-') + 1:]) 
            if p1 == 0:
                log.error('pyPczdump uses 1-based indexing, not zero-based.')
                sys.exit(-1)
            p = pcz_instance.projs[p1 - 1:p2].T
        else:
            if int(args.proj) == 0:
                log.error('pyPczdump uses 1-based indexing, not zero-based.')
                sys.exit(-1)
            p = pcz_instance.projs[int(args.proj) - 1]
        if args.output is not None:
            np.savetxt(args.output, np.column_stack((p,)))
        else:
            log.info('Values of the projections of eigenvector(s)'
                     + ' %s follow:\n' % args.proj)
            for i in p:
                if len(p.shape) > 1:
                    fmt = '%f ' * len(i) + '\n'
                    print(fmt % tuple(i))
                else:
                    print(i)
    elif args.evals is True:
        evs = pcz_instance.evals
        if args.output is not None:
            np.savetxt(args.output, np.column_stack((evs,)))
        else:
            log.info("The list of eigenvalues follows:\n")
            for i in evs:
                print(i)
    elif args.info is True:
        if pcz_instance.title is not None:
            log.info("Basic information on the compressed file:\n")
            print("%s\n" % pcz_instance.title)
        print("The PCZ file format version is %s\n" % pcz_instance.version)
        print("The number of atoms is %d\n" % pcz_instance.n_atoms)
        print("The number of frames is %d.\n" % pcz_instance.n_frames)
        print("The number of eigenvectors is %d.\n" % pcz_instance.n_vecs)
        print("The variance captured inside this file is %.2f%%.\n" % (
              100 * pcz_instance.evals.sum() / pcz_instance.totvar))
    elif args.fluc is not None:
        if int(args.fluc) == 0:
            log.error('pyPczdump uses 1-based indexing, not zero-based.')
            sys.exit(-1)
        evec = pcz_instance.evecs[int(args.fluc) - 1].reshape((-1, 3))
        fluc = np.sqrt((evec * evec).sum(axis=1))

        if args.output is not None:
            np.savetxt(args.output, np.column_stack((fluc,)))
        else:
            log.info('Values of the fluctuations associated with '
                      + 'eigenvector %d follow:\n' % int(args.fluc))
            for i in fluc:
                print(i)
    elif args.avg is True:
        pcz_instance = pca.load(args.input)
        avg = pcz_instance.refxyz

        r = (pcz_instance.evecs.T *
             pcz_instance.evals).reshape(pcz_instance.n_atoms, -1)
        rmsf = np.sqrt((r * r).sum(axis=1))
        if args.output is None:
            out = tempfile.NamedTemporaryFile(suffix='.pdb').name
        else:
            out = args.output
        u = mdt.Trajectory(avg * 0.1, pcz_instance.topology)
        u.save(out, bfactors=rmsf)

        if args.output is None:
            with open(out, 'rb') as f:
                for line in f:
                    print(line[:-1].decode('utf-8'))

    elif args.coll is True:
        col = np.zeros((pcz_instance.n_vecs))
        for i in range(pcz_instance.n_vecs):
            e = pcz_instance.evecs[i]
            for j in range(0, pcz_instance.n_atoms * 3, 3):
                r2 = e[j] * e[j] + e[j + 1] * e[j + 1] + e[j + 2] * e[j + 2]
                col[i] = col[i] - r2 * math.log(r2)
        col = np.exp(col) / pcz_instance.n_atoms
        if args.output is None:
            log.info('Collectivity metric values K for each eigenvector '
                     + 'follow.:\n')
            log.info('Modes producing most of the collective motion in the '
                     + 'system will have high K values.\n')
            for i in col:
                print(i)
        else:
            np.savetxt(args.output, np.column_stack((col,)))

    elif args.rms is not None:
        if ((int(args.rms) > 0) and (int(args.rms) <= pcz_instance.n_frames)):
            s2 = pcz_instance.scores(int(args.rms) - 1)
        rmsd = np.zeros((pcz_instance.n_frames))
        for i in range(pcz_instance.n_frames):
            rmsd[i] = 0.0
            s1 = pcz_instance.scores(i)
            if ((int(args.rms) > 0) and (int(args.rms) <= pcz_instance.n_frames)):
                s1 = s1 - s2
            rmsd[i] = np.sum(s1 * s1) / pcz_instance.n_atoms

        if args.output is not None:
            np.savetxt(args.output, np.column_stack((rmsd,)))
        else:
            for i in rmsd:
                print(np.sqrt(i))

    elif args.anim is not None:
        avg = pcz_instance.refxyz
        if int(args.anim) == 0:
            log.error('pyPczdump uses 1-based indexing, not zero-based.')
            sys.exit(-1)
        evec = pcz_instance.evecs[int(args.anim) - 1]
        proj = pcz_instance.projs[int(args.anim) - 1]

        ev = evec.reshape((-1, 3))
        fluc = np.sqrt((ev * ev).sum(axis=1))

        rmin = np.min(proj)
        rmax = np.max(proj)
        rinc = (rmax - rmin) * 0.1
        proj = np.zeros(20)
        for i in range(1, 6, 1):
            proj[i] = proj[i - 1] + rinc
        for i in range(6, 16, 1):
            proj[i] = proj[i - 1] - rinc
        for i in range(16, 20, 1):
            proj[i] = proj[i - 1] + rinc

        if args.output is None:
            out = tempfile.NamedTemporaryFile(suffix='.pdb').name
        else:
            out = args.output

        trj = []
        for j in range(20):
            trj.append(avg.flatten() + evec * proj[j])

        trj = np.array(trj) * 0.1 # convert to nanometers
        trj = trj.reshape((20, -1, 3))
        u = mdt.Trajectory(trj, pcz_instance.topology)
        u.save(out, bfactors=fluc)

        if args.output is None:
            with open(out, 'rb') as f:
                for line in f:
                    print(line[:-1].decode('utf-8'))

