from . import settings
from matialvarezs_request_handler import utils as matialvarezs_request_handler_utils
# from . import models
import json


def create_organisation(name):
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
        return json.loads(res.content.decode('utf-8'))
        # organisation_id = res_data['orgId']

    else:
        print("error al guardar organisation")
        return None


def update_organisation(object_project_id, name):
    pass


def change_current_organization(organisation_id):
    # organisation = models.OrganisationGrafana.objects.get(object_project_id=object_project_id)
    url = settings.GRAFANA_API_BASE_URL + 'user/using/' + str(organisation_id)
    res = matialvarezs_request_handler_utils.send_post_and_get_response(url,
                                                                        data={}, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        print("ORGANIZACION GRAFANA ACTUAL CAMBIADA")
    else:
        print("ERROR AL CAMBIAR ORGANIZACION ACTUAL GRAFANA")


def create_datasource():
    data = {
        "name": settings.DATASOURCE_NAME,
        "type": "postgres",
        "access": "proxy",
        # "url": settings.DATABASE_HOST + ":" + settings.DATABASE_PORT,
        "url": settings.DATABASE_HOST,
        # "host":settings.DATABASE_HOST,
        # "port":settings.DATABASE_PORT,
        "secureJsonData": {
            "password": settings.DATABASE_PASSWORD
        },
        "user": settings.DATABASE_USER,
        "database": settings.DATABASE_NAME,
        "jsonData": {
            "host": settings.DATABASE_HOST,
            "port": settings.DATABASE_PORT,
            "sslmode": "disable",
            "default": True
        },

    }
    # organisation = models.OrganisationGrafana.objects.get(object_project_id=1)
    url = settings.GRAFANA_API_BASE_URL + 'datasources'
    res = matialvarezs_request_handler_utils.send_post_and_get_response(url,
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        print("OK crear datasource")
    else:
        print("error al crear datasource")
        print(res.reason)


def create_folder(name):
    data = {
        "uid": None,
        "title": name
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'folders',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        return res.json()
    else:
        return None


def update_folder(name, folder_uid):
    data = {
        "title": name,
    }
    res = matialvarezs_request_handler_utils.send_put(settings.GRAFANA_API_BASE_URL + 'folders/' + folder_uid,
                                                      data=data, headers=settings.GRAFANA_API_HEADERS,
                                                      convert_data_to_json=True)
    return res


def delete_folder(folder_uid):
    res = matialvarezs_request_handler_utils.send_delete(settings.GRAFANA_API_BASE_URL + 'folders/' + folder_uid,
                                                         headers=settings.GRAFANA_API_HEADERS)
    return res


def create_global_user(username, email, name, password):
    data = {
        "role": "Viewer",
        "loginOrEmail": username,
        "password": password,
        "email": email,
        "name": name

    }

    print(settings.GRAFANA_API_BASE_URL + 'admin/users')
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'admin/users',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    print(res)
    if res.status_code == 200:
        print(res.json())
        print("USUARIO GRAFANA GUARDADO")
        return res.json()
    else:
        print("ERROR AL CREAR USUARIO", res.reason)
        return None


def add_global_user_to_organisation(email):
    data = {
        "role": "Viewer",
        "loginOrEmail": email
    }
    res = matialvarezs_request_handler_utils.send_post(settings.GRAFANA_API_BASE_URL + 'org/users',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    print("res al asociar usuario con organisacion actual",res)
    return res
def create_dashboard(dashboard, **options):
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
    folder_id = options.get('folder_id', 0)
    data = {
        "dashboard": dashboard.dashboard_content,
        "folderId": folder_id,
        "overwrite": False
    }

    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'dashboards/db',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        print("***** DATA AL GUARDAR DASHBOARD ", data)
        print("RES AL GUARDAR DASHBOARD", json.loads(res.content.decode('utf-8')))
        res_data = json.loads(res.content.decode('utf-8'))
        return res_data


    else:
        print("ERROR AL GUARDAR DASHBOARD", json.loads(res.content.decode('utf-8')))
        return None


def update_dashboard(json_dashboard, folder_id):
    data = {
        "dashboard": json_dashboard,
        "folderId": folder_id,
        "overwrite": True,
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'dashboards/db',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res.status_code == 200:
        # dashboard_db_storaged.dashboard_content = json_dashboard
        # dashboard_db_storaged.save()
        print("**** DATA AL ACTUALIZAR DASHBOARD ****", data)
        print("RES AL ACTUALIZAR DASHBOARD", json.loads(res.content.decode('utf-8')))
    else:
        print("ERROR AL ACTUALIZAR DASHBOARD", json.loads(res.content.decode('utf-8')))


def delete_dashboard(dashboard_uid):
    res = matialvarezs_request_handler_utils.send_delete(
        settings.GRAFANA_API_BASE_URL + 'dashboards/uid/' + dashboard_uid,
        headers=settings.GRAFANA_API_HEADERS)
    #print(res,res.status_code,res.reason)
    return res
