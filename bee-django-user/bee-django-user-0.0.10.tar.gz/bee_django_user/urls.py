#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

app_name = "bee_django_user"

urlpatterns = [
    # url(r'^', views.home_page, name='homepage'),
    url(r'^test/$', views.test, name='test'),
    url(r'^$', views.UserList.as_view(), name='index'),

    url(r'^login/$', auth_views.LoginView.as_view(template_name='bee_django_user/user/login.html'), name='user_login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/user/login'}, name='user_logout'),
    url(r'^password/change/$', views.UserPasswordChangeView.as_view(),name='user_password_change'),
    url(r'^password/change/done/$', auth_views.PasswordChangeDoneView.as_view(
        template_name='bee_django_user/user/password_change_done.html'
    ), name='user_password_change_done'),

    # 学生
    url(r'^list/$', views.UserList.as_view(), name='user_list'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user_detail'),
    url(r'^create/$', views.UserCreate.as_view(), name='user_create'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.UserUpdate.as_view(), name='user_update'),
    url(r'^group/update/(?P<pk>[0-9]+)/$', views.UserGroupUpdate.as_view(), name='user_group_update'),
    # 组及权限
    url(r'^group/list/$', views.GroupList.as_view(), name='group_list'),

    # 班级
    url(r'^class/list/$', views.ClassList.as_view(), name='class_list'),
    url(r'^class/create/$', views.ClassCreate.as_view(), name='class_create'),
    url(r'^class/detail/(?P<pk>[0-9]+)/$', views.ClassDetail.as_view(), name='class_detail'),
    url(r'^class/update/(?P<pk>[0-9]+)/$', views.ClassUpdate.as_view(), name='class_update'),

]
