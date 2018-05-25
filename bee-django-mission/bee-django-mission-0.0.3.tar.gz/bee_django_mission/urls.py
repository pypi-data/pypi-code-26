#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views

app_name = 'bee_django_mission'
urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^comming_soon', views.CommingSoon.as_view(), name='comming_soon'),
    # 获取学生的周任务
    url(r'^user/mission/list/week/(?P<user_id>[0-9]+)/$',views.UserMissionListWeek.as_view(), name='user_line_week'),
    # 获取学生的长线任务
    url(r'^user/mission/list/unlimited/(?P<user_id>[0-9]+)/$',views.UserMissionListUnlimited.as_view(), name='user_line_unlimited'),
    url(r'^user/stage/detail/(?P<pk>[0-9]+)/$', views.UserStageDetail.as_view(), name='user_stage_detail'),
]
