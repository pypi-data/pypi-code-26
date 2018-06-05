# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from django_signoff import views


app_name = 'django_signoff'
urlpatterns = [
    url(
        r'^$',
        views.legal_index,
        name='legal_index',
    ),
    url(
        r'^view/(?P<id>[\d]+)/?$',
        views.legal_document,
        name='legal_document',
    ),
]
