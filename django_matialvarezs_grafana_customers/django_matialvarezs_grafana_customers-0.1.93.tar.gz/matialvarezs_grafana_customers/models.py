from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
# Create your models here.



class OrganisationGrafana(models.Model):
    object_project = models.IntegerField(default=0)
    organisation_id = models.IntegerField(default=0)

class DashboardGrafana(models.Model):
    object_project = models.IntegerField(default=0)
    dashboard_uid = models.CharField(max_length=15,default='')
    dashboard_id = models.IntegerField(default=0)
    dashboard_content = JSONField(default={})

class PanelGrafana(models.Model):
    object_project = models.IntegerField(default=0)
    dashboard = models.ForeignKey(DashboardGrafana,default=None,blank=True,null=True,related_name='panel_dashboard_grafana')
    panel_id = models.IntegerField(default=0)
    panel_content = JSONField(default={})

class DjangoGrafanaUser(models.Model):
    django_user = models.ForeignKey(User,related_name='django_user_grafana')
    grafana_user = models.IntegerField(default=0)