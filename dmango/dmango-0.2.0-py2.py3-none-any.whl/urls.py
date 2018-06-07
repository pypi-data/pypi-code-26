# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views


app_name = 'dmango'
urlpatterns = [
    url(
        regex="^test/~create/$",
        view=views.testCreateView.as_view(),
        name='test_create',
    ),
    url(
        regex="^test/(?P<pk>\d+)/~delete/$",
        view=views.testDeleteView.as_view(),
        name='test_delete',
    ),
    url(
        regex="^test/(?P<pk>\d+)/$",
        view=views.testDetailView.as_view(),
        name='test_detail',
    ),
    url(
        regex="^test/(?P<pk>\d+)/~update/$",
        view=views.testUpdateView.as_view(),
        name='test_update',
    ),
    url(
        regex="^test/$",
        view=views.testListView.as_view(),
        name='test_list',
    ),
	]
