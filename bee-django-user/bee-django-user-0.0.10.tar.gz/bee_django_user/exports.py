#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from .models import User


# 获取一个助教，所教的所有学生
def get_teach_users(assistant):
    users = User.objects.filter(userprofile__user_class__assistant=assistant)
    return users
