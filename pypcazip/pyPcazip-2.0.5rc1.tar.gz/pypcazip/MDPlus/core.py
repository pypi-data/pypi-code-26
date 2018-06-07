from __future__ import absolute_import, print_function, division
from six.moves import range
from six import integer_types

import numpy as np
import mdtraj as mdt
import os
import logging as log
from MDPlus import fastfitting, utils
import warnings

class Cofasu(object):

    """
    Construct a Cofau object from a list of Fasu objects.

    A Cofasu presents the data in one or many trajectory files in the form
    of a numpy array-like object.

    Args:

        fasulist (Fasu or list of Fasus): Define the trajectory data to
            be included.
        check (Optional, str): if check is None, fasus are considered 
            legitimate if they match in their second dimension (i.e., 
            number of atoms) If check is 'names', fasus must also match 
            atom names.  If check is 'masses', fasus must match for atom 
            masses, but not neccessarily names.
        comm (Optional, MPI communicator): If provided, trajectory I/O and
            processing is done in parallel.

    Attributes:

        avg (numpy array): mean coordinates as a [natoms, 3] array

    Other attributes are numpy array-like (see Examples)

    Examples::

        f1 = Fasu('protein.pdb','traj1.dcd', selection='name CA')
        f2 = Fasu('protein.pdb' 'traj2.xtc', selection='name CA')
        trajdata = Cofasu([f1, f2])
        print trajdata[34] # prints the 34th coordinate set
        print trajdata[:].mean(axis=0) # prints the average structure

    """
    def __init__(self, fasulist, check=None, comm=None):

        if comm is not None:
            rank = comm.Get_rank()
            size = comm.Get_size()
        else:
            rank = 0
            size = 1

        if not isinstance(fasulist, list):
            fasulist = [fasulist,]

        nfasus = len(fasulist)
        for ifas in range(nfasus):
            if fasulist[ifas].owner is None:
                fasulist[ifas].owner = size * ifas // nfasus

        for f in fasulist:
            if f.owner == rank:
                f._process()
            else:
                f.names = None
                f.masses = None
                f.shape = None
                f.x = None
                f.topology = None

        for f in fasulist:
            if comm is not None:
                f.masses = comm.bcast(f.masses, root=f.owner)
                f.names = comm.bcast(f.names, root=f.owner)
                f.shape = comm.bcast(f.shape, root=f.owner)
                f.topology = comm.bcast(f.topology, root=f.owner)
                if f.x is None:
                    f.x = np.array((1, f.shape[1], f.shape[2]), dtype='float32')
        
        nats = fasulist[0].shape[1]
        for i in range(1, len(fasulist)):
            if not fasulist[i].shape[1] == nats:
                raise ValueError('Fasus have mismatched number of atoms')

        if check is "names":
            nref = fasulist[0].names
            for i in range(1, len(fasulist)):
                if not (nref[:] == fasulist[i].names[:]).all:
                    raise ValueError('Fasus have mismatched atom names')

        elif check is "masses":
            mref = fasulist[0].masses
            for i in range(1, len(fasulist)):
                if not (mref[:] == fasulist[i].masses[:]).all:
                    raise ValueError('Fasus have mismatched atom masses')

        # Update fasu.frames slice definitions now file sizes are known:
        for i in range(len(fasulist)):
            if isinstance(fasulist[i].frames, slice):
                frames = fasulist[i].frames
                if frames.stop == None:
                    l = fasulist[i].shape[0]
                    start = frames.start
                    step = frames.step
                    stop = l
                    #stop = l + 1
                    if step is not None:
                        stop = stop * step
                    if start is not None:
                        stop += start
                    fasulist[i].frames = slice(start, stop, step) 

        self.masses = fasulist[0].masses # atom masses
        self.topology = fasulist[0].topology
        totframes = 0
        for f in fasulist:
            totframes += f.shape[0]
        # Shape of trajectory array (nframes, natoms, 3)
        self.shape = (totframes, fasulist[0].shape[1], fasulist[0].shape[2])
        self.fasulist = fasulist
        self.comm = comm
        self.avg = self.mean_structure() # mean structure

    def _x(self, key):
        """
        Private method to access coordinate data.
        """

        if isinstance(key, tuple):
            _key1 = key[0]
            if isinstance(_key1, integer_types):
                _key1 = slice(_key1, _key1+1)
            _key2 = key[1]
            if len(key) == 3:
                _key3 = key[2]
            else:
                _key3 = None

        elif isinstance(key, integer_types):
            _key1 = slice(key, key+1)
            _key2 = None
            _key3 = None

        elif isinstance(key, slice):
            _key1 = key
            _key2 = None
            _key3 = None

        totsize = self.shape[0]
        indx = list(range(totsize))[_key1]
        newsize = len(indx)

        reverse = False
        if indx[-1] < indx[0]:
            reverse = True
            indx = indx[::-1]
        maxval = 0
        j = 0
        x = []
        y = []
        sizes = [f.shape[0] for f in self.fasulist]
        for size in sizes:
            ix = []
            iy = []
            minval = maxval
            maxval += size
            while j < len(indx) and indx[j] < maxval:
                ix.append(j)
                iy.append(indx[j] - minval)
                j += 1
            x.append(ix)
            y.append(iy)
        if reverse:
            for ix in x:
                for v in ix:
                    v = len(indx) - v
            for iy in y:
                 iy = iy.reverse()

        xtmp = np.zeros((newsize, self.shape[1], self.shape[2]), dtype='float32')
        for i in range(len(self.fasulist)):
            f = self.fasulist[i]
            if self.comm is not None:
                
                rank = self.comm.Get_rank()
                if rank == f.owner:
                    xtmp[x[i]] = f.x[y[i]]
                xtmp[x[i]] = self.comm.bcast(xtmp[x[i]], root=f.owner)
            else:
                xtmp[x[i]] = f.x[y[i]]
        if _key2 is not None:
            if _key3 is not None:
                xtmp = xtmp[(slice(0,len(xtmp)), _key2, _key3)]
            else:
                xtmp = xtmp[(slice(0,len(xtmp)), _key2)]
        if len(xtmp) == 1:
            xtmp = xtmp[0]
        return xtmp

    def __len__(self):
        return self.shape[0]

    def __getitem__(self, key):
        return self._x(key)

    def mean_structure(self):
        """
        Return the mean structure, without any fitting process.

        Returns:
            crds ([natoms, 3] numpy array): coordinates of mean structure

        """
        if self.comm is None:
            rank = 0
        else:
            rank = self.comm.Get_rank()

        sum = np.zeros((self.shape[1], self.shape[2]), dtype='float32')
        for f in self.fasulist:
            if f.owner == rank:
                sum += f.x.sum(axis=0)
        if self.comm is not None:
            tsum = self.comm.allreduce(sum)
        else:
            tsum = sum

        return  tsum/len(self)

    def align(self, target=None, weighted=False, procrustes=False,
    error=0.0001, maxcyc=10):
        """
        Align the frames in a trajectory to some reference structure.
        
        Least-squares fits each frame to some reference structure, with
        optional mass-weighting.

        Args:
            target (Optional, [N,3] numpy array): A reference structure to fit 
                to; if not provided, the first frame in the first trajectory is
                used.

            weighted (Optional, bool, default=False): If specified, mass-
                weighted fitting is done.

            procrustes (Optional, bool, default=False): If True, procrustes 
                iterative fitting is done to convergence.

            error (Optional, float, default=0.0001): Defines the target error 
                for the procrustes fit.

            maxcyc (Optional, int, default=10): Defines the maximum number of 
                iterations for the procrustes method.

        Examples::

            c = Cofasu([fasu1, fasu2])
            c.align() # align to 1st frame
            c.align(target=c[34], procrustes=True) # iterativly align to 34th frame
            c.align(weighted=True) # Align with mass-weighting

        """

        if target is None:
            targ = self[0]
        else:
            targ = target

        if weighted:
            weights = self.masses
        else:
            weights = np.ones_like(self.masses)
        weights = np.array([weights,] * 3).T

        if self.comm is None:
            rank = 0
        else:
            rank = self.comm.Get_rank()
        for f in self.fasulist:
            if f.owner ==  rank:
                f.x = fastfitting.fitted_traj(f.x, targ, weights)

        self.avg = self.mean_structure()
            
        if not procrustes:
            return

        err = self.avg - targ
        err = (err*err).mean()
        cycle = 1
        while err > error and cycle < maxcyc:
            target = self.avg
            oldavg = self.avg
            for f in self.fasulist:
                if f.owner ==  rank:
                    f.x = fastfitting.fitted_traj(f.x, target, weights)

            self.avg = self.mean_structure()
            
            err = self.avg - oldavg
            err = (err*err).mean()
            cycle += 1
        if self.comm is None or rank == 0:
            log.debug('Procrustes converged in {} cycles'.format(cycle)
                      + ' with error {}'.format(err))

    def write(self, filename, coordinates=None):
        """
        Write selected data to an output trajectory file.

        Args:
            filename (str): Name of the file to be written. All MDTraj-
                supported formats are available, selected by the filename
                extension.

            coordinates (Optional, [nframes, natoms, 3] numpy array):
                The data to be written, else all frames in the Cofasu will be 
                output.

        Examples::

            trajdata.write('output.dcd') # Outputs all frames
            start = trajdata[:20]
            trajdata.write('twentyframes.xtc', start) # Just 20 frames.
        """

        # Note: currently ignores box data.
        ext = os.path.splitext(filename)[1].lower()
        needs_topology = ext in ['.gro', '.pdb']

        if self.comm is not None:
            rank = self.comm.Get_rank()
        else:
            rank = 0


        if coordinates is None:
            coordinates = self[:]

        if ext in ['.xtc', '.trr', '.gro']:
            coordinates = coordinates * 0.1
        if ext in '.gro' and coordinates.ndim == 2:
            coordinates = np.array([coordinates,])
        if rank == 0:
            top = self.topology
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                with mdt.open(filename, 'w') as f:
                    if needs_topology:
                        f.write(coordinates, top)
                    else:
                        f.write(coordinates)

class Fasu(object):
    """
    An object that defines the data to be extracted from trajectory files.

    A Fasu object is a wrapper round a trajectory file that defines which
    frames and atoms are to be extracted for analysis, and if certain
    coordinate transformations are required (centering and/or imaging).

    Args:
        trajectory (str or [str] or Trajectory): Name(s) of trajectory 
            file(s), or an mdtraj.Trajectory.
        topology (Optional, str): Name of a topology file compliant with the 
            trajectory files(s). Will be required if the trajectory file
            does not provide topology information itself.
        frames (Optional, slice object or numpy array): Selection of 
            trajectory frames to include.
        selection (Optional, str): mdtraj-compliant atom selection
            string.
        centre (Optional, str): An mdtraj-compliant atom selection string 
            that defines atoms whose geometric centre will be moved to the 
            centre of the periodic box (if there is one), or to the origin 
            (if there isn't).
        pack_into_box (Optional, bool): if True, all coordinates will be 
            imaged into the primary unit cell, after any centering has been
            done.

    Examples::

        f = Fasu(trajectory.dcd', top='protein.pdb')
        f = Fasu[['traj1.dcd', 'traj2.dcd'], top='protein.pdb')
        f = Fasu('trajectory.xtc', top='protein.pdb', frames=slice(0,50,5))
        f = Fasu('trajectory.nc', top='protein.pdb', selection='name CA')
        f = Fasu('traj.dcd', top='prot.pdb', centre='(resid 20) and (name CA)',
                 pack_into_box=True)

    """

    def __init__(self, trajectory, top=None, frames=None, selection='all', 
    centre=None, pack_into_box=False):

        if top is not None:
            test = open(top, 'r')
            test.close()
        self.topfile = top # name of topology file

        if not isinstance(trajectory, mdt.Trajectory):
            self.trajectory = None
            if not isinstance(trajectory, list):
                self.trajfiles = [trajectory,]
            else:
                self.trajfiles = trajectory

            for t in self.trajfiles:
                test = open(t, 'r')
                test.close()
        else:
            self.trajectory = trajectory
            self.trajfiles = None

        if frames is not None:
            if not (isinstance(frames, slice) or 
                    isinstance(frames, np.ndarray)):
                raise TypeError('frames must be a slice object or numpy array')
        if frames is None:
            frames = slice(0, None, 1)

        self.frames = frames # number of frames
        self.selection = selection # MDTRaj selection string
        self.centre = centre
        self.pack_into_box = pack_into_box
        self.owner = None
        self.processed = False

    def _process(self):
        """
        Private function that processes the Fasu definition

        """
        if self.processed:
            return

        if self.trajectory is None:
            ext = os.path.splitext(self.trajfiles[0])[1].lower()
            if not ext in ['.gro', '.pdb']:
                self.trajectory = mdt.load(self.trajfiles, top=self.topfile)
            else:
                self.trajectory = mdt.load(self.trajfiles)

        self.sel = self.trajectory.top.select(self.selection)
        self.trajectory.top = self.trajectory.top.subset(self.sel)
        self.topology = self.trajectory.top
        self.trajectory.xyz = self.trajectory.xyz[:, self.sel, :]
        if self.trajectory.n_atoms == 0:
            raise ValueError('Atom selection matches no atoms.')

        masses = [atom.element.mass for atom in self.trajectory.top.atoms]
        masses = np.array(masses, dtype='float32')
        names = [self.trajectory.top.atom(i).name for i in
                 range(self.trajectory.n_atoms)]

        if self.frames is not None:
            x = np.array(self.trajectory.xyz[self.frames], dtype='float32', 
                         order='F')
        else:
            x = np.array(self.trajectory.xyz, dtype='float32', order='F')

        if self.centre is not None:
            c = self.trajectory.top.select(self.centre)
            if len(c) == 0:
                raise ValueError('Atom selection for centering matches no atoms.')
            for i in range(len(x)):
                try:
                    cx = x[i][c].mean(axis=0)
                except IndexError:
                    print(c)
                    raise
                if self.trajectory.unitcell_vectors is None:
                    shift = -cx
                else:
                    shift = self.trajectory.unitcell_vectors[i].diagonal()/2 - cx
                x[i] = x[i] + shift

        if self.pack_into_box:
            x = fastfitting.pib(x, self.trajectory.unitcell_vectors)

        self.x = x * 10.0 # convert from nanometres to angstroms.
        self.masses = masses
        self.names = names
        self.trajectory = self.trajectory[0] # truncate to save memory
        self.shape = x.shape
        self.processed = True
