"""This module is for data I/O

- loading data from IDL .sav file
- loading data from NetCDF file
- saving data to NetCDF file

Requirements

- datafile.DataFile
- numpy.swapaxes
- scipy.io.idl or idlsave

"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ['save2nc', 'readsav', 'file_import', 'file_list']

__date__ = '03042018'
__version__ = '0.1.1'
__author__ = 'J.G. Chen'
__email__ = 'cjgls@pku.edu.cn'


import os
import re

import numpy as np

try:
    from scipy.io.idl import readsav as oreadsav
except ImportError:
    try:
        from idlsave import read as oreadsav
    except ImportError:
        print("ImportError: Module for reading IDL .sav file not available")
        raise

from boutpy.boututils.datafile import DataFile


def save2nc(filename, mode, *args, **kwargs):
    """Save variables to NetCDF file.

    **ONLY** for numeric type variables.

    Parameters
    ----------
    filename :  str
    mode : str ['w','a']
        the mode of dealing with the file.
        can be 'write'('w'), 'append'('a'), 'append forcely'('af')

        - 'write'
            if ``filename`` does not exist, create one. if ``filename`` exist,
            erase content!!!!
        - 'append'
            if ``filename`` not exist, create one if ``filename`` exist,
            append contents into the file.

    info : bool
        show extra details
    format : str
        describes the netCDF data model version, one of `NETCDF3_CLASSIC`,
        `NETCDF4`, `NETCDF4_CLASSIC` or `NETCDF3_64BIT`.
    args : arguments, optional
        Arrays to save to the file. Since it is not possible for Python
        to know the names of the arrays outside `save2nc`, the arrays
        will be saved with names "var_0", "var_1", and so on. These
        arguments can be any expression.
    kwargs : keyword arguments, optional
        Arrays to save to the file. Arrays will be saved in the file
        with the keyword names.

    Returns
    -------
    None

    See Also
    --------
    numpy.savez : Save several arrays into an uncompressed `.npz` file format
    numpy.load : Load the files created by savez_compressed.


    Notes
    -----

    - dims option: set name of dimensions
    - format option: set netCDF file model

    - 07/29/2016 created by J.G. Chen
    - 02/21/2017 by J.G.Chen
        initial `fid` to aviod Error when cannot open file.

    Any bug reports and suggestion are gladly welcome.
    Email: cjgls@pku.edu.cn

    """

    if isinstance(filename, basestring):
        if not filename.endswith('.nc'):
            filename += '.nc'

    write = True    # writable
    create = True   # create new file except for 'append' mode
    if 'a' in mode:
        if os.path.isfile(filename):
            create = False

    vardict = {}
    # need to convert ndarray sub-class to ndarray, otherwise may fail.
    for key in kwargs:
        if isinstance(kwargs[key], (int, float)):
            vardict[key] = kwargs[key]
        else:
            vardict[key] = np.asarray(kwargs[key])

    # add `args` to `vardict`
    for i, val in enumerate(args):
        key = 'var_%d' % i
        if key in vardict.keys():
            raise ValueError(
                "keyword `{} already exists, ".format(key)
                + "Can NOT use it to store the un-named variable")
        if isinstance(val, (int, float)):
            vardict[key] = val
        else:
            vardict[key] = np.asarray(val)

    info = vardict.pop('info', False)

    try:
        fid = None
        fid = DataFile(filename, write=write, create=create)
        # , format=format)
        if info:
            print("saving vars: ", vardict.keys())
        for key, val in vardict.items():
            fid.write(key, val, dims='xyzt', info=info)
            # dims='xyzt', guessing the dimension names are
            # 'x', 'y', 'z', 't' for the 1st, 2nd, 3th, 4th
            # dimension respectively.
    finally:
        if fid:
            fid.close()
        else:
            print("ERROR: cannot r/a/w file: {}".format(filename))
        return None


def readsav(filename, idict=None, python_dict=False,
            uncompressed_file_name=None, verbose=False, reverse=True):
    """Read an IDL .sav file.

    NOTE : This function just reverses the axes order of the results
        obtained from module scipy.io.idl.readsav() or idlsave.read().
        reverse axes order: [x1, x2, ..., xn] --> [xn, ..., x2, x1]

    Parameters
    ----------
    file_name : str
        Name of the IDL save file.
    idict : dict, optional
        Dictionary in which to insert .sav file variables
    python_dict : bool, optional
        By default, the object return is not a Python dictionary, but a
        case-insensitive dictionary with item, attribute, and call
        access to variables. To get a standard Python dictionary,
        set this option to True.
    uncompressed_file_name : str, optional
        This option only has an effect for .sav files written with the
        /compress option. If a file name is specified, compressed .sav
        files are uncompressed to this file. Otherwise, readsav will
        use the `tempfile` module to determine a temporary filename
        automatically, and will remove the temporary file upon
        successfully reading it in.
    verbose : bool, optional
        Whether to print out information about the save file, including
        the records read, and available variables.
    reverse : bool, optional
        reverse axes order of data

    Returns
    -------
    data_dict : AttrDict or dict
        If `python_dict` is set to False (default), this function
        returns a case-insensitive dictionary with item, attribute,
        and call access to variables. If `python_dict` is set to True,
        this function returns a Python dictionary with all variable
        names in lowercase. If `idict` was specified, then variables
        are written to the dictionary specified, and the updated
        dictionary is returned.

    """

    # data in .sav file loaded by python with module idlsave.read
    # or scipy.io.idl.readsave are in **reversed** axes order
    # comparing to the data in IDL.

    data_dict = oreadsav(filename, idict=idict, python_dict=python_dict,
                         uncompressed_file_name=uncompressed_file_name,
                         verbose=verbose)

    if not reverse:
        return data_dict

    # reverse axes order [x1, x2, ..., xn] --> [xn, ..., x2, x1]
    for key in data_dict.keys():
        ndims = data_dict[key].ndim
        for i in xrange(np.int(ndims / 2)):
            data_dict[key] = data_dict[key].swapaxes(i, ndims - 1 - i)

    return data_dict


def file_import(filename):
    """Import an NetCDF file.

    Parameters
    ----------
    filename : str
        Name of NetCDF file.

    Returns
    -------
    data : dict
        This function returns a dictionary with variables name as its keys
        and its values are in numpy.ndarray type

    """

    f = DataFile(filename)      # Open NetCDF file
    varlist = f.list()          # Get list of all variables in file
    data = {}                   # Create empty dictionary
    for v in varlist:
        data[v] = f.read(v)
    f.close()
    return data


def file_list(filename, ncol=None, sep=" "):
    """Return a sorted list of names of all variables in NetCDF file.

    Parameters
    ----------
    filename: str | dict
        NetCDF file name or dict
    ncol : int, optional, default: None
        Output to stdout in `ncol` columns format, without return value.
    sep : str, optional, default: " "
        Separator for the stdout.

    Returns
    -------
    ret : list
        return a name list if `ncol` is not specified.

    """

    if isinstance(filename, str):
        f = DataFile(filename)
        varlist = f.list()
        f.close()
    elif isinstance(filename, dict):
        varlist = filename.keys()
    else:
        raise TypeError("Only string or dict type supported!")

    varlist.sort()
    if ncol:
        # TODO: automatically adjust the width of each column
        nsize = len(varlist)
        nrow = int(np.ceil(nsize / np.float(ncol)))
        tmp = np.concatenate([varlist, [''] * (nrow * ncol - nsize)])
        lmax = int(tmp.dtype.str.split(tmp.dtype.char)[-1])
        tmp = np.asarray(map(lambda x: "{{:{}}}".format(lmax).format(x), tmp))
        var_to_print = tmp.reshape(nrow, ncol, order='F')
        print("\n".join([sep.join(var_to_print[i, :]) for i in range(nrow)]))
    else:
        return varlist
