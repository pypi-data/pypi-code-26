from . import api, models,manage_organisations,utils


def create_user(user_project_id,username,email,name,password,object_organisation_project_id):
    res_data = api.create_global_user(username,email,name,password)
    if res_data:
        grafana_user_id = res_data['id']
        django_grafana_user = utils.get_or_none_user_grafana(user_project_id=user_project_id,grafana_user_id=grafana_user_id)
        if not django_grafana_user:
            django_grafana_user = models.DjangoGrafanaUser(user_project_id=user_project_id,grafana_user_id=grafana_user_id)
            django_grafana_user.save()
            manage_organisations.change_current_organization(object_organisation_project_id)
            api.add_global_user_to_organisation(email)
        return True
    else:
        return None
