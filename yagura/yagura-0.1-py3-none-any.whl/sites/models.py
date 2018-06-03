from uuid import uuid4
from django.db import models
from django.conf import settings
from django.urls import reverse_lazy


class Site(models.Model):
    """Monitoring target site model
    """
    id = models.UUIDField(
        'Site ID in project', primary_key=True, default=uuid4)
    url = models.URLField('Site URL')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url

    def get_absolute_url(self):
        return reverse_lazy('sites:detail', args=(self.id, ))
