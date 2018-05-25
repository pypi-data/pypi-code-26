from . import base_row_dashboard
from . import models
import json


def create_row_dashboard(title, object_project_id, object_project_panel_ids):
    json_row = base_row_dashboard.get_base_row(title)

    panles_row = list()
    for id in object_project_panel_ids:
        json_panel = models.PanelGrafana.objects.get(object_project_id=id).panel_content
        panles_row.append(json_panel)
    row = models.PanelsByRowDashboardGrafana(object_project_id=object_project_id, title=title,
                                             panels=object_project_panel_ids, row_content=json.dumps(json_row))
    row.save()
