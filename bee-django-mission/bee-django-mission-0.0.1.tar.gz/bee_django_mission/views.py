# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, qrcode, os, shutil, urllib
from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.views.generic import ListView, DetailView, TemplateView, RedirectView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.utils.datastructures import MultiValueDict
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.utils.six import BytesIO
from django.apps import apps
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django import forms

from .decorators import cls_decorator, func_decorator
from .models import Line, Stage, Mission, UserLine, UserStage, UserMission
from .utils import add_user_line


# from .forms import UserStageFinishForm


# Create your views here.
def test(request):
    user = request.user
    # ====init
    # line = Line.objects.all().filter(line_type=2).first()
    # u_l = UserLine()
    # u_l.line = line
    # u_l.user = user
    # u_l.save()

    # ====check mission
    # ret=check_user_mission_finish(user)
    # ul=UserLine.objects.all().first()
    # us.finish_and_start_next_user_stage()


    # print(ret)
    # ==update missions
    user_stage = UserStage.objects.get(id=1)
    user_stage.add_user_missions()
    return


def comming_soon(request):
    return render(request, 'bee_django_mission/comming_soon.html')


@method_decorator(cls_decorator(cls_name='UserStageDetail'), name='dispatch')
class UserStageDetail(DetailView):
    model = UserStage
    template_name = None
    context_object_name = 'user_stage'

    def get_user_stage(self):
        # print(self.kwargs['pk'])
        user_stage_id = self.kwargs["pk"]
        return get_object_or_404(UserStage, pk=user_stage_id)

    def get_user_line(self):
        user_stage = self.get_user_stage()
        return get_object_or_404(UserLine, userstage=user_stage)

    def get_user_stage_list(self):
        user_line = self.get_user_line()
        return user_line.get_all_user_stage()

    def get_context_data(self, **kwargs):
        context = super(UserStageDetail, self).get_context_data(**kwargs)
        user_stage = self.get_user_stage()
        user_stage_list = self.get_user_stage_list()
        user_mission_list = UserMission.objects.filter(user_stage=user_stage)
        context["user_stage_list"] = user_stage_list
        context["is_finished"] = user_stage.finish_at
        context["can_finish"] = user_stage.check_finish()
        context["user_mission_list"] = user_mission_list
        return context

    def get_template_names(self):
        user_line = self.get_user_line()
        line = user_line.line
        if line.line_type == 1:
            return 'bee_django_mission/user/mission/unlimited_list.html'
        if line.line_type == 2:
            return 'bee_django_mission/user/mission/week_list.html'


class UserMissionList(RedirectView):
    def get_line_type(self):
        return 0

    def get_redirect_url(self, *args, **kwargs):
        # 获取周任务，没有则添加

        user_id = self.kwargs["user_id"]
        line_type = self.get_line_type()
        user_line = None
        try:
            user_line = UserLine.objects.get(user_id=user_id, line__line_type=line_type)
        except:
            if line_type == 2:
                user = get_object_or_404(User, pk=user_id)
                user_line = add_user_line(user, line_type)
        user_stage = get_user_stage(user_line)
        if user_stage:
            # 更新阶段任务的完成状态
            user_stage.update_user_stage_finish()
            self.url = reverse('bee_django_mission:user_stage_detail', kwargs={"pk": user_stage.id})
        else:
            # self.pattern_name = 'bee_django_mission:comming_soon'
            self.url = reverse('bee_django_mission:comming_soon')
        return super(UserMissionList, self).get_redirect_url(*args, **kwargs)


class UserMissionListWeek(UserMissionList):
    def get_line_type(self):
        return 2


class UserMissionListUnlimited(UserMissionList, RedirectView):
    def get_line_type(self):
        return 1


# class FinishUserStage(TemplateView):
#     model = UserStage
#     form_class = UserStageFinishForm
#     template_name = 'bee_django_exam/grade/grade_form.html'
#     success_url = reverse_lazy('bee_django_exam:grade_list')

# def get(self, request, *args, **kwargs):
#     return self.http_method_not_allowed(request, *args, **kwargs)


# ============
# 获取user_line下的进行中，或已完成的阶段任务
def get_user_stage(user_line):
    if not user_line:
        return None
    woking_user_stage = user_line.get_woking_user_stage()
    if woking_user_stage:
        return woking_user_stage
    finished_user_stage = user_line.get_last_finished_user_stage()
    if finished_user_stage:
        return finished_user_stage
    return None
