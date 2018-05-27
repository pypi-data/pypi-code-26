from . import models
from . import utils
from . import manage_dashboard
import json


def create_and_save_panel_database(dashboard_uid, object_project_panel_id, panel_id, panel_content):
    dashboard = models.DashboardGrafana.objects.get(dashboard_uid=dashboard_uid)
    panel = utils.get_or_none_panel_grafana(object_project_id=object_project_panel_id)
    if not panel:
        #print("EN EL IF DE CREAR PANELS")
        panel = models.PanelGrafana(object_project_id=object_project_panel_id, panel_id=panel_id,
                                    panel_content=panel_content)
        panel.save()

        dashboard_panel = models.DashboardPanelsGrafana(dashboard=dashboard, panel=panel)
        dashboard_panel.save()
    else:
        #print("EN EL ELSE DE CREAR PANELS")
        dashboard = models.DashboardGrafana.objects.get(dashboard_uid=dashboard_uid)
        panel = utils.get_or_none_panel_grafana(object_project_id=object_project_panel_id)
        dashboard_panel = utils.get_or_none_dashboard_panel_grafana(dashboard=dashboard, panel=panel)
        print("dashboard_panel EN EL ELSE DE CREAR PANELS",dashboard_panel)
        if not dashboard_panel:
            dashboard_panel = models.DashboardPanelsGrafana(dashboard=dashboard, panel=panel)
            dashboard_panel.save()
            print("dashboard_panel save() en el else")
            # manage_dashboard.update_dashboard(dashboard)
            # manage_dashboard.update_dashboard(dashboard, panel.panel_content)
