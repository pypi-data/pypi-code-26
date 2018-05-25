# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.db import models
from django.db.models import Count, Sum, Max, Min
from django.db.models.functions import TruncMonth, TruncDay
from django.core.urlresolvers import reverse
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.apps import apps
from django.utils import timezone

from .dt import get_current_week_range_datetime, get_now, LOCAL_TIMEZONE


# 更新任务
def update_user_missions(user, stage_list):
    for stage in stage_list:
        mission_list = Mission.objects.filter(stage=stage)
        for mission in mission_list:
            # 检查重复，没有则创建
            try:
                UserMission.objects.get(user=user, mission=mission)
                continue
            except:
                user_mission = UserMission()
                user_mission.user = user
                user_mission.mission = mission
                user_mission.save()


# Create your models here.

class ContentType(models.Model):
    app_label = models.CharField(max_length=180, verbose_name='app名')
    model = models.CharField(max_length=180, verbose_name='模块名')
    user_field = models.CharField(max_length=180, verbose_name='用户字段名')
    info = models.CharField(max_length=180, verbose_name='备注', null=True)

    class Meta:
        db_table = 'bee_django_mission_content_type'
        app_label = 'bee_django_mission'
        ordering = ['id']
        unique_together=("app_label",'model')

    def __str__(self):
        return self.app_label + '.' + self.model


LINE_TYPE_CHOICES = ((1, "长期任务"), (2, '周任务'))


class Line(models.Model):
    name = models.CharField(max_length=180, verbose_name='标题')
    created_at = models.DateTimeField(auto_now_add=True)
    line_type = models.IntegerField(default=0, choices=LINE_TYPE_CHOICES)
    auto_finish = models.BooleanField(default=True, verbose_name='是否自动完成')
    auto_start = models.BooleanField(default=True, verbose_name='是否自动开启下一个')

    class Meta:
        db_table = 'bee_django_mission_line'
        app_label = 'bee_django_mission'
        ordering = ['id']
        verbose_name = '任务线'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    # 获取下一个stage，如stage为空，则获取第一个stage
    def get_next_stage(self, last_stage=None):
        if last_stage:
            current_stage_level = last_stage.level
        else:
            current_stage_level = 0
        next_stage_list = self.stage_set.filter(level__gt=current_stage_level).order_by("level")
        if next_stage_list.count() > 0:
            next_stage = next_stage_list.first()
            return next_stage
        else:
            return None


            # def add_user_first_stage(self, user):
            #     # 已经有未完成的stage
            #     user_stage_list = UserStage.objects.filter(user=user, finish_at__isnull=True)
            #     if user_stage_list.count() > 0:
            #         return
            #
            #     # 找到第一个任务块
            #     stage_list = self.stage_set.all().order_by("level")
            #     if stage_list.count() > 0:
            #         stage = stage_list.first()
            #     else:
            #         return
            #
            #     # 添加
            #     u_s = UserStage()
            #     u_s.user = user
            #     u_s.stage = stage
            #     u_s.save()
            #     return
            #
            # def add_user_next_stage(self, user):
            #     # 已经有未完成的stage
            #     user_stage_list = UserStage.objects.filter(user=user, finish_at__isnull=True)
            #     if user_stage_list.count() > 0:
            #         return
            #
            #     # 找到当前最高stage
            #     user_stage_list = UserStage.objects.filter(user=user, finish_at__isnull=False).order_by('-stage__level')
            #     if user_stage_list.count() > 0:
            #         user_stage = user_stage_list.first()
            #         max_stage_level = user_stage.level
            #     else:
            #         return
            #
            #     stage_list = self.stage_set.filter().order_by("level")


class Stage(models.Model):
    line = models.ForeignKey(Line, on_delete=models.SET_NULL, null=True)
    level = models.IntegerField(verbose_name='阶段', null=True)
    name = models.CharField(max_length=180, verbose_name='标题')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("line", "level")
        db_table = 'bee_django_mission_stage'
        app_label = 'bee_django_mission'
        ordering = ['level']
        verbose_name = '阶段任务'

    def __str__(self):
        return self.line.name + "-" + self.name

    def __unicode__(self):
        return self.line.name + "-" + self.name

        # def add_to_user_stage(self, user):
        #     user_stage = UserStage()
        #     user_stage.user = user
        #     user_stage.stage = self
        #     user_stage.save()
        #
        # def update_user_mission(self, user):
        #     mission_list = self.mission_set.all()
        #     for mission in mission_list:
        #         # 检查重复，没有则创建
        #         try:
        #             UserMission.objects.get(user=user, mission=mission)
        #             continue
        #         except:
        #             user_mission = UserMission()
        #             user_mission.user = user
        #             user_mission.mission = mission
        #             user_mission.save()


MISSION_AGGREGATE_TYPE_CHOICES = ((1, "Count"), (2, "Sum"), (3, "TruncDay"))
MISSION_COMPARISON_TYPE_CHOICES = ((1, '>='), (2, '>'))
MISSION_OPERATOR_TYPE_CHOICES = ((0,'无'),(1, '* 60'),)


class MissionType(models.Model):
    name = models.CharField(max_length=180, verbose_name='标题',unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, verbose_name='app及model')
    aggregate_type = models.IntegerField(default=1, choices=MISSION_AGGREGATE_TYPE_CHOICES,
                                         verbose_name='聚合类型')  # max/count/sum
    field_name = models.CharField(max_length=180, default='id', verbose_name='取值字段名')
    timestamp_field = models.CharField(max_length=180, verbose_name='时间字段名', null=True, blank=True)
    comparison_type = models.IntegerField(verbose_name='比较类型', choices=MISSION_COMPARISON_TYPE_CHOICES,
                                          default=1)  # 大于等于小于
    operator_type = models.IntegerField(verbose_name='对值运算', choices=MISSION_OPERATOR_TYPE_CHOICES,
                                        default=0)
    conditions = models.TextField(verbose_name='其他附加条件', help_text='格式为：[条件1：值1，条件2：值2]，多个条件用,分割', null=True,
                                  blank=True)

    link_url = models.CharField(max_length=180, null=True, blank=True, verbose_name='链接地址')
    link_name = models.CharField(max_length=180, null=True, blank=True, verbose_name='链接名字')

    class Meta:
        db_table = 'bee_django_mission_type'
        app_label = 'bee_django_mission'
        ordering = ['id']
        verbose_name = u'任务类型'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Mission(models.Model):
    mission_type = models.ForeignKey(MissionType, on_delete=models.SET_NULL, null=True)
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=180, verbose_name='标题')
    count = models.IntegerField(verbose_name='数量')
    info = models.TextField(verbose_name='备注', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_by = models.IntegerField(verbose_name='顺序', null=True, blank=True)

    class Meta:
        db_table = 'bee_django_mission'
        app_label = 'bee_django_mission'
        ordering = ['created_at']
        verbose_name = '任务'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class UserLine(models.Model):
    line = models.ForeignKey(Line)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    start_at = models.DateTimeField(auto_now_add=True)
    finish_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'bee_django_mission_user_line'
        app_label = 'bee_django_mission'
        ordering = ['start_at']
        verbose_name = '学生任务线'

    def __str__(self):
        return self.line.name

    def __unicode__(self):
        return self.line.name

    # 获取该学生，同一user_line下，最后完成的user_stage
    def get_last_finished_user_stage(self):
        finished_user_stage_list = UserStage.objects.filter(user_line=self, finish_at__isnull=False).order_by(
            'finish_at')
        if finished_user_stage_list.count() > 0:
            return finished_user_stage_list.last()
        else:
            return None

    # 获取该学生，同一user_line下的所有stage
    def get_all_user_stage(self):
        user_stage_list = UserStage.objects.filter(user_line=self).order_by(
            'finish_at')
        return user_stage_list

    # 获取该学生，同一user_line下，正在进行的user_stage
    def get_woking_user_stage(self):
        woking_user_stage_list = UserStage.objects.filter(user_line=self, finish_at__isnull=True).order_by(
            'finish_at')
        if woking_user_stage_list.count() == 1:
            return woking_user_stage_list.last()
        else:
            return None

    # 添加下一个或第一个user_stage
    # 参数：check检查是否已经有同类型的已开启的user_stage。为true时，不添加，false时，强行再添加一个
    def add_user_stage(self, check=True):
        # 已经有未完成的stage
        if check == True:
            user_stage_list = UserStage.objects.filter(user_line__user=self.user, finish_at__isnull=True,
                                                       user_line__line__line_type=self.line.line_type)
            if user_stage_list.count() > 0:
                return


        # 找到第一个任务块
        last_finished_user_stage = self.get_last_finished_user_stage()
        if last_finished_user_stage:
            last_stage = last_finished_user_stage.stage
        else:
            last_stage = None
        next_stage = self.line.get_next_stage(last_stage)

        # 添加阶段任务
        if next_stage:
            new_user_stage = UserStage()
            new_user_stage.user_line = self
            new_user_stage.stage = next_stage
            # 如果是周任务，添加结束时间
            if self.line.line_type == 2:
                start_dt, end_dt = get_current_week_range_datetime()
                new_user_stage.start_at = start_dt
                new_user_stage.end_at = end_dt
                new_user_stage.name = start_dt.strftime("%Y") + '年第' + start_dt.strftime("%W") + "周任务"
            new_user_stage.save()
        return


class UserStage(models.Model):
    user_line = models.ForeignKey(UserLine)
    stage = models.ForeignKey(Stage)
    name = models.CharField(max_length=180, null=True, verbose_name='标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    start_at = models.DateTimeField(default=timezone.now, verbose_name='开始时间')
    finish_at = models.DateTimeField(null=True, verbose_name='完成时间')
    end_at = models.DateTimeField(null=True, verbose_name='结束时间')

    class Meta:
        db_table = 'bee_django_mission_user_stage'
        app_label = 'bee_django_mission'
        ordering = ['start_at']
        verbose_name = '学生阶段任务'

    def __str__(self):
        return self.stage.name

    def get_name(self):
        if self.name:
            return self.name
        return self.stage.name

    # 添加当前user_stage下的所有mission
    def add_user_missions(self):
        # 已经有未完成的stage
        mission_list = Mission.objects.filter(stage=self.stage)

        for mission in mission_list:
            # 已经添加过该mission
            try:
                UserMission.objects.get(mission=mission, user_stage=self)
            except:
                new_user_misssion = UserMission()
                new_user_misssion.user_stage = self
                new_user_misssion.mission = mission
                new_user_misssion.save()

    # 检查stage是否完成
    def check_finish(self):
        unfinish_list = UserMission.objects.filter(user_stage=self, finish_at__isnull=True)
        if unfinish_list.count() > 0:
            return False
        return True

    # 更新user_stage的完成情况，并根据情况，开启下一stage
    # manual是否为手动完成
    def update_user_stage_finish(self, manual=False):
        # 如果任务线为不自动完成，则不更新
        if not manual:
            if not self.user_line.line.auto_finish:
                return

        res = self.check_finish()
        if res:
            self.finish_at = get_now()
            self.save()
            self.user_line.add_user_stage()

            # 结束任务stage，并开启下一个stage
            # def finish_and_start_next_user_stage(self):
            #     try:
            #         self.finish_at = datetime.datetime.now()
            #         self.save()
            #     except Exception as e:
            #         print(e)
            #
            #     current_stage = self.stage
            #     current_line = self.stage.line
            #
            #     # 有未完成stage，则退出
            #     user_stage_list = UserStage.objects.filter(user=self.user, finish_at__isnull=True)
            #     if user_stage_list.count() > 0:
            #         return
            #
            #     # 找到下一个stage
            #     next_stage_list = Stage.objects.filter(level__gt=current_stage.level, line=current_line)
            #     if next_stage_list.count() > 0:
            #         next_stage = next_stage_list.first()
            #         # 添加到该用户
            #         next_stage.add_to_user_stage(self.user)


class UserMission(models.Model):
    # line = models.ForeignKey(Line)
    user_stage = models.ForeignKey(UserStage)
    mission = models.ForeignKey(Mission)
    custom_name = models.CharField(max_length=180, blank=True, null=True, verbose_name='自定义名字')
    custom_count = models.IntegerField(blank=True, null=True, verbose_name='自定义数量')
    # user = models.ForeignKey(settings.AUTH_USER_MODEL)
    finish_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'bee_django_mission_user_mission'
        app_label = 'bee_django_mission'
        ordering = ['finish_at']
        verbose_name = '学生的任务'

    def __str__(self):
        return self.mission.name

    def __unicode__(self):
        return self.mission.name

    def get_name(self):
        if self.custom_name:
            return self.custom_name
        return self.mission.name

    def get_count(self):
        if self.custom_count:
            return self.custom_count
        return self.mission.count

    # 获取user_mission的完成情况
    def get_user_mission_progress(self):
        if self.finish_at:
            return 1
        # 表
        content_type = self.mission.mission_type.content_type
        app_name = content_type.app_label
        model_name = content_type.model
        app = apps.get_app_config(app_name)
        model = app.get_model(model_name)
        print(app, model)
        # 查询条件
        user_field = content_type.user_field

        aggregate_type = self.mission.mission_type.aggregate_type
        field_name = self.mission.mission_type.field_name
        timestamp_field = self.mission.mission_type.timestamp_field
        comparison_type = self.mission.mission_type.comparison_type  # 大于等于小于
        operator_type = self.mission.mission_type.operator_type  # 对count做运算
        conditions = self.mission.mission_type.conditions
        count = self.get_count()
        if operator_type == 1:
            count = count * 60



        # 查询
        try:
            queryset = model.objects.all()
            # print(queryset)
            if queryset.count() == 0:
                return 0
            kwargs = {}  # 动态查询的字段
            # name_field = get_user_name_field()
            kwargs[user_field] = self.user_stage.user_line.user
            if conditions:
                condition_list = conditions.split(',')
                # print(condition_list)
                for condition in condition_list:
                    # print(condition)
                    key = condition.split(':')[0]
                    value = condition.split(':')[1]
                    kwargs[key] = value
            # 周任务
            if self.user_stage.user_line.line.line_type == 2:
                kwargs[timestamp_field + "__range"] = [self.user_stage.start_at, self.user_stage.end_at]

            # print(kwargs)
            queryset = queryset.filter(**kwargs)
            if queryset.count() == 0:
                return 0
            # print(queryset)
            # 聚合查询
            if aggregate_type == 1:  # count
                queryset = queryset.aggregate(_agg=Count(field_name))
            elif aggregate_type == 2:  # sum
                queryset = queryset.aggregate(_agg=Sum(field_name))
            elif aggregate_type == 3:  # TruncDay
                _queryset = queryset.annotate(day=TruncDay(field_name, tzinfo=LOCAL_TIMEZONE)).values('day').annotate(
                    count=Count('id')).values('day') \
                    .order_by('day')
                queryset = {}
                queryset["_agg"] = _queryset.count()

            else:
                return 0
            print(self.mission.name)
            print(queryset)
            print(count)
            # 比较
            if comparison_type == 1:
                res = queryset["_agg"] >= count
            elif comparison_type == 2:
                res = queryset["_agg"] > count
            else:
                res = None

            if res:
                print('finished')
                self.finish_at = get_now()
                self.save()
                return 1
            else:

                print(queryset["_agg"])
                print('not finished')
                return round(queryset["_agg"].__int__(), 2) / count.__int__()


        except Exception as e:
            print(e)
        return 0


# 创建user_line后，自动创建该用户对应的stage
@receiver(post_save, sender=UserLine)
def create_user_stage(sender, **kwargs):
    user_line = kwargs['instance']
    if kwargs['created']:
        user_line.add_user_stage(check=True)


# 创建user_stage后，自动创建该用户对应stage里的所有mission
@receiver(post_save, sender=UserStage)
def create_user_missions(sender, **kwargs):
    user_stage = kwargs['instance']
    if kwargs['created']:
        user_stage.add_user_missions()
