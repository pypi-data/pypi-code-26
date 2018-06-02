import ipywidgets as widgets
from traitlets import Dict, Unicode, List

default_map_style = {
    'version': 8,
    'sources': {
        'osm': {
            'type': 'raster',
            'tiles': ['http://tile.openstreetmap.org/{z}/{x}/{y}.png']
        }
    },
    'layers': [{
        'id': 'osm',
        'type': 'raster',
        'source': 'osm'
    }]
}


class SimpleMap(widgets.DOMWidget):
    """A widget for creating MapboxGL JS slippy maps based on a style object"""

    _view_name = Unicode('SimpleMapView').tag(sync=True)
    _model_name = Unicode('SimpleMapModel').tag(sync=True)
    _view_module = Unicode('jupyter_voter').tag(sync=True)
    _model_module = Unicode('jupyter_voter').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    map_style = Dict(default_value=default_map_style).tag(sync=True)


class VectorMap(widgets.DOMWidget):
    """A widget for mapping GeoJSON vector features on a MapboxGL JS slippy map"""

    _view_name = Unicode('VectorMapView').tag(sync=True)
    _model_name = Unicode('VectorMapModel').tag(sync=True)
    _view_module = Unicode('jupyter_voter').tag(sync=True)
    _model_module = Unicode('jupyter_voter').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    map_style = Dict(default_value=default_map_style).tag(sync=True)
    vector = Dict(default_value={}).tag(sync=True)


class CompareMap(widgets.DOMWidget):
    """A widget for mapping GeoJSON vector features on a MapboxGL JS slippy map"""

    _view_name = Unicode('CompareMapView').tag(sync=True)
    _model_name = Unicode('CompareMapModel').tag(sync=True)
    _view_module = Unicode('jupyter_voter').tag(sync=True)
    _model_module = Unicode('jupyter_voter').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    vector = Dict(default_value={}).tag(sync=True)
    before = List(default_value=[]).tag(sync=True)
    after = List(default_value=['http://tile.openstreetmap.org/{z}/{x}/{y}.png']).tag(sync=True)
