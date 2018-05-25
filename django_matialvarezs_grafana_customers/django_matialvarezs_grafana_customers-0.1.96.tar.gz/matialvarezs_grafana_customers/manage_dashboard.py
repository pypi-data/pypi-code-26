import json
from . import base_dashboard, api,base_row_dashboard
from . import models


def create_dashboard(title_dashboard, panels, object_project_id, **options):
    dashboard = base_dashboard.get_dashboard()
    dashboard['title'] = title_dashboard
    dashboard['panels'] = panels
    # base['panels'] = panels
    # for panel in panels:
    #     dashboard['panels'].append(panel)
    print("DASHBOARD COMPLETO:   ", dashboard)
    api.create_dashboard(dashboard, object_project_id)
    # return base

def create_row_dashboard(title,object_project_id,object_project_panel_id):
    json_row = base_row_dashboard.get_base_row(title)


def update_dashboard(dashboard,panel):
    #dashboard = models.DashboardGrafana.objects.get(object_project=object_project_id)
    json_dashboard = dashboard.dashboard_content
    json_dashboard['uid'] = dashboard.dashboard_uid
    json_dashboard['id'] = dashboard.dashboard_id
    #for panel in panels:
    json_dashboard['panels'].append(panel)
    api.update_dashboard(json_dashboard, dashboard)
