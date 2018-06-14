# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2015-2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################
import logging
import traceback

from django.conf import settings

logger = logging.getLogger("geonode_mapstore_client.settings")

DEFAULT_MS2_BACKGROUNDS = [{
        "type": "osm",
        "title": "Open Street Map",
        "name": "mapnik",
        "source": "osm",
        "group": "background",
        "visibility": True
    },
    {
        "type": "google",
        "title": "Google HYBRID",
        "name": "HYBRID",
        "source": "google",
        "group": "background",
        "visibility": False
    },
    {
        "type": "mapquest",
        "title": "MapQuest OSM",
        "name": "osm",
        "source": "mapquest",
        "group": "background",
        "visibility": False
    },
    {
        "type": "bing",
        "title": "Bing Aerial",
        "apiKey": "AqTGBsziZHIJYYxgivLBf0hVdrAk9mWO5cQcb8Yux8sW5M8c8opEC2lZqKR1ZZXf",
        "name": "Aerial",
        "source": "bing",
        "group": "background",
        "visibility": False
    },
    {
        "type": "tileprovider",
        "title": "NASAGIBS Night 2012",
        "provider": "NASAGIBS.ViirsEarthAtNight2012",
        "name": "Night2012",
        "source": "nasagibs",
        "group": "background",
        "visibility": False
    },
    {
        "type": "wms",
        "url": "http://www.realvista.it/reflector/open/service",
        "visibility": False,
        "title": "e-Geos Ortofoto RealVista 1.0",
        "name": "rv1",
        "group": "background",
        "format": "image/jpeg"
    },
    {
        "type": "wms",
        "url": "https://demo.geo-solutions.it/geoserver/wms",
        "visibility": False,
        "title": "Natural Earth",
        "name": "sde:NE2_HR_LC_SR_W_DR",
        "group": "background",
        "format": "image/png"
    },
    {
        "type": "wms",
        "url": "https://demo.geo-solutions.it/geoserver/wms",
        "visibility": False,
        "title": "Hypsometric",
        "name": "sde:HYP_HR_SR_OB_DR",
        "group": "background",
        "format": "image/png"
    },
    {
        "type": "wms",
        "url": "https://demo.geo-solutions.it/geoserver/wms",
        "visibility": False,
        "title": "Gray Earth",
        "name": "sde:GRAY_HR_SR_OB_DR",
        "group": "background",
        "format": "image/png"
    },
    {
        "type": "tileprovider",
        "title": "OpenTopoMap",
        "provider": "OpenTopoMap",
        "name": "OpenTopoMap",
        "source": "OpenTopoMap",
        "group": "background",
        "visibility": False
    }
]

MAP_BASELAYERS = getattr(settings, "MAPSTORE_BASELAYERS", DEFAULT_MS2_BACKGROUNDS)


def get_geonode_catalogue_service():
    pycsw = getattr(settings, "PYCSW", None)
    if pycsw:
        try:
            pycsw_config = pycsw["CONFIGURATION"]
            if pycsw_config:
                    pycsw_catalogue = {
                        ("%s" % pycsw_config['metadata:main']['identification_title']): {
                            "url": settings.CATALOGUE['default']['URL'],
                            "type": "csw",
                            "title": pycsw_config['metadata:main']['identification_title'],
                            "autoload": True
                         }
                    }

                    return pycsw_catalogue
        except:
            traceback.print_exc()
            tb = traceback.format_exc()
            logger.error(tb)

    return None

GEONODE_CATALOGUE_SERVICE = get_geonode_catalogue_service()

DEFAULT_MS2_CATALOGUE_SERVICES = {
    "Demo WMS Service": {
        "url": "https://demo.geo-solutions.it/geoserver/wms",
        "type": "wms",
        "title": "Demo WMS Service",
        "autoload": False
     },
    "Demo WMTS Service": {
        "url": "https://demo.geo-solutions.it/geoserver/gwc/service/wmts",
        "type": "wmts",
        "title": "Demo WMTS Service",
        "autoload": False
    }
}
DEFAULT_MS2_CATALOGUE_SELECTED_SERVICE = GEONODE_CATALOGUE_SERVICE.keys()[0] if GEONODE_CATALOGUE_SERVICE else "Demo WMS Service"

CATALOGUE_SERVICES = getattr(settings, "MAPSTORE_CATALOGUE_SERVICES", DEFAULT_MS2_CATALOGUE_SERVICES)
CATALOGUE_SELECTED_SERVICE = getattr(settings, "MAPSTORE_CATALOGUE_SELECTED_SERVICE", DEFAULT_MS2_CATALOGUE_SELECTED_SERVICE)
