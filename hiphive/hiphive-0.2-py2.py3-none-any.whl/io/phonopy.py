"""This module provides functions for reading and writing data files
in phonopy and phono3py formats.
"""

import os
import h5py
import numpy as np
from itertools import product

from .. import ForceConstants
from ..io.logging import logger

logger = logger.getChild('io_phonopy')


def _filename_to_format(filename):
    """ Try to guess the format from the filename """
    basename = os.path.basename(filename)

    if basename == 'FORCE_CONSTANTS':
        return 'text'

    if '.' in basename:
        extension = basename.split('.')[-1]
        if extension == 'hdf5':
            return 'hdf5'
    raise TypeError('Could not guess file format')


def read_phonopy_fc2(filename, format=None):
    """Parse a second order force constant file in phonopy format.

    Parameters
    ----------
    filename : str
        input file name
    format : str
       specify the file-format, if None tries to guess the format from filename

    Returns
    -------
    NumPy (N,N,3,3) array
        second order force constant matrix where `N` is the number of atoms
    """
    fc2_readers = {
        'text': _read_phonopy_fc2_text,
        'hdf5': _read_phonopy_fc2_hdf5
    }

    if format is None:
        format = _filename_to_format(filename)
    if format not in fc2_readers.keys():
        raise TypeError('Did not recognize format {}'.format(format))
    return fc2_readers[format](filename)


def write_phonopy_fc2(filename, fc2, format=None):
    """Write second order force constant matrix in phonopy format.

    Parameters
    ----------
    filename : str
        output file name
    fc2 : ForceConstants/dictionary/NumPy array
        second order force constant matrix; dict should contain second order
        force constants (others will be ignored) and be sparse in permutations
    format : str
       specify the file-format, if None tries to guess the format from filename
     """
    fc2_writers = {
        'text': _write_phonopy_fc2_text,
        'hdf5': _write_phonopy_fc2_hdf5
    }

    # get fc2_array
    if isinstance(fc2, ForceConstants):
        fc2_array = fc2.get_fc_array(order=2)
    elif isinstance(fc2, dict):
        fcs = ForceConstants(fc2)
        fc2_array = fcs.get_fc_array(order=2)
    elif isinstance(fc2, np.ndarray):
        fc2_array = fc2
    else:
        raise ValueError('fc2 should be ForceConstants, dict or NumPy array')
    Natoms = fc2_array.shape[0]
    assert fc2_array.shape == (Natoms, Natoms, 3, 3)

    # write
    if format is None:
        format = _filename_to_format(filename)
    if format not in fc2_writers.keys():
        raise TypeError('Did not recognize format {}'.format(format))
    fc2_writers[format](filename, fc2_array)


def read_phonopy_fc3(filename):
    """Parse a third order force constant file in phonopy hdf5 format.

    Parameters
    ----------
    filename : str
        input file name

    Returns
    -------
    NumPy array
        third order force constant matrix
    """
    with h5py.File(filename, 'r') as hf:
        fc3 = hf['fc3'][:]
    return fc3


def write_phonopy_fc3(filename, fc3):
    """Write third order force constant matrix in phonopy hdf5 format.

    Parameters
    ----------
    filename : str
        output file name
    fc3 : dictionary/NumPy array
        third order force constant matrix; if dict it may contain other order
        force constants aswell since these are filterd, however should be
        sparse in permutations
    """

    if isinstance(fc3, ForceConstants):
        fc3_array = fc3.get_fc_array(order=3)
    if isinstance(fc3, dict):
        fcs = ForceConstants(fc3)
        fc3_array = fcs.get_fc_array(order=3)
    elif isinstance(fc3, np.ndarray):
        fc3_array = fc3

    with h5py.File(filename, 'w') as hf:
        hf.create_dataset('fc3', data=fc3_array)
        hf.flush()


def _read_phonopy_fc2_text(filename):
    """ Reads phonopy-fc2 file in text format """
    with open(filename, 'r') as f:
        lines = f.readlines()
        for n, line in enumerate(lines):
            flds = line.split()
            if len(flds) == 1:  # first line in fc2 file
                Natoms = int(flds[0])
                fc2 = np.empty((Natoms, Natoms, 3, 3)) * np.nan
            elif len(flds) == 2:
                i = int(flds[0]) - 1  # phonopy index starts with 1
                j = int(flds[1]) - 1
                for x in range(3):
                    fc_row = lines[n + x + 1].split()
                    for y in range(3):
                        fc2[i][j][x][y] = float(fc_row[y])
    return fc2


def _read_phonopy_fc2_hdf5(filename):
    """Reads phonopy-fc2 file in hdf5 format  """
    with h5py.File(filename, 'r') as hf:
        if 'force_constants' in hf.keys():
            fc2 = hf['force_constants'][:]
        elif 'fc2' in hf.keys():
            fc2 = hf['fc2'][:]
        else:
            logger.warning('Could not find fc2 data in file {}'.format(
                filename))
            return
    return fc2


def _write_phonopy_fc2_text(filename, fc2):
    """ Writes fc2 NumPy array to filename in text format """
    Natoms = fc2.shape[0]
    with open(filename, 'w') as f:
        f.write('{:}\n'.format(Natoms))
        for i, j in product(range(Natoms), range(Natoms)):
            fc2_ij = fc2[(i, j)]
            assert fc2_ij.shape == (3, 3), fc2_ij.shape
            f.write('{:-5d}{:5d}\n'.format(i + 1, j + 1))
            for row in fc2_ij:
                f.write((3*' {:22.15f}'+'\n').format(*tuple(row)))


def _write_phonopy_fc2_hdf5(filename, fc2):
    """ Writes fc2 NumPy array to filename in hdf5 format """
    with h5py.File(filename, 'w') as hf:
        hf.create_dataset('fc2', data=fc2)
        hf.flush()
