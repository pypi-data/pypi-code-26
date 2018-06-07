from __future__ import absolute_import, print_function, division
from six.moves import range

import numpy as np
import pandas as pd
from scipy.linalg import eigh
from scipy.optimize import minimize_scalar
import struct
import logging as log
import sys
from time import time
import warnings
import mdtraj as mdt
from MDPlus.core import Fasu, Cofasu
from MDPlus import fastfitting
import networkx as nx

def load(filename):
    """
    Initialises a new Pcamodel object with the data from the given file.

    Args:
        filename (str): Name of the .pcz format file to be loaded.

    """
    try:
        filehandle = open(filename, 'rb')
    except IOError as e:
        print("Problems while trying to open {}.".format(filename))
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        raise
    data = filehandle.read(104)
    try:
        filetype = data[0:4].decode('utf-8')
    except:
        filetype = None

    if not filetype in ['PCZ1']:
        print("Error: {}: unrecognised pcz file format".format(filename))
        raise IOError("Error: unrecognised pcz file format")

    if filetype == 'PCZ1':
        keydata = struct.unpack('4s80s4if', data)
        version = keydata[0].decode('utf-8')
        title = keydata[1].decode('utf-8')
        n_atoms = keydata[2]
        nbonds = keydata[3]
        n_frames = keydata[4]
        n_vecs = keydata[5]
        totvar = keydata[6]

        atomnames = []
        resnames = []
        chainnames = []
        bonds = []
        elements = []

        data = filehandle.read(4 * n_atoms)
        atomseq = np.array(struct.unpack('{}i'.format(n_atoms),
                           data))
        for i in range(n_atoms):
            data = filehandle.read(4) 
            aname = struct.unpack('4s', data)
            atomnames.append(str(aname[0].decode('utf-8')))
            n = str(aname[0]).strip().upper()
            e = n[0]
            if e.isdigit():
                e = n[1]
            elements.append(e)
        for i in range(n_atoms):
            data = filehandle.read(3) 
            rname = struct.unpack('3s', data)
            resnames.append(rname[0].decode('utf-8'))
        data = filehandle.read( 4 * n_atoms)
        resseq = np.array(struct.unpack('{}i'.format(n_atoms),
                          data))
        for i in range(n_atoms):
            data = filehandle.read(1) 
            cname = struct.unpack('1s', data)
            chainnames.append(cname[0].decode('utf-8'))

        data = filehandle.read( 4 * nbonds)
        bindx = struct.unpack('{}h'.format(2 * nbonds), data)
        bindx = np.array(bindx).reshape((-1, 2))

        data = filehandle.read(12 * n_atoms) 
        acme = struct.unpack('{}f'.format(3 * n_atoms), data)
        acme = np.array(acme).reshape((-1, 3))
        data = filehandle.read(12 * n_atoms) 
        avg = struct.unpack('{}f'.format(3 * n_atoms), data)
        avg = np.array(avg).reshape((-1, 3))
        data = [(atomseq[i], atomnames[i], elements[i], resseq[i], resnames[i], chainnames[i], "") for i in range(n_atoms)]
        atoms = pd.DataFrame(data, columns=["serial", "name", "element", "resSeq", "resName", "chainID", "segmentID"])
        topology = mdt.Topology.from_dataframe(atoms, bindx)

        data = filehandle.read(4 * n_vecs)
        evals = struct.unpack('{}f'.format(n_vecs), data)
        evals = np.array(evals)

        evecs = np.zeros((n_vecs, 3 * n_atoms))
        for i in range(n_vecs):
            data = filehandle.read(12 * n_atoms)
            evecs[i] = struct.unpack('{}f'.format(3 * n_atoms), data)

        data = filehandle.read(4 * n_vecs)
        p0 = struct.unpack('{}f'.format(n_vecs), data)
        p0 = np.array(p0)
            
        data = filehandle.read(4 * n_vecs)
        pinc = struct.unpack('{}f'.format(n_vecs), data)
        pinc = np.array(pinc)

        projs = np.zeros((n_vecs, n_frames))
        prj = np.zeros((n_vecs))
        for i in range(n_frames):
            data = filehandle.read(2 * n_vecs)
            prj[:] = struct.unpack('{}h'.format(n_vecs), data)
            projs[:,i] = (prj * pinc) + p0

        regready = False
    else:
        raise IOError('Error: unrecognised pcz file format')

    return Pcamodel(evecs, evals, projs, avg, acme, topology, totvar,
                    version=version, title=title)

def fromtrajectory(traj, quality=90.0, req_evecs=None, fastmethod=False,
                   weighted=False):
    """
    Initialises a new Pcamodel object with the data from the given
    mdtraj-like object.

    Arguments:
        traj: An mdtraj trajectory, or similar.
        quality (Opt, float): Percentage of variance to be explained.
            Defaults to 90.0 (90%).
        req_evecs (Optional, int): Number of eigenvectors to calculate. If
            set, overrides quality setting.
        fastmethod (optional, bool): If True, an approximate fast matrix
            diagonalizaion method is used.
        weighted (optional, bool): If True, PCA is done on the mass-weighted
            covariance matrix.

    >>> topfile = "../../../test/2ozq.pdb"
    >>> trjfile = "../../../test/2ozq.dcd"
    >>> from MDPlus.core import Fasu, Cofasu
    >>> t = Cofasu(Fasu(trjfile, top=topfile, 
    ...            selection='name CA and resid 1 to 10'))
    >>> p = fromtrajectory(t)

    
    The quality setting defaults to 90%:
    >>> p = fromtrajectory(t, quality=95)
    >>> p = fromtrajectory(t, quality=120)
    Traceback (most recent call last):
    ...
    ValueError: Pcz: quality must lie in the range 0:100.

    If fastmethod=True then a fast approximate diagonalisation
    method is used.

    >>> f = Fasu(trjfile, top=topfile, selection='resid 1 to 30')
    >>> t = Cofasu(f)
    >>> p1 = fromtrajectory(t)
    >>> ev1 = p1.evals
    >>> p2 = fromtrajectory(t, fastmethod=True)
    >>> ev2 = p2.evals
    >>> print(np.allclose(ev1, ev2))
    True

    """
    if isinstance(traj, mdt.Trajectory):
        traj = Cofasu(Fasu(traj))
    n_atoms = traj.shape[1]
    n_frames = traj.shape[0]
    acme = traj[0]
    comm = traj.comm
    if comm is not None:
        rank = comm.Get_rank()
        size = comm.Get_size()
    else:
        rank = 0
        size = 1
        
    if quality < 0 or quality > 100:
        raise ValueError('Pcz: quality must lie in the range 0:100.')

    if rank == 0:
        log.debug('Pcz: {0} atoms and {1} snapshots'.format(n_atoms, 
                 n_frames))
    if rank == 0:
        log.info('Pcz: least-squares fitting snapshots...')
    time_avg_0 = time()
    traj.align(target=acme, procrustes=True, weighted=weighted)
    avg = traj.avg
    time_avg_1 = time()
    if rank == 0:
        log.debug( 'Pcz: Time for trajectory fitting: '
                 + '{0:.2f} s'.format(time_avg_1 - time_avg_0))

    if rank == 0:
         log.info('Pcz: calculating covariance matrix...')
    time_cov_0 = time()
    if n_frames < (3 * n_atoms):
        fastmethod = True
    if fastmethod:
        # adapted from Ian Dryden's R code. If you have
        # n atoms and p snapshots, then the conventional
        # way to do the pca is to calculate the [3n,3n]
        # covariance matrix and then diagonalise that.
        # However if p < 3n, then the last 3n-p eigenvectors
        # and values are meaningless anyway, and instead
        # you can calculate the [p,p] covariance matrix,
        # diagonalise that, and then do some
        # data massaging to recover the full eigenvectors
        # and eigenvalues from that. Here we extend the
        # approach to situations where 3n is just too big
        # for diagonalisation in a reasonable amount of
        # time, by just taking a selection of snapshots
        # from the full set (<< 3n) and applying this
        # approach. Obviously this is an approximate
        # method, but it may be good enough.
        if rank == 0:
            log.info("Using fast approximate diagonalisation method")
        nsamples = min(1000,n_frames)
        stepsize = n_frames//nsamples
        tmptrj = traj[::stepsize]
        nsamples = len(tmptrj)
        tmptrj = tmptrj - avg
        tmptrj = tmptrj.reshape((-1, 3 * n_atoms))

        cv = np.dot(tmptrj, tmptrj.T)/nsamples
    else:
        n3 = n_atoms * 3
        lcv = np.zeros((n3, n3))
        nlocal = 0
        for f in traj.fasulist:
            if f.owner == rank:
                dx = (f.x - avg).reshape((-1, n3))
                lcv += np.dot(dx.T, dx.conj())
                nlocal += 1
        log.debug('Process {} owns {} fasus.'.format(rank, nlocal))
        if comm is None:
            cv = lcv
        else:
            comm.Barrier()
            cv = np.zeros((n3, n3))
            comm.Allreduce(lcv, cv)
        cv = cv / n_frames
        if rank == 0:
            log.debug("Global CM calculated")

    if weighted:
        m = np.sqrt(np.vstack((traj.masses, traj.masses, traj.masses)).T.flatten())
        m2 = np.dot(m.T, m)
        cv = cv * m2
        
    time_cov_1 = time()
    if rank == 0:
        log.debug( 'Pcz: Time for calculating covariance matrix: '
                 + '{0:.2f} s\n'.format(time_cov_1 - time_cov_0))
        log.debug('Total variance = {}'.format(cv.trace()))
    if rank == 0:
        if weighted:
            log.info('Pcz: diagonalizing mass-weighted covariance matrix...')
        else:
            log.info('Pcz: diagonalizing covariance matrix...')
    time_diag_cov_0 = time()

    if fastmethod:
        w, v = eigh(cv)
        vv = np.zeros(nsamples)
        z = np.dot(tmptrj.T,v)
        for i in range(nsamples):
            vv[i] = np.sqrt((z[:,i]*z[:,i]).sum())
            z[:,i] = z[:,i]/vv[i]

            w2 = np.sqrt(abs(w/nsamples))*vv
        w = w2[w2.argsort()]
        v = z[:,w2.argsort()]
        cs = np.cumsum(w[::-1])
        totvar = cs[-1]
        tval = cs[-1] * quality / 100
        i = 0
        while cs[i] < tval:
            i += 1
        n_vecs = i + 1
    else:
        if rank == 0:
            w, v = eigh(cv)
        else:
            w = None
            v = None
        if comm is not None:
            w = comm.bcast(w, root=0)
            v = comm.bcast(v, root=0)
        cs = np.cumsum(w[::-1])
        totvar = cs[-1]
        tval = cs[-1] * quality / 100
        i = 0
        while cs[i] < tval:
            i += 1
        n_vecs = i + 1
        if req_evecs is not None:
            n_vecs = req_evecs
            if req_evecs > len(cv) - 1:
                raise ValueError('Pcz: you asked for {0} eigenvectors but there'
                              + ' are only {1} available.'.format(req_evecs, 
                                                                  len(w)))
    evals = w[-1:-(n_vecs + 1):-1]
    evecs = v[:, -1:-(n_vecs + 1):-1].T

    time_diag_cov_1 = time()
    if rank == 0:
        log.debug( 'Pcz: Time for diagonalizing covariance matrix: '
                 + '{0:.2f} s\n'.format(time_diag_cov_1 - time_diag_cov_0))

    time_proj_calc_0 = time()
    if rank == 0:
        log.info('Pcz: calculating projections...')

    plist = []
    n3 = 3 * n_atoms
    for f in traj.fasulist:
        if f.owner == rank:
            dx = (f.x - avg).reshape((-1, n3))
            plist.append(np.dot(dx, evecs.T).T)

    if len(plist) == 0:
        lproj = np.zeros((0, 0))
    else:
        lproj = np.hstack(plist)
    if comm is not None:
        gproj = comm.allgather(lproj)
        projs = np.hstack([p for p in gproj if p.size > 0])
    else:
        projs = lproj
        
    time_proj_calc_1 = time()
    if rank == 0:
        log.debug('Pcz: Time for calculating projections: '
                 + '{0:.2f} s'.format(time_proj_calc_1 - time_proj_calc_0))
    
    return Pcamodel(evecs, evals, projs, avg, acme, traj.topology, totvar)


class Pcamodel(object):
    """
    PCA analysis of trajectory data.

    Defines the attributes and methods of an object that describes a PCA model
    built from (probably) MD trajectory data.

    Attributes:
        n_atoms (int): number of atoms
        n_frames (int): number of frames
        n_vecs (int): Number of eigenvectors.
        title: (str): Title (usually taken from trajectory file).
        refxyz ([n_atoms, 3] numpy array): Mean structure.
        acme ([n_atoms, 3] numpy array): Coordinates of a structure with 
            "good" geometry - typically the first frame of the original 
            trajectory.
        topology: The MDTraj topology
        totvar (float): The total variance in the original trajectory.
        evals ([n_vecs] numpy array): Eigenvalues, in descending order of size.
        evecs ([n_vecs, 3*n_atoms] numpy array): Eigenvectors, in same order as
            eigenvectors.
        projs ([n_vecs, n_frames] numpy array): Projection data.

    Methods:

    """

    def __init__(self, evecs, evals, projs, refxyz, acme, topology, totvar, 
                 title=None, version='PCZ1'):
        """
        Initialises a new Pcamodel object.

        """
        self.evecs = evecs
        self.evals = evals
        self.projs = projs
        self.refxyz = refxyz
        self.acme = acme
        self.topology = topology
        self.totvar = totvar
        self.rank = 0
        self.n_atoms = self.topology.n_atoms
        self.n_frames = self.projs.shape[1]
        self.n_vecs = len(evals)
        self.title = title
        if self.title is None:
            self.title = 'Created by pyPcazip'
        
        self.version = version
        self._bondinit()


    def scores(self, framenumber):
        """
        Return the scores (projections) corresponding to a chosen snapshot.

        Args:
            framenumber (int): index of trajectory frame

        Returns:
            scores ([n_vecs] numpy array): Scores for each eigenvector.

        Example:

        >>> topfile = "../../../test/2ozq.pdb"
        >>> trjfile = "../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> t = Cofasu(Fasu(trjfile, top=topfile, selection='name CA'))
        >>> p = fromtrajectory(t)
        >>> s = abs(p.scores(12))
        >>> print(np.allclose(s[3], 0.5800652, rtol=0.001, atol=0.001))
        True

        """
        return self.projs.T[framenumber]


    def frame(self,framenumber, regularize=True):
        """
        Method to return the coordinates of the given frame.
        
        Args:
            framenumber (int): index of selected frame
            regularize (bool): if True, the geometry
                (bond lengths and angles are adjusted to match those in the
                "acme" structure as far as possible, without changing the
                PC scores of this frame).

        Retuns:
            crds ([natom, 3] numpy array): coordinates


        Example:

        >>> topfile = "../../../test/2ozq.pdb"
        >>> trjfile = "../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> t = Cofasu(Fasu(trjfile, top=topfile, selection='name CA'))
        >>> t.align(t[0])
        >>> p = fromtrajectory(t, quality=95)
        >>> ref = t[5]
        >>> x = p.frame(5)
        >>> print( (abs(x - ref)).mean() < 0.19)
        True

        """
        if(framenumber >= self.n_frames):
            return None
        else:
            scores = self.scores(framenumber)
            return self.unmap(scores, regularize=regularize)


    def closest(self, scores):
        """
        Returns the index of the frame with scores closest to the target values.

        Args:
            scores (numpy array): target scores. If the scores vector has less
                than nvec elements, the least significant are assumed to be zero.

        Returns:
            indx (int): The index of the snapshot whose scores are closest to
                the input set.
        """
        ns = len(scores)
        temp = self.projs

        best = 0
        err = ((temp[0:ns, 0] - scores) * (temp[0:ns, 0] - scores)).sum()
        for frame in range(self.n_frames):
            newerr = ((temp[0:ns, frame] - scores) 
                      * (temp[0:ns, frame] - scores)).sum()
            if newerr < err:
                err = newerr
                best = frame
        return best

    def _bondinit(self):
        """ Private function to set up bond length and angle data 

        Initialises the bond and angle (1,3 atom pairs) arrays used for
        the regularizaion process.
        """

        bonds = [bond for bond in self.topology.bonds]
        bindx = []
        for bond in bonds:
            bindx.append((bond[0].index, bond[1].index))
        i = 0
        self.nbonds = len(bindx)
        # check for complete connectivity:
        G = nx.Graph()
        G.add_edges_from(bindx)
        cc = list(nx.connected_components(G))
        if len(cc) > 1 or self.nbonds == 0:
            if self.nbonds == 0:
                log.debug('No bonds in molecular topology - trying to fix...')
            else:
                log.debug('Molecule is fragmented - trying to fix...')
            bindx = self._find_bonds(self.acme)
            self.nbonds = len(bindx)
            log.debug('Generated {} bonds'.format(self.nbonds))
            G.clear()
            G.add_edges_from(bindx)
            cc = list(nx.connected_components(G))
            if len(cc) > 1 or self.nbonds == 0:
                log.debug('Still fragmented - no regularization possible')
                self.fragmented = True
            else:
                self.fragmented = False
        else:
            self.fragmented = False
            
        if not self.fragmented:
            b13 = []
            for b0 in bindx[:-1]:
                i += 1
                for b1 in bindx[i:]:
                    if b0[0] == b1[0]:
                        b13.append((b0[1], b1[1]))
                    if b0[1] == b1[0]:
                        b13.append((b0[0], b1[1]))
            self.b13 = bindx + b13
            self.lref = self._bond_lengths(self.acme, self.b13)
        self.bindx = bindx

    def _find_bonds(self, x):
        """
        Find likely bonds, based on stored topology and coordinates in x
        """
        ref = mdt.Trajectory(x * 0.1, self.topology)
        pairs = []
        t = self.topology
        for i in range(ref.n_atoms - 1):
            for j in range(i + 1, ref.n_atoms):
                pairs.append((i, j))
        d = mdt.compute_distances(ref, pairs, periodic=False)[0]
        r = [(t.atom(i).element.radius + t.atom(j).element.radius) for i,j in pairs]
        d = np.array(d)
        r = np.array(r) * 0.53
        bindx = []
        for i in range(len(pairs)):
            if d[i] - r[i] < 0:
                bindx.append(pairs[i])
        return bindx
        

    def _bond_lengths(self, x, bondlist):
        """
        calculate lengths of bonds in x
        """
        llist = []
        for b in bondlist:
            dx = x[b[0]] - x[b[1]]
            llist.append(np.sqrt((dx * dx).sum()))
        return np.array(llist)

    def _lerror(self, x, bondlist, lref):
        """
        bond length error metric
        """
        assert len(bondlist) == len(lref)
        lx = self._bond_lengths(x, bondlist)
        dl = lx - lref
        return (dl * dl).mean()

    def _bond_shake(self, x, bondlist, lref, evecs, tol=0.005):
        """
        SHAKE type process to regularize bond lengths and angles

        Input coordinates x are refined to minimize error
        in the bond and 1-3 atom distances relative to those in the "acme"
        structure. The coordinate shifts are restricted to dimensions not in
        the essential subspace. 
        """
        if len(bondlist) == 0:
            return x
        if self.fragmented:
            return x

        xshift = np.zeros_like(x)
        errinit = self._lerror(x, bondlist, lref)
        errold = errinit + 2.0 * tol
        errnew = errinit
        def fun(sfac, x, xshift, bondlist, lref):
            return self._lerror(x + xshift * sfac, bondlist, lref)
        while errold - errnew > tol:
            xshift[:] = 0.0
            errold = errnew
            for b in range(len(bondlist)):
                i = bondlist[b][0]
                j = bondlist[b][1]
                dx = x[i] - x[j]
                l = np.sqrt((dx * dx).sum())
                dl = lref[b] - l
                dx = 0.5 * (dx * dl / l)
                xshift[i] += dx
                xshift[j] -= dx

            xshift = xshift.flatten()
            for e in evecs:
                xshift -= e * np.dot(e, xshift)
            xshift = xshift.reshape((-1, 3))
            result = minimize_scalar(fun, bounds=(0.0, 1.0), args=(x,
                                 xshift, self.b13, self.lref))
            sfac = result.x
            errnew = result.fun
            x = x + xshift * sfac
        return x

    def unmap(self,scores, regularize=True, tol=0.005):
        """
        Return the coordinates corresponding to a given set of scores. 

        Args:
            scores (numpy array): a list of scores. If scores has less than
                nvec elements, the least significant are assumed to be zero.
            regularize (bool): if True, coordinates are regularised - bond 
                lengths and angles are refined to match as far as possible
                those in self.acme.


        Returns:
            crds ([natom, 3] numpy array): coordinates.

        Example:

        >>> topfile = "../../../test/2ozq.pdb"
        >>> trjfile = "../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> t = Cofasu(Fasu(trjfile, top=topfile, selection='name CA'))
        >>> p = fromtrajectory(t)
        >>> a = p.refxyz
        >>> a2 = p.unmap(np.zeros(p.n_vecs))
        >>> print((abs(a - a2)).mean() < 0.001)
        True

        """
        x = self.refxyz
        for i in range(self.n_vecs):
            x = x + (self.evecs[i]*scores[i]).reshape((self.n_atoms,3))

        if regularize and (self.fragmented == False):
            xreg = self._bond_shake(x, self.b13, self.lref, self.evecs, tol)
            x = xreg
            
        return x

    def map(self,crds):
        """
        Method to map an arbitrary coordinate set onto the PC model. 
        
        The coordinate set should be a (natom,3) array-like object that matches
        (for size) what's in the pczfile. An array of scores will be 
        returned, one value for each eignevector in the pcz file.

        Args:
            crds ([natom, 3] numpy array): coordinates.

        Returns:
            scores ([n_vecs] numpy array): list of scores.

        Example:

        >>> topfile = "../../../test/2ozq.pdb"
        >>> trjfile = "../../../test/2ozq.dcd"
        >>> from MDPlus.core import Fasu, Cofasu
        >>> t = Cofasu(Fasu(trjfile, top=topfile, selection='name CA'))
        >>> p = fromtrajectory(t)
        >>> m = p.scores(10)
        >>> crds = t[10]
        >>> print(np.allclose(abs(p.map(crds)),abs(m), rtol=0.001, atol=0.001))
        True

        """
        c = fastfitting.fitted(crds, self.refxyz)
        c = c - self.refxyz
        prj = np.zeros(self.n_vecs)
        for i in range(self.n_vecs):
             prj[i]=(np.dot(c.flatten(),self.evecs[i]))
        return prj
  

    def write(self, filename,  version='PCZ1', title='Created by pcz.write()'):
        """
        Write out the PCZ file.

        Args:
            filename (str): Name of .pcz file.
            version (str): Pcz version (format) - only 'PCZ1' supported here.
            title (str): Title for .pcz file.

        """

        self.version = version # Pcz file version (format)
        if self.rank != 0:
            return


        if self.version == 'PCZ1':
            log.debug("Using "+self.version+" format")
            f = open(filename, 'wb')
            f.write(struct.pack('4s', self.version.encode('utf-8')))
            f.write(struct.pack('80s', title.encode('utf-8')))
            f.write(struct.pack('4if', 
                                self.n_atoms, self.nbonds, self.n_frames, 
                                self.n_vecs, self.totvar))

            chainnames = [chr(ord('A') + i) for i in range(26)]
            top = self.topology
            atoms = top.atoms
            if top.atom(0).serial == None:
                i = 1
                for a in atoms:
                    f.write(struct.pack('i', int(i)))
                    i += 1
            else:
                for a in atoms:
                    try:
                        f.write(struct.pack('i', a.serial))
                    except:
                        raise TypeError('Error: serial is of type {}'.format(type(a.serial)))
            
            for a in range(self.n_atoms):
                aname = top.atom(a).name
                if len(aname) == 1:
                    aname = ' ' + aname + '  '
                elif len(aname) == 2:
                    aname = ' ' + aname + ' '
                elif len(aname) == 3:
                    aname = ' ' + aname
                f.write(struct.pack('4s', aname.encode('utf-8')))
            for a in range(self.n_atoms):
                rname = top.atom(a).residue.name
                if len(rname) == 1:
                    rname = rname + '  '
                elif len(rname) == 2:
                    rname = rname + ' '
                f.write(struct.pack('3s', rname.encode('utf-8')))
            for a in range(self.n_atoms):
                f.write(struct.pack('i', top.atom(a).residue.resSeq))
            for a in range(self.n_atoms):
                i = top.atom(a).residue.chain.index % 26
                f.write(struct.pack('1s', chainnames[i].encode('utf-8')))
            for bond in self.bindx:
                bond = np.array(bond).astype(np.int16)
                f.write(struct.pack('2h', bond[0], bond[1]))
            for v in self.acme.flatten():
                f.write(struct.pack('f', v))
                

            for v in self.refxyz.flatten():
                f.write(struct.pack('f', v))
            for i in range(self.n_vecs):
                f.write(struct.pack('f', self.evals[i]))
            for i in range(self.n_vecs):
                for v in self.evecs[i]:
                    f.write(struct.pack('f', v))

            p0 = (self.projs.max(axis=1) + self.projs.min(axis=1)) / 2
            for v in p0:
                f.write(struct.pack('f', v))

            pinc = (self.projs.max(axis=1) - self.projs.min(axis=1)) / 65534
            for v in pinc:
                f.write(struct.pack('f', v))

            for i in range(self.n_frames):
                prj = ((self.projs[:, i] - p0) / pinc).astype(np.int16)
                for ipr in prj: 
                    f.write(struct.pack('h', ipr))
            f.close()
            return
          
        else:
            raise TypeError('Only PCZ1 format supported')


    def maha(self, scores):
        """
        Calculate the Mahalanobis from a set of score deltas.

        Args:
            scores (numpy array): list of scores  - typically differences
                between the scores for two configurations. If fewer than n_vecs
                elements, the least sigificant are presumed to be zero.

        Returns:
            mdist (float): the Mahalanobis distance.
        """
        mdist = 0.0
        s = scores[:self.n_vecs]
        for i in range(len(s)):
            mdist += s[i] * s[i] / self.evals[i]

        return np.sqrt(mdist)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
