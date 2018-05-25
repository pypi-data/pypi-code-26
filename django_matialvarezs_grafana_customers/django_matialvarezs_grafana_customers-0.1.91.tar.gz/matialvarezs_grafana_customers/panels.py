from . import models
from . import utils
from . import manage_dashboard
import json


def create_and_save_panel_database(object_project_dashboard_id, object_project_panel_id, panel_id, panel_content):
    dashboard = models.DashboardGrafana.objects.get(object_project=object_project_dashboard_id)
    panel = utils.get_or_none_panel_grafana(object_project=object_project_panel_id)
    if not panel:
        panel = models.PanelGrafana(object_project=object_project_panel_id, dashboard=dashboard, panel_id=panel_id,
                                    panel_content=panel_content)
        panel.save()
        manage_dashboard.update_dashboard(dashboard, panel.panel_content)
