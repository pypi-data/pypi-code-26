"""File readers for commercial instrumentation."""
import datetime
import calendar

import numpy as np


def read_file_stream_or_path(path_or_file):
    try:
        with open(path_or_file, mode='r') as fid:
            data = fid.read()
    except FileNotFoundError:
        path_or_file.seek(0)
        data = path_or_file.read()
    except AttributeError:
        data = path_or_file

    return data


def read_oceanoptics(file, metadata=False):
    """Read spectral transmission data from an ocean optics spectrometer.

    Parameters
    ----------
    file : `str` or path_like or file_like
        contents of a file, path_like to the file, or file object
    metadata : `bool`
        whether to also gather metadata

    Returns
    -------
    `dict`
        a dictionary with keys of wvl and values

    Raises
    ------
    `IOError`
        if the file is malformed.

    """
    txtlines = read_file_stream_or_path(file).splitlines()

    idx, ready_length, ready_spectral = None, False, False
    for i, line in enumerate(txtlines):
        if 'Number of Pixels in Spectrum' in line:
            length, ready_length = int(line.split()[-1]), True
        elif '>>>>>Begin Spectral Data<<<<<' in line:
            idx, ready_spectral = i, True

    if not ready_length or not ready_spectral:
        raise IOError('''File lacks line stating "Number of Pixels in Spectrum" or
                         ">>>>>Begin Spectral Data<<<<<" and appears to be corrupt.''')
    data_lines = txtlines[idx + 1:]
    wavelengths = np.empty(length)
    values = np.empty(length)
    for idx, line in enumerate(data_lines):
        wvl, val = line.split()
        wavelengths[idx] = wvl
        values[idx] = val

    basics = {
        'wvl': wavelengths,
        'values': values,
    }

    if metadata:
        # date
        date_raw = data_lines[2].split()[1:]
        (month, day, time), year = date_raw[1:4], date_raw[-1]
        month_no = list(calendar.month_name).index(month)
        h, m, s = time.split(':')
        timestamp = datetime.datetime(year=year, month=month_no, day=day, hour=h, minute=m, second=s)

        user = ' '.join(data_lines[3].split()[1:])
        spec = data_lines[4].split()[-1]
        integration = float(data_lines[6].split()[-1]) * 1e3
        averages = int(data_lines[7].split()[-1])
        dark_corrected = data_lines[8].split()[-1] == 'true'
        nonlinear_corrected = data_lines[9].split()[-1] == 'true'

        return {
            **basics,
            'timestamp': timestamp,
            'user': user,
            'instrument': spec,
            'integration_time': integration,
            'averages': averages,
            'dark_corrected': dark_corrected,
            'nonlinear_corrected': nonlinear_corrected
        }
    else:
        return basics
