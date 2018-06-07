"""Function is for collecting data parallelly and more efficiently. """

__all__ = ['collect']

import os
import sys
import glob
import time

from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
import numpy as np

from boutpy.boututils import DataFile
from boutpy.boutdata.field import Field


def check_range(R, low, up, name='range'):
    """Check range R in interval [low , up].

    Parameters
    ----------
    R : int, 1 or 2-element(s) list
        target range to be check
    low, up : int
        low and up limit of the interval, (NOTE: ``up`` <= ``low`` is
        acceptable)
    name : str, optional, default: 'range'
        used in the output message

    Returns
    -------
    R0 : int
        if ``R`` is an int value
    tuple(R0, R1)
    R0, R1 : int
        if ``R`` is an 1 or 2-element(s) list

    """

    nsize = np.abs(up - low) + 1
    bt = np.min([low, up])
    if R is not None:
        try:
            nd = len(R)
            r = R[:]
        except:
            # No len attribute, so probably a single number
            r = [R, R]
            nd = 2
        if nd == 1:
            r = [R[0], R[0]]
            nd = 2
        if nd == 2:
            if r[0] > nsize - 1:
                r[0] = nsize - 1
            elif r[0] < (-1) * nsize:
                r[0] = (-1) * nsize
            if r[1] > nsize - 1:
                r[1] = nsize - 1
            elif r[1] < (-1) * nsize:
                r[1] = (-1) * nsize
            r = list((np.array(r)) % nsize + bt)
        else:
            print "WARNING: {} must be in [{}, {}]".format(
                name, low, up)
            print "         set to [{}, {}]".format(low, up)
            r = [low, up]
    else:
        r = [low, up]
    if r[0] > r[1]:
        r = [r[1], r[0]]
    return r


def collect(varname, xind=None, yind=None, zind=None, tind=None,
            path="data", yguards=False, info=False, prefix="BOUT.dmp",
            nthreads=None, shift=True, checkt=False):
    """Collect a variable from a set of BOUT++ outputs in parallel.

    Parameters
    ----------
    varname : str
        Name of the variable.
    xind, yind, zind, tind: int or list[min, max], optional, default: None
        Range for X/Y/Z/T indices to collect. If it's ``None``, it will
        collect all the data in this dimension.
    path : str, optional, default: "./data"
        Path to data files
    prefix : str, optional, default: "BOUT.dmp"
        File prefix
    nthreads : int, optional, default: None
        Using ``nthreads`` threads to speed up collocting. If
        ``nthreads=None``, it is set to the number of the cpus in current
        node/system.
    yguards : bool, optional, default: False
        Collect Y boundary guard cells if ``yguards=True``
    checkt : bool, optional, default: False
        Check t_array of each dump file and print broken files' name if
        ``True``.
    shift : bool, optional, default: True
        Shift axis if the variables is **time-dependent**
        .. centered:: [t, x, ...] --> [x, ..., t]
    info : bool, optional, defalt: False
        Print information about collect if ``True``

    Returns
    -------
    collect : Field

    Notes
    -----
    the `shift` option is set to True by default, which means it returns the
    data in [x, y, z, t] order which is different from the previous version
    in [t, x, y, z] order.

    """

    # Search for BOUT++ dump files in NetCDF format
    file_list = glob.glob(os.path.join(path, prefix + ".nc"))
    if file_list != []:
        print "Single (parallel) data file"
        f = DataFile(file_list[0])  # Open the file
        data = f.read(varname)
        return data.view(Field)

    file_list = glob.glob(os.path.join(path, prefix + "*.nc"))
    file_list.sort()
    if file_list == []:
        print "ERROR: No data files found"
        return None

    nfiles = len(file_list)
    # print "Number of files: " + str(nfiles)

    # Read data from the first file
    f = DataFile(file_list[0])

    # print "File format    : " + f.file_format
    if not nthreads:
        nthreads = cpu_count()  # get number of cpu
    elif (nthreads < 0) or (nthreads > 2 * cpu_count()):
        raise ValueError("unsuitable 'nthreads' value")

    if info:
        print "nthreads: {}\n".format(nthreads)
    try:
        dimens = f.dimensions(varname)
        ndims = len(dimens)
    except TypeError:
        raise TypeError("ERROR: Variable '" + varname + "' not found")

    if ndims < 2 and varname != "t_array":
        # Just read from file
        # We will handle t_array later
        data = f.read(varname)
        f.close()
        return data.view(Field)

    if ndims > 4:
        raise ValueError("Too many dimensions")

    # These scalars are the *same* between dump files,
    # so just read from one dump file
    mxsub = f.read("MXSUB")
    mysub = f.read("MYSUB")
    mz = f.read("MZ")
    myg = f.read("MYG")

    # t_array is a vector that *may* vary from dump file to file.
    # For example, when a simulation exceeds its wall time and is
    # cutoff before making its final time step, the computer may
    # not have time to make all of the final writes to the dump
    # files, which results in dump files with different final times.
    # This previously led to "broadcast" errors that result from
    # trying to combine arrays of different sizes (corresponding to
    # the different final times).
    #
    # We handle this here by examining t_array in *each* of the
    # dump files in file_list. The t_array with the the *smallest*
    # final time is chosen as the nominal t_array, and any results
    # beyond the final time in the nominal t_array are truncated.
    # This allows us to avoid the aforementioned broadcast errors.
    #
    # NOTE: This will not affect physics analysis because at *most*
    # the final data point in time of some processors will be truncated.

    # load baseline t_array from BOUT.dmp.0.nc
    t_array = f.read("t_array")

    # NOTE: Checking 't_array' is time consuming
    #   o this function will try collecting var without checking t_array,
    #     and it will *automatically* recollect var by truncating the
    #     final time step if there are some broken files
    #   o you can try 'checkt = True, info = True' to get more infomations

    # modify t_array if any other dump files have smaller final times
    if checkt:  # check t_array
        print "Checking t_array ...\n"

        def check_tarray(file):
            f_tmp = DataFile(file)
            len_t_tmp = f_tmp.size("t_array")
            f_tmp.close()
            return len_t_tmp[0]
            # return size of t_array,
            # otherwise the restarted case lossing in the middle time
            # is undetectable.

        pool = Pool(nthreads)
        len_t = pool.map(check_tarray, file_list)
        len_t = np.array(len_t)
        pool.close()
        pool.join()

        f_tmp = DataFile(file_list[len_t.argmin()])
        t_array = f_tmp.read("t_array")
        f_tmp.close()

        # print filename of broken files
        (timesize, counts) = np.unique(len_t, return_counts=True)
        print "t_array size:\t", timesize
        print "      counts:\t", counts
        if counts.size > 1:
            print "Broken dump files: "
            file_list = np.array(file_list)
            print file_list[len_t == timesize[counts.argmin()]]
            print
        else:
            print "No data missing in dump files!\n"
    # ------------ end of checking t_array --------------------

    if varname == "t_array":
        return t_array.view(Field)

    nt = len(t_array)

    if info:
        print 't_array size = %d\n' % nt
        print "mxsub = %d mysub = %d mz = %d\n" % (mxsub, mysub, mz)

    # Get the version of BOUT++ (should be > 0.6 for NetCDF anyway)
    try:
        v = f.read("BOUT_VERSION")

        # 2D decomposition
        nxpe = f.read("NXPE")
        mxg = f.read("MXG")
        nype = f.read("NYPE")
        npe = nxpe * nype

        if info:
            print "BOUT_VERSION: ", v
            print "nxpe = %d, nype = %d, npe = %d\n" % (nxpe, nype, npe)
            if npe < nfiles:
                print "WARNING: More files than expected (" + str(npe) + ")"
            elif npe > nfiles:
                print "WARNING: Some files missing. Expected " + str(npe)

        nx = nxpe * mxsub + 2 * mxg
    except KeyError:
        print "BOUT++ version : Pre-0.2"
        # Assume number of files is correct
        # No decomposition in X
        nx = mxsub
        mxg = 0
        nxpe = 1
        nype = nfiles

    if yguards:
        ny = mysub * nype + 2 * myg
    else:
        ny = mysub * nype

    f.close()

    xind = check_range(xind, 0, nx - 1, "xind")
    yind = check_range(yind, 0, ny - 1, "yind")
    zind = check_range(zind, 0, mz - 2, "zind")
    tind = check_range(tind, 0, nt - 1, "tind")

    xsize = xind[1] - xind[0] + 1
    ysize = yind[1] - yind[0] + 1
    zsize = zind[1] - zind[0] + 1
    tsize = tind[1] - tind[0] + 1

    if info:
        print "xind = {}, yind = {}, zind = {}, tind = {}".format(
              xind, yind, zind, tind)

    # Map between dimension names and output size
    sizes = {'x': xsize, 'y': ysize, 'z': zsize, 't': tsize}

    # Create a list with size of each dimension
    ddims = map(lambda d: sizes[d], dimens)

    # Create the data array
    data = np.zeros(ddims)

    # determine index range of x,y-processor
    r_pe_xind = [int(float(xind[0] - mxg) / mxsub),
                 int(float(xind[1] - mxg) / mxsub)]
    if yguards:
        r_pe_yind = [int(float(yind[0] - myg) / mysub),
                     int(float(yind[1] - myg) / mysub)]
    else:
        r_pe_yind = [int(float(yind[0]) / mysub), int(float(yind[1]) / mysub)]

    # check boundary
    r_pe_xind = np.min([[nxpe - 1, nxpe - 1], r_pe_xind], axis=0)
    r_pe_xind = np.max([[0, 0], r_pe_xind], axis=0)
    r_pe_yind = np.min([[nype - 1, nype - 1], r_pe_yind], axis=0)
    r_pe_yind = np.max([[0, 0], r_pe_yind], axis=0)
    # thread size used in cxx source code
    # x_nthreads_src = r_pe_xind[1] - r_pe_xind[0] + 1
    # y_nthreads_src = r_pe_yind[1] - r_pe_yind[0] + 1

    # index range of dump files in which the target data locate
    r_nfile = np.array([
        [iny * nxpe + inx for inx in xrange(r_pe_xind[0], r_pe_xind[1] + 1)]
        for iny in xrange(r_pe_yind[0], r_pe_yind[1] + 1)])
    ind_nfile = r_nfile.flatten()
    size_nfile = ind_nfile.size

    if info:
        print "Processor range: x = {}, y = {}".format(r_pe_xind, r_pe_yind)
        print "Index array of dump files:"
        print "   shape = {}, size = {}\n".format(r_nfile.shape, size_nfile)
        if info == 2:
            print "Indices of dump files:\n{}\n".format(r_nfile)

    # processing ``index`` file
    def processor(index):
        # Get X and Y processor indices
        pe_yind = int(index / nxpe)
        pe_xind = index % nxpe

        # Get local ranges
        if yguards:
            ymin = yind[0] - pe_yind * mysub
            ymax = yind[1] - pe_yind * mysub
        else:
            ymin = yind[0] - pe_yind * mysub + myg
            ymax = yind[1] - pe_yind * mysub + myg

        xmin = xind[0] - pe_xind * mxsub
        xmax = xind[1] - pe_xind * mxsub

        inrange = True

        if yguards:
            # Check lower y boundary
            if pe_yind == 0:
                # Keeping inner boundary
                if ymax < 0:
                    inrange = False
                if ymin < 0:
                    ymin = 0
            else:
                if ymax < myg:
                    inrange = False
                if ymin < myg:
                    ymin = myg

            # Upper y boundary
            if pe_yind == (nype - 1):
                # Keeping outer boundary
                if ymin >= (mysub + 2 * myg):
                    inrange = False
                if ymax > (mysub + 2 * myg - 1):
                    ymax = (mysub + 2 * myg - 1)
            else:
                if ymin >= (mysub + myg):
                    inrange = False
                if ymax >= (mysub + myg):
                    ymax = (mysub + myg - 1)

        else:
            if (ymin >= (mysub + myg)) or (ymax < myg):
                inrange = False  # Y out of range

            if ymin < myg:
                ymin = myg
            if ymax >= mysub + myg:
                ymax = myg + mysub - 1

        # Check lower x boundary
        if pe_xind == 0:
            # Keeping inner boundary
            if xmax < 0:
                inrange = False
            if xmin < 0:
                xmin = 0
        else:
            if xmax < mxg:
                inrange = False
            if xmin < mxg:
                xmin = mxg

        # Upper x boundary
        if pe_xind == (nxpe - 1):
            # Keeping outer boundary
            if xmin >= (mxsub + 2 * mxg):
                inrange = False
            if xmax > (mxsub + 2 * mxg - 1):
                xmax = (mxsub + 2 * mxg - 1)
        else:
            if xmin >= (mxsub + mxg):
                inrange = False
            if xmax >= (mxsub + mxg):
                xmax = (mxsub + mxg - 1)

        # Number of local values
        nx_loc = xmax - xmin + 1
        ny_loc = ymax - ymin + 1

        # Calculate global indices
        xgmin = xmin + pe_xind * mxsub
        xgmax = xmax + pe_xind * mxsub

        if yguards:
            ygmin = ymin + pe_yind * mysub
            ygmax = ymax + pe_yind * mysub

        else:
            ygmin = ymin + pe_yind * mysub - myg
            ygmax = ymax + pe_yind * mysub - myg

        if not inrange:
            return None     # Don't need this file

        filename = os.path.join(path, prefix + "." + str(index) + ".nc")
        if nthreads == 1 and info:
            # the output is not in threads' order,
            # so the following message may be meaningless
            print " Reading from " + filename + ": [" \
                + str(xmin) + "-" + str(xmax) + "][" \
                + str(ymin) + "-" + str(ymax) + "] -> [" \
                + str(xgmin) + "-" + str(xgmax) + "][" \
                + str(ygmin) + "-" + str(ygmax) + "]",
            sys.stdout.flush()

        f = DataFile(filename)

        if ndims == 4:
            d = f.read(varname, ranges=[tind[0], tind[1] + 1,
                                        xmin, xmax + 1,
                                        ymin, ymax + 1,
                                        zind[0], zind[1] + 1])
            try:
                data[:, (xgmin - xind[0]):(xgmin - xind[0] + nx_loc),
                     (ygmin - yind[0]):(ygmin - yind[0] + ny_loc), :] = d
            except ValueError:
                # Error due to unmatched shapes,
                # i.e. the `index file is broken.
                return index
        elif ndims == 3:
            # Could be xyz or txy
            if dimens[2] == 'z':  # xyz
                d = f.read(varname,
                           ranges=[xmin, xmax + 1,
                                   ymin, ymax + 1,
                                   zind[0], zind[1] + 1])
                data[(xgmin - xind[0]):(xgmin - xind[0] + nx_loc),
                     (ygmin - yind[0]):(ygmin - yind[0] + ny_loc), :] = d
            else:  # txy
                d = f.read(varname,
                           ranges=[tind[0], tind[1] + 1,
                                   xmin, xmax + 1,
                                   ymin, ymax + 1])
                try:
                    data[:, (xgmin - xind[0]):(xgmin - xind[0] + nx_loc),
                         (ygmin - yind[0]):(ygmin - yind[0] + ny_loc)] = d
                except ValueError:
                    # Error due to unmatched shapes.
                    return index
        elif ndims == 2:
            # xy
            d = f.read(varname, ranges=[xmin, xmax + 1,
                                        ymin, ymax + 1])
            data[(xgmin - xind[0]):(xgmin - xind[0] + nx_loc),
                 (ygmin - yind[0]):(ygmin - yind[0] + ny_loc)] = d

        f.close()
        # no Error, normal exit
        return 0

    if nthreads == 1:
        # collect var in current thread
        for i in range(size_nfile):
            processor(ind_nfile[i])
            percent = float(i+1) / size_nfile
            filename = os.path.join(
                path, prefix + "." + str(ind_nfile[i]) + ".nc")
            print "\rProcessing : [{:<20}] {:>6.1%} {}".format(
                ('=' * int(percent * 20) + '>')[0:20], percent, filename),
            sys.stdout.flush()
        print

    else:
        try:
            # collect var in parallel
            pool = Pool(processes=nthreads)
            obj_pool = pool.imap(processor, ind_nfile)
            pool.close()
            # progress info
            while True:
                completed = obj_pool._index
                percent = float(completed) / size_nfile
                print "\rProcessing: [{:<20}] {:>6.1%}".format(
                    ('=' * int(percent * 20) + '>')[0:20], percent),
                sys.stdout.flush()
                if completed == size_nfile:
                    break
                time.sleep(0.05)
            print
            brokenfiles = [i for i in obj_pool if i]
            if brokenfiles:
                raise ValueError('Broken files')

        except ValueError:
            pool.terminate()
            pool.join()
            print "\n" + "#" * 15 + " WARNING " + "#" * 15
            print "Oops! Missing data in dump files: {}.".format(brokenfiles)
            print "      Using 't_array' carefully!"
            print "Checking t_array & Recollecting ...\n"
            data = collect(varname, xind=xind, yind=yind, zind=zind,
                           tind=[tind[0], tind[1] - 1], path=path,
                           yguards=yguards, info=info, prefix=prefix,
                           nthreads=nthreads, shift=False, checkt=True)
        except KeyboardInterrupt:
            print "Keyboard Interrupt, terminating workers ...\n"
            data = None
            pool.terminate()
        finally:
            pool.join()

    # Shift axis if var is time-dependent
    if (dimens[0] == u't') and shift:
        if info:
            print "\nShift axis: [t, x, ...] --> [x, ..., t]\n"
        data = np.rollaxis(data, 0, len(dimens))

    print "data shape: ", data.shape

    return data.view(Field)
