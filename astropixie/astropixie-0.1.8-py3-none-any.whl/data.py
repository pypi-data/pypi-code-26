import csv
import os
import re
from urllib.request import urlopen
from urllib.parse import urljoin

from astropy import units as u
from astropy.coordinates import SkyCoord

from astroquery.sdss import SDSS

import numpy as np

import pandas as pd


class OpenCluster(object):
    ra = None
    dec = None
    distance = None

    def stars(cls):
        NotImplemented()


class SampleOpenCluster(OpenCluster):
    def _get_data_source(self, name):
        url = urljoin('http://assets.lsst.rocks/data/', name)
        return urlopen(url)


class Berkeley20(SampleOpenCluster):
    """
    paper: ???
    http://simbad.u-strasbg.fr/simbad/sim-id?Ident=Berkeley20&submit=submit+id
    https://www.aanda.org/articles/aa/abs/2002/27/aa2476/aa2476.html
    """
    coord = SkyCoord('05 32 37.0 +00 11 18', unit=(u.hourangle, u.deg),
                     distance=9000 * u.parsec)  # +- 480
    fe_h = -0.3
    tau = 5.5
    eb_v = 0.15
    Z = 0.008  # Z_sun
    d_modulus = 14.7  # (m - M)
    name = 'Berkeley 20'
    image_path = 'http://assets.lsst.rocks/data/berkeley20-square.png'
    _dtype = [('id', 'i'), ('x', 'f'), ('y', 'f'),
              ('u_b', 'f'), ('b_v', 'f'), ('v_r', 'f'),
              ('v_i', 'f'), ('err_u_b', 'f'),
              ('err_b_v', 'f'), ('err_v_r', 'f'),
              ('err_v_i', 'f'), ('lum', 'f'), ('temp', 'f')]

    @property
    def distance(self):
        return self.coord.distance.value

    def cds_stars(cls):
        data_source = cls._get_data_source('berkeley20.tsv')
        with data_source as f:
            
            reader = csv.reader(f, delimiter=';')
            b20p = [row for row in reader]
            b20rawdata = b20p[41:]
            data = []
            for b in b20rawdata:
                data.append(b[3:5])
            x = [float(data[i][1]) for i in range(len(data))]
            y = [float(data[i][0]) for i in range(len(data))]
            return (x, y)

    def stars(cls):
        data_source = cls._get_data_source('berkeley20-durgapal.dat')
        with data_source as f:
            lines = [l.decode('utf-8')[:-1] for l in f.readlines()]
            data = []
            pattern = re.compile('^\s+|\s* \s*|\s+$')
            for l in lines:
                values = [v for v in pattern.split(l) if v]
                V = float(values[3])
                B_V = float(values[5])
                data.append([V, B_V])
            x = [data[i][1] for i in range(len(data))]
            y = [data[i][0] for i in range(len(data))]
            return (x, y)

    def _dtype_row(cls, arr, values):
        i = 0
        v_len = len(values)
        for name in arr.dtype.names:
            if i < v_len:
                values[i] = arr.dtype[name].type(values[i])
            else:
                values.append(0)
            i += 1
        return np.array([tuple(values)], dtype=cls._dtype)

    def to_array(cls):
        data_source = cls._get_data_source('berkeley20-durgapal.dat')
        with data_source as f:
            lines = [l.decode('utf-8')[:-1] for l in f.readlines()]
            data = np.empty((0, 1), dtype=cls._dtype)
            pattern = re.compile('^\s+|\s* \s*|\s+$')
            for l in lines:
                values = [v for v in pattern.split(l) if v]
                newrow = cls._dtype_row(data, values)
                data = np.row_stack((data, newrow))
            return data


class SDSSRegion(Berkeley20):
    """
    An SDSS (ugriz) region of the sky. Expects PSFs and can be used with
    astropixie widgets.
    
    Default to Berkeley 20, but accept astropy tables.
    """

    _dtype = [('id', np.int64), ('u', 'f'), ('g', 'f'), ('r', 'f'), ('i', 'f'),
              ('g_r', 'f'), ('r_i', 'f'),
              ('lum', 'f'), ('temp', 'f')]

    def __init__(self, table=None):
        if not table:
            self.cat = self.get_cat()
        else:
            self.cat = table
        self.raw = self.cat

    def get_cat(self):
        query = """
SELECT TOP 2000
       p.objID,
       p.ra,
       p.dec,
       p.u,
       p.g,
       p.r,
       p.i,
       p.z
FROM PhotoPrimary AS p
JOIN dbo.fGetNearbyObjEq(83.15416667, 0.18833333, 1.32) AS r ON r.objID = p.objID
WHERE p.clean = 1 and p.probPSF = 1
        """
        return SDSS.query_sql(query)

    def stars(self):
        data = []
        for row in self.cat:
            g = row['g']
            r = row['r']
            # Use V and R so the data is similar to the VizieR data.
            V = g - 0.5784*(g - r) - 0.0038  # sigma = 0.0054
            R = r - 0.1837*(g - r) - 0.0971  # sigma = 0.0106
            data.append([V, V - R])
        x = [data[i][1] for i in range(len(data))]
        y = [data[i][0] for i in range(len(data))]
        return (x, y)

    def to_array(self):
        values = ['id', 'u', 'g', 'r', 'i', 'g_r', 'r_i', 'lum', 'temp']
        data = np.empty((0, 1), dtype=self._dtype)
        for r in self.cat:
            v = []
            v.append(r['objID'])
            v.append(r['u'])
            v.append(r['g'])
            v.append(r['r'])
            v.append(r['i'])
            v.append(r['g'] - r['r'])
            v.append(r['r'] - r['i'])
            newrow = self._dtype_row(data, v)
            data = np.row_stack((data, newrow))
        return data

    def ids(self):
        data = []
        for row in self.cat:
            data.append(row['objID'])
        return data


class NGC2849(SampleOpenCluster):
    """
    paper: http://iopscience.iop.org/article/10.1086/424939/pdf
           https://academic.oup.com/mnras/article/430/1/221/984833
    """
    coord = SkyCoord('09 19 23.0 -40 31 01', unit=(u.hourangle, u.deg),
                     distance=6110 * u.parsec)

    def stars(cls):
        data_source = self._get_data_source('ngc2849-kyeong.dat')
        with data_source as f:
            lines = [l.decode('utf-8')[:-1] for l in f.readlines()]
            lines = lines[2:]
            data = []
            pattern = re.compile('^\s+|\s* \s*|\s+$')
            for l in lines:
                values = [v for v in pattern.split(l) if v]
                V = float(values[7])
                B = float(values[5])
                data.append([V, B - V])
                x = [data[i][1] for i in range(len(data) - 1)]
                y = [data[i][0] for i in range(len(data) - 1)]
        return (x, y)


class NGC7790(SampleOpenCluster):
    """
    paper: https://aas.aanda.org/articles/aas/pdf/2000/15/ds6060.pdf
    """
    coord = SkyCoord('23 58 24.0 +61 12 30', unit=(u.hourangle, u.deg),
                     distance=3230 * u.parsec)


# http://adsbit.harvard.edu/cgi-bin/nph-iarticle_query?bibcode=1968ApJ...151..611M&db_key=AST&page_ind=3&data_type=GIF&type=SCREEN_VIEW&classic=YES
# Morgan-Keenan (MK), Effective Surface Temperature, U-V, B-V
temps = [['O5', 37500, -1.47, -0.32],
         ['O6', 36500, -1.46, -0.32],
         ['O7', 35700, -1.45, -0.32],
         ['O8', 35000, -1.44, -0.31],
         ['O9', 34300, -1.43, -0.31],
         ['O9.5', 32100, -1.40, -0.30],
         ['B0', 30900, -1.38, -0.30],
         ['B0.5', 26200, -1.29, -0.28],
         ['B1', 22600, -1.19, -0.26],
         ['B2,', 20500, -1.10, -0.24],
         ['B3', 17900, -0.91, -0.20],
         # B4 is missing?
         ['B5', 15600, -0.72, -0.16],
         ['B6', 14600, -0.63, -0.14],
         ['B7', 13600, -0.54, -0.12],
         ['B8', 12000, -0.39, -0.09],
         ['B9', 10700, -0.25, -0.06],
         ['B9.5', 10000, -0.13, -0.03],
         ['A0', 9600, 0.00, 0.00],
         ['A1', 9320, 0.06, 0.03],
         ['A2', 9070, 0.12, 0.06],
         ['A3', 8840, 0.17, 0.09],
         ['A4', 8630, 0.21, 0.12],
         ['A5', 8500, 0.25, 0.14],
         # A6 is missing?
         ['A7', 8200, 0.30, 0.19],
         ['F0', 7520, 0.37, 0.31],
         # F1 is missing?
         ['F2', 7240, 0.39, 0.36],
         ['F3', 7000, 0.41, 0.40],
         # F4 is missing
         ['F5', 6810, 0.43, 0.43],
         ['F6', 6580, 0.48, 0.47],
         ['F7', 6370, 0.54, 0.51],
         ['F8', 6210, 0.60, 0.54],
         ['G0', 5980, 0.70, 0.59],
         ['G1', 5890, 0.75, 0.61],
         ['G2', 5800, 0.79, 0.63],
         ['G', 5200],
         ['K', 3700],
         ['M', 2400]]


def get_hr_data(name):
    if name.lower() == 'berkeley20':
        data = Berkeley20()
    elif name.lower() == 'berkeley20_cds':
        b20 = Berkeley20()
        b20.stars = b20.cds_stars
        data = b20
    elif name.lower() == 'ngc2849':
        data = NGC2849()
    else:
        raise NotImplemented('Only berkeley20 and ngc2849 are '
                             'implemented right now.')
    if data:
        return data


def pprint(arr, columns=('temp', 'lum'),
           names=('Temperature (Kelvin)', 'Luminosity (solar units)'),
           max_rows=32, precision=2):
    """
    Create a pandas DataFrame from a numpy ndarray.

    By default use temp and lum with max rows of 32 and precision of 2.

    arr - An numpy.ndarray.
    columns - The columns to include in the pandas DataFrame. Defaults to
              temp and lum.
    names - The column names for the pandas DataFrame. Defaults to
            Temperature and Luminosity.
    max_rows - If max_rows is an integer then set the pandas
               display.max_rows option to that value. If max_rows
               is True then set display.max_rows option  to 1000.
    precision - An integer to set the pandas precision option.
    """
    if max_rows is True:
        pd.set_option('display.max_rows', 1000)
    elif type(max_rows) is int:
        pd.set_option('display.max_rows', max_rows)
    pd.set_option('precision', precision)
    df = pd.DataFrame(arr.flatten(), index=arr['id'].flatten(),
                      columns=columns)
    df.columns = names
    return df



L_ZERO_POINT = 3.0128 * pow(10, 28)  # units to add:  * u.watt
