# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.apps import apps
from django.conf import settings
from bee_django_crm.models import PreUser
from bee_django_course.cc import create_room


# Create your models here.


# def get_crm_preuser():
#     if settings.CRM_PREUSER:
#         return settings.CRM_PREUSER
#     return None


# 用户，扩展的user
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    student_id = models.IntegerField(verbose_name='学号', unique=True, null=True)
    room_id = models.CharField(max_length=180, verbose_name='习琴室ID', null=True, blank=True)
    user_class = models.ForeignKey('bee_django_user.UserClass', verbose_name='用户班级', on_delete=models.SET_NULL,
                                   null=True, blank=True)
    if settings.CRM_PREUSER:
        preuser = models.OneToOneField(settings.CRM_PREUSER, verbose_name='crm用户', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bee_django_user_profile'
        app_label = 'bee_django_user'
        ordering = ['-created_at']
        permissions = (
            ('can_manage', '可以访问后台管理'),
            ('can_change_user_group', '可以修改用户组'),
            ('view_all_users', '可以查看所有用户'),
            ('view_manage_users', '可以查看管理的用户'),
            ('view_teach_users', '可以查看教的用户'),
        )

    def __str__(self):
        return self.user.username

    def has_group(self, group_name):
        group_name_list = []
        for group in self.user.groups.all():
            group_name_list.append(group.name)
        print(group_name_list)
        if group_name in group_name_list:
            return True
        return False

    @classmethod
    def fix_cc_room_id(cls):
        for e in cls.objects.all():
            if not e.room_id:
                room_id = create_room(e.preuser.name + '的直播间')
                if room_id:
                    e.room_id = room_id
                    e.save()

                    # def has_manage(self):
                    #     try:
                    #         if self.has_group("管理员") or self.has_group("客服") or self.has_group("助教"):
                    #             return True
                    #     except:
                    #         return False
                    #     return False

                    # # 获取学生列表数据集
                    # def get_user_list_queryset(self):
                    #     if self.has_group("管理员") or self.has_group("客服"):
                    #         return User.objects.all()
                    #     elif self.has_group("助教"):
                    #         return User.objects.filter(userprofile__user_class__assistant__userprofile=self)
                    #     return []


@receiver(post_save, sender=UserProfile)
def create_user(sender, **kwargs):
    user_pofile = kwargs['instance']
    if kwargs['created']:
        user = User.objects.create_user(username=settings.USER_EX_USERNAME + user_pofile.student_id.__str__(),
                                        password=settings.USER_DEFAULT_PASSWORD)
        user.first_name = user_pofile.preuser.name
        user.save()
        user_pofile.user = user
        user_pofile.save()
        try:
            group = Group.objects.get(name='学生')
            user.groups.add(group)
        except Exception as e:
            print(e)



            # user_profile_list = UserProfile.objects.all().order_by("-student_id")
            # if user_profile_list.count() >= 1:
            #     max_student_id = user_profile_list.first().student_id
            # else:
            #     max_student_id = 0

    return


# @receiver(post_save, sender=User)
# def create_user_profile(sender, **kwargs):
#     user = kwargs['instance']
#     if kwargs['created']:
#         user_profile_list = UserProfile.objects.all().order_by("-student_id")
#         if user_profile_list.count() >= 1:
#             max_student_id = user_profile_list.first().student_id
#         else:
#             max_student_id = 0
#         user_profile = UserProfile(user=user)
#         user_profile.student_id = max_student_id + 1
#         user_profile.save()
#     return
# 如果有crm，则创建并关联crm用户
# res = apps.is_installed("bee_django_crm")
# if not res:
#     return
# try:
#     from bee_django_crm.models import PreUser
#     preuser = PreUser(user=user)
#     preuser.save()
# except:
#     return


# 班级
class UserClass(models.Model):
    name = models.CharField(max_length=180, verbose_name='班级名称')
    assistant = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='助教', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'bee_django_user_class'
        app_label = 'bee_django_user'
        ordering = ['-created_at']
        permissions = (
            ('view_all_classes', '可以查看所有班级'),
            ('view_manage_classes', '可以查看管理的班级'),
            ('view_teach_classes', '可以查看教的班级'),
        )
