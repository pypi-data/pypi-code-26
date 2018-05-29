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
from .utils import check_add_user_line, get_current_week_stage
from .forms import MissionForm, StageUnlimitedForm


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


# ======Stage start =========
class StageList(ListView):
    model = Stage
    template_name = 'bee_django_mission/stage/list.html'
    context_object_name = 'stage_list'
    paginate_by = 20


class StageUnlimitedList(StageList):
    template_name = 'bee_django_mission/stage/unlimited_list.html'
    line_type = 1

    def get_queryset(self):
        queryset = super(StageUnlimitedList, self).get_queryset()
        return queryset.filter(line__line_type=self.line_type)

    def get_context_data(self, **kwargs):
        context = super(StageUnlimitedList, self).get_context_data(**kwargs)
        line = Line.objects.get(line_type=self.line_type)
        context["line"] = line
        return context


# class StageDetail(DetailView):
#     model = Mission
#     template_name = 'bee_django_mission/mission/detail.html'
#     context_object_name = 'mission'


@method_decorator(cls_decorator(cls_name='StageCreate'), name='dispatch')
class StageCreate(CreateView):
    model = Stage
    form_class = StageUnlimitedForm
    template_name = 'bee_django_mission/stage/form.html'

    def form_valid(self, form):
        stage = form.save(commit=False)
        line = Line.objects.get(id=self.kwargs["line_id"])
        stage.line = line
        stage.save()
        return super(StageCreate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='StageUpdate'), name='dispatch')
class StageUpdate(UpdateView):
    model = Stage
    form_class = StageUnlimitedForm
    template_name = 'bee_django_mission/stage/form.html'


@method_decorator(cls_decorator(cls_name='StageDelete'), name='dispatch')
class StageDelete(DeleteView):
    model = Mission
    success_url = reverse_lazy('bee_django_mission:stage_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# ======Mission end =========


# ======Mission start =========
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
    form_class = None
    template_name = 'bee_django_mission/mission/form.html'
    fields = ['mission_type', "stage", "name", "count", "info", 'order_by']

    def get_context_data(self, **kwargs):
        context = super(MissionCreate, self).get_context_data(**kwargs)
        line = Line.objects.get(line_type=self.kwargs["line_type"])
        context["line"] = line
        context["form"] = MissionForm(instance=self.object, line=line)
        return context


@method_decorator(cls_decorator(cls_name='MissionUpdate'), name='dispatch')
class MissionUpdate(UpdateView):
    model = Mission
    form_class = None
    template_name = 'bee_django_mission/mission/form.html'

    fields = ['mission_type', "stage", "name", "count", "info", 'order_by']

    def get_context_data(self, **kwargs):
        context = super(MissionUpdate, self).get_context_data(**kwargs)
        line = Line.objects.get(line_type=self.kwargs["line_type"])
        context["line"] = line
        context["form"] = MissionForm(instance=self.object, line=line)
        return context

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


# ======Mission end =========

class CommingSoon(TemplateView):
    template_name = 'bee_django_mission/mission/comming_soon.html'


# 只是获取显示，所有检查更新在UserMissionList处理
@method_decorator(cls_decorator(cls_name='UserStageDetail'), name='dispatch')
class UserStageDetail(DetailView):
    model = UserStage
    template_name = None
    context_object_name = 'user_stage'
    template_name_week = 'bee_django_mission/user/mission/week_list.html'
    template_name_unlimited = 'bee_django_mission/user/mission/unlimited_list.html'

    def get_user_stage(self):
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
        context["user_mission_list"] = user_mission_list
        context["user_stage_status"] = user_stage.stutas
        return context

    def get_template_names(self):
        user_line = self.get_user_line()
        line = user_line.line
        if line.is_unlimited_line():
            return self.template_name_unlimited
        if line.is_week_line():
            return self.template_name_week





class UserMissionList(RedirectView):
    success_pattern_name = "bee_django_mission:user_stage_detail"
    comming_soon_pattern_name = "bee_django_mission:comming_soon"

    def get_line_type(self):
        return 0

    def get_redirect_url(self, *args, **kwargs):
        # 获取周任务，没有则添加

        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, pk=user_id)
        line_type = self.get_line_type()
        user_line = None
        user_stage = None


        try:
            user_line = UserLine.objects.get(user=user, line__line_type=line_type)
        except:
            if line_type == 2:
                user_line = check_add_user_line(user, line_type, check=False)

        # 如果没有user_line,跳转错误页面
        if not user_line:
            self.url = reverse(self.comming_soon_pattern_name, kwargs={"user_id": user_id, "line_type": line_type})
            return super(UserMissionList, self).get_redirect_url(*args, **kwargs)

        # 长线任务，获取进行中的或者已完成的user_stage
        if user_line.line.is_unlimited_line():
            user_stage = user_line.get_woking_user_stage()
            if not user_stage:
                # TODO获取完成的一个user_stage
                user_stage=None

        # 周任务，获取本周user_stage
        elif user_line.line.is_week_line():
            user_stage = get_current_week_stage(user)
            # 没有本周任务，则新增加一个
            if not user_stage:
                user_stage=user_line.add_user_stage()

        if user_stage:
            # 更新mission状态
            user_stage.update_user_mission()
            # 更新阶段任务的完成状态
            user_stage.update_user_stage_status()
            self.url = reverse(self.success_pattern_name, kwargs={"pk": user_stage.id})
        return super(UserMissionList, self).get_redirect_url(*args, **kwargs)



class UserMissionListWeek(UserMissionList):
    def get_line_type(self):
        return 2


class UserMissionListUnlimited(UserMissionList):
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
        # def get_user_stage(user_line):
        #     if not user_line:
        #         return None
        #     woking_user_stage = user_line.get_woking_user_stage()
        #     if woking_user_stage:
        #         return woking_user_stage
        #     else:
        #         return None
        # finished_user_stage = user_line.get_last_user_stage(status_list=[1])
        # if finished_user_stage:
        #     return finished_user_stage
        # return None
