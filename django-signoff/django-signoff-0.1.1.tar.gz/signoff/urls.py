# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from signoff import views


app_name = 'signoff'
urlpatterns = [
    url(
        r'^$',
        views.index,
        name='signoff_index',
    ),
    url(
        r'^view/(?P<id>[\d]+)/?$',
        views.view_document,
        name='signoff_document',
    ),
]
