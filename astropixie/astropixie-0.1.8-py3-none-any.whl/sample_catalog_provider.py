import os.path

from astropy.coordinates import SkyCoord
from astropy import units as u

import numpy

from astropixie.types import OpenCluster, Star


class SampleCatalogProvider:
    def __init__(self):
        self.clusters = {
            OpenCluster('Berkeley 20',
                        SkyCoord('05 32 37.0 +00 11 18',
                                 unit=(u.hourangle, u.deg), distance=9000 * u.parsec),
                        source=None):
            self.list_berkeley20,
            OpenCluster('NGC2849',
                        SkyCoord('09 19 23.0 -40 31 01',
                                 unit=(u.hourangle, u.deg), distance=6110 * u.parsec),
                        source=None):
            self.list_ngc2849,
            OpenCluster('NGC7790',
                        SkyCoord('23 58 24.0 +61 12 30',
                                 unit=(u.hourangle, u.deg), distance=3230 * u.parsec),
                        source=None):
            self.list_ngc7790,
        }

    def list_open_clusters(self):
        return list(self.clusters.keys())

    def list_stars(self, coord):
        for cluster, f in self.clusters.items():
            if cluster.coord == coord:
                return f()

        return []

    def list_berkeley20(self):
        datafile = self._get_sample_data_path('berkeley20.tsv')
        stars = numpy.genfromtxt(
            datafile, delimiter=';', skip_header=41,
            names=['Seq', 'Xpos', 'Ypos', 'Vmag', 'V_R', 'e_Vmag', 'e_Rmag']
        )

        results = []

        for star in stars:
            v_mag = star['Vmag']
            r_mag = (star['V_R'] * -1.0) + v_mag
            results.append(Star(v_mag, r_mag))

        return results

    def list_ngc2849(self):
        pass


    def list_ngc7790(self):
        pass

    def _get_sample_data_path(self, name):
        modPath = os.path.dirname(__file__)
        return os.path.join(modPath, 'sample_data', name)
