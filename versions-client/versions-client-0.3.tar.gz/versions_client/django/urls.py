from __future__ import unicode_literals

from django.conf.urls import url

from .views import versions_view


app_name = 'versions_client'

urlpatterns = [
    url(r'^versionz$', versions_view, name='prometheus'),
]
