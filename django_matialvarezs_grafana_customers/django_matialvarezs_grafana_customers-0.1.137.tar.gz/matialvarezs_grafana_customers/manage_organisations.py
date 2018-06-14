from . import api,models
def create_organisation(object_project_id, name):
    res_data = api.create_organisation(name)
    if res_data:
        customer_org_grafana = models.OrganisationGrafana(object_project_id=object_project_id,
                                                          organisation_id=res_data['orgId'])
        customer_org_grafana.save()

def change_current_organization(object_project_id):
    organisation = models.OrganisationGrafana.objects.get(object_project_id=object_project_id)
    api.change_current_organization(organisation.organisation_id)


def update_organisation():
    pass