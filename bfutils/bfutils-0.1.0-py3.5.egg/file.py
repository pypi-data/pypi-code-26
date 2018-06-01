"""
Methods for interacting with BF files and filenames, as well as
retrieving metadata.
"""

from bfutils import constants
import os
import re
import json

_orbit_info_dict = None

__all__ = ['orbit_start', 'bf_file_orbit', 'is_bf_file', 
    'get_bf_filename']

def orbit_start( orbit, orbit_info=constants.ORBIT_INFO_JSON ):
    '''
    Find the starting time of orbit according to the orbit info json
    file.
    Returns the starting time in the format of yyyymmddHHMMSS.
    '''

    global _orbit_info_dict

    if _orbit_info_dict is None:
        with open( orbit_info, 'r' ) as f:
            _orbit_info_dict = json.load( f )

    try:
        stime = _orbit_info_dict[str(orbit)]['stime']
    except KeyError: 
        raise ValueError("Argument 'orbit' is outside the supported bounds.")

    return stime

def bf_file_orbit( file ):
    '''
    Returns the orbit number of a basic fusion file as an integer.

    The argument 'file' can be a BF filename (or path to a BF file).
    '''

    bn = os.path.basename( file )
    if not is_bf_file( file ):
        raise ValueError('Argument "file" is not a Basic Fusion file.')

    return int( bn.split('_')[3].replace('O', '') )

def is_bf_file( file ):
    '''
    Returns True if "file" is a proper Basic Fusion filename.
    Else, returns False.
    '''

    bn = os.path.basename(file)
    if re.match( constants.BF_re, bn):
        return True

    return False

def get_bf_filename( orbit ):
    '''
    Retrieve the filename of a Basic Fusion granule from a specific 
    orbit. The filename is primarily constructed from a template 
    (in constants.py) and three pieces of information:

    1. Orbit start time (data/Orbit_Path_Start.json)
    2. BF format number (data/config.yml)
    3. BF version number (data/config.yml)

    It is possible that either the format or the version numbers do 
    not match the BF files you actually have. If so, change the
    values in config.yml to the proper value.
    '''

    o_start = orbit_start( orbit )

    filename = constants.BF_template.format( orbit, o_start, 
        constants.CONFIG['bf_format'],
        constants.CONFIG['bf_version'])

    return filename
