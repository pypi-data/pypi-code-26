from ohm2_handlers_light import utils as ohm2_handlers_light_utils
from . import models
def get_or_none_panel_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(models.PanelGrafana,**kwargs)