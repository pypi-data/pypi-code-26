from . import settings
from matialvarezs_request_handler import utils as matialvarezs_request_handler_utils
from . import models
import json


def create_organisation(object_project_id, name):
    data = {
        "name": name
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'orgs',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    # res = requests.post(settings.GRAFANA_API_BASE_URL + 'orgs',data=data, headers=settings.GRAFANA_API_HEADERS)
    # res.
    print("res antes de guardar organisation en grafana", res.content)
    if res.status_code == 200:
        print("res al guardar organisation en grafana", res.content)
        res_data = json.loads(res.content.decode('utf-8'))
        organisation_id = res_data['orgId']
        customer_org_grafana = models.OrganisationGrafana(object_project=object_project_id,
                                                          organisation_id=organisation_id)
        customer_org_grafana.save()
    else:
        print("error al guardar organisation")


def update_organisation(object_project_id, name):
    pass


def change_current_organization(object_project_id):
    organisation = models.OrganisationGrafana.objects.get(object_project=object_project_id)
    url = settings.GRAFANA_API_BASE_URL + 'user/using/' + str(organisation.organisation_id)
    res = matialvarezs_request_handler_utils.send_post_and_get_response(url,
                                                                        data={}, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        print("ORGANIZACION GRAFANA ACTUAL CAMBIADA")
    else:
        print("ERROR AL CAMBIAR ORGANIZACION ACTUAL GRAFANA")


def create_datasource():
    data = {
        "id": 1,
        "orgId": 1,
        "name": "backend_siscorvac",
        "type": "postgres",
        "access": "proxy",
        "url": "http://" + settings.DATABASE_HOST + ":" + settings.DATABASE_PORT,
        "password": settings.DATABASE_PASSWORD,
        "user": settings.DATABASE_USER,
        "database": settings.DATABASE_NAME,
        "basicAuth": True,
        "basicAuthUser": "basicuser",
        "basicAuthPassword": "basicuser",
        "isDefault": False,
        "jsonData": None
    }
    # organisation = models.OrganisationGrafana.objects.get(object_project=1)
    url = settings.GRAFANA_API_BASE_URL + 'datasources'
    res = matialvarezs_request_handler_utils.send_post_and_get_response(url,
                                                                        data={}, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        print("OK crear datasource")
    else:
        print("error al crear datasource")
        print(res.reason)


def create_user():
    pass


def create_dashboard(json_dashboard, object_project_id):
    # data = {
    #     "dashboard": {
    #         "id": None,
    #         "uid": None,
    #         "title": "Production Overview",
    #         "tags": [json_dashboard],
    #         "timezone": "browser",
    #         "schemaVersion": 16,
    #         "version": 0
    #     },
    #     "folderId": 0,
    #     "overwrite": False
    # }
    data = {
        "dashboard": json_dashboard,
        "folderId": 0,
        "overwrite": False
    }

    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'dashboards/db',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        res_data = json.loads(res.content.decode('utf-8'))
        dashboard_uid = res_data['uid']
        dashboard_id = res_data['id']
        dashboard_grafana = models.DashboardGrafana(object_project=object_project_id, dashboard_uid=dashboard_uid,
                                                    dashboard_id=dashboard_id, dashboard_content=json_dashboard)
        dashboard_grafana.save()
        print("RES AL GUARDAR DASHBOARD", json.loads(res.content.decode('utf-8')))
    else:
        print("ERROR AL GUARDAR DASHBOARD", json.loads(res.content.decode('utf-8')))


def update_dashboard(json_dashboard, dashboard_db_storaged):
    data = {
        "dashboard": json_dashboard,
        "folderId": 0,
        "overwrite": True,
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'dashboards/db',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        dashboard_db_storaged.dashboard_content = json_dashboard
        dashboard_db_storaged.save()
        print("RES AL ACTUALIZAR DASHBOARD", json.loads(res.content.decode('utf-8')))
    else:
        print("ERROR AL ACTUALIZAR DASHBOARD", json.loads(res.content.decode('utf-8')))
