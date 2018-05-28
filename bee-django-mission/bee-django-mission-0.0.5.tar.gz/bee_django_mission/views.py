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
from .forms import MissionForm

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

#======Mission start =========
class MissionList(ListView):
    model = Mission
    template_name = 'bee_django_mission/mission/list.html'
    context_object_name = 'mission_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(MissionList, self).get_context_data(**kwargs)

        return context

class MissionDetail(DetailView):
    model = Mission
    template_name = 'bee_django_mission/mission/detail.html'
    context_object_name = 'mission'


@method_decorator(cls_decorator(cls_name='MissionCreate'), name='dispatch')
class MissionCreate(CreateView):
    model = Mission
    form_class = MissionForm
    template_name = 'bee_django_mission/mission/form.html'


@method_decorator(cls_decorator(cls_name='MissionUpdate'), name='dispatch')
class MissionUpdate(UpdateView):
    model = Mission
    form_class = MissionForm
    template_name = 'bee_django_mission/mission/form.html'

    # def get_context_data(self, **kwargs):
    #     context = super(MissionUpdate, self).get_context_data(**kwargs)
    #     # context["source"] = Source.objects.get(id=self.kwargs["pk"])
    #     return context


@method_decorator(cls_decorator(cls_name='MissionDelete'), name='dispatch')
class MissionDelete(DeleteView):
    model = Mission
    success_url = reverse_lazy('bee_django_mission:mission_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)
#======Mission end =========

class CommingSoon(TemplateView):
    template_name = 'bee_django_mission/mission/comming_soon.html'


@method_decorator(cls_decorator(cls_name='UserStageDetail'), name='dispatch')
class UserStageDetail(DetailView):
    model = UserStage
    template_name = None
    context_object_name = 'user_stage'
    template_name_week = 'bee_django_mission/user/mission/week_list.html'
    template_name_unlimited = 'bee_django_mission/user/mission/unlimited_list.html'

    def get_user_stage(self):
        # print(self.kwargs['pk'])
        user_stage_id = self.kwargs["pk"]
        return get_object_or_404(UserStage, pk=user_stage_id)

    def get_user_line(self):
        user_stage = self.get_user_stage()
        return get_object_or_404(UserLine, userstage=user_stage)

    def get_user_stage_list(self):
        user_line = self.get_user_line()
        return user_line.get_user_all_stage()

    def get_context_data(self, **kwargs):
        context = super(UserStageDetail, self).get_context_data(**kwargs)
        user_stage = self.get_user_stage()
        user_stage_list = self.get_user_stage_list()
        user_mission_list = UserMission.objects.filter(user_stage=user_stage)
        context["user_stage_list"] = user_stage_list
        res=user_stage.check_user_mission_finish
        if res and user_stage.stutas == 0:
            context["can_finish"] = True
        context["user_mission_list"] = user_mission_list
        return context

    def get_template_names(self):
        user_line = self.get_user_line()
        line = user_line.line
        if line.line_type == 1:
            return self.template_name_unlimited
        if line.line_type == 2:
            return self.template_name_week


class UserMissionList(RedirectView):
    success_pattern_name = "bee_django_mission:user_stage_detail"
    comming_soon_pattern_name = "bee_django_mission:comming_soon"

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
            # user_stage.update_user_stage_finish()
            self.url = reverse(self.success_pattern_name, kwargs={"pk": user_stage.id})
        else:
            # self.pattern_name = 'bee_django_mission:comming_soon'
            self.url = reverse(self.comming_soon_pattern_name)
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
    else:
        return None
    # finished_user_stage = user_line.get_last_user_stage(status_list=[1])
    # if finished_user_stage:
    #     return finished_user_stage
    # return None
