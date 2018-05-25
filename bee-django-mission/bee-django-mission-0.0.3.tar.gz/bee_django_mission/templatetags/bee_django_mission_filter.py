#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from datetime import datetime
from django import template
# from bee_django_exam.utils import get_user_model, get_user_name
# from bee_django_exam.exports import filter_local_datetime, get_user_icon

register = template.Library()


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)

#
# # 本地化时间
# @register.filter
# def local_datetime(_datetime):
#     return filter_local_datetime(_datetime)
