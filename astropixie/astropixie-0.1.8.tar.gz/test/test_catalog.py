from astropy.coordinates import SkyCoord

import astropixie


def test_list_open_cluster_stars():
    for c in astropixie.Catalog.list_open_clusters():
        if c.name == 'Berkeley 20':
            b20Coord = SkyCoord(ra='5h33m0s', dec='0h13m0s')
            assert c.coord.ra == b20Coord.ra
            assert c.coord.dec == b20Coord.dec

            stars = astropixie.Catalog.list_stars(c.coord)
            assert stars
        else:
            assert False
