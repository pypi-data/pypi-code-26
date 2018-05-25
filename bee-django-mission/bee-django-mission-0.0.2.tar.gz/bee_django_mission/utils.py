#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'bee'
import json, pytz
from django.conf import settings
from django.apps import apps
from django.contrib.auth.models import User
from django.http import HttpResponse
from datetime import datetime
from django.conf import settings
from django.apps import apps

from .models import Stage, UserStage, UserMission, Mission, Line, UserLine

LOCAL_TIMEZONE = pytz.timezone('Asia/Shanghai')


class JSONResponse(HttpResponse):
    def __init__(self, obj):
        if isinstance(obj, dict):
            _json_str = json.dumps(obj)
        else:
            _json_str = obj
        super(JSONResponse, self).__init__(_json_str, content_type="application/json;charset=utf-8")


# ====dt====
# 获取本地当前时间
def get_now(tz=LOCAL_TIMEZONE):
    return datetime.now(tz)


def get_user_model():
    if settings.COIN_USER_TABLE in ["", None]:
        user_model = User
    else:
        app_name = settings.COIN_USER_TABLE.split(".")[0]
        model_name = settings.COIN_USER_TABLE.split(".")[1]
        app = apps.get_app_config(app_name)
        user_model = app.get_model(model_name)
    return user_model


# 获取登录用户
def get_login_user(request):
    if settings.COIN_USER_TABLE in ["", None]:
        return request.user

    token = request.COOKIES.get('cookie_token', '')
    # 没有登录
    if not token:
        return None

    try:
        user_table = get_user_model()
        user = user_table.objects.get(token=token)
        return user
    except:
        return None


# 获取自定义user的自定义name
def get_user_name(user):
    try:
        return getattr(user, settings.COIN_USER_NAME_FIELD)
    except:
        return None


def get_default_name():
    return settings.COIN_DEFAULT_NAME


# ====================
# 给某学生添加长线任务，check检查是否已有长线任务，如果有，则不添加。默认检查
def add_user_line(user, line_type, check=True):
    if check:
        try:
            UserLine.objects.get(user=user, line__line_type=line_type)
            return None
        except:
            pass
    line = Line.objects.all().filter(line_type=line_type).first()
    u_l = UserLine()
    u_l.line = line
    u_l.user = user
    u_l.save()
    return u_l

# 给某学生添加周任务，check检查是否已有周任务，如果有，则不添加。默认检查
# def add_user_week_line(user, check=True):
#     if check:
#         try:
#             UserLine.objects.get(user=user, line__line_type=2)
#             return None
#         except:
#             pass
#     line = Line.objects.all().filter(line_type=2).first()
#     u_l = UserLine()
#     u_l.line = line
#     u_l.user = user
#     u_l.save()
#     return u_l

# def update_user_missions(user, stage_list=None):
#     # 没有指定stage，则更新学生所有未完成任务
#     if not stage_list:
#         user_stage_list = UserStage.objects.filter(user=user, finish_at__isnull=True)
#         stage_list = []
#         for s in user_stage_list:
#             try:
#                 stage = Stage.objects.get(id=s.stage.id)
#                 stage_list.append(stage)
#             except:
#                 continue
