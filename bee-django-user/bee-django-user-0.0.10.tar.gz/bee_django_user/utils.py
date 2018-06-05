# -*- coding:utf-8 -*-
__author__ = 'bee'

from bee_django_user.models import UserProfile


def get_max_student_id():
    user_profile_list = UserProfile.objects.filter(student_id__isnull=False).order_by("-student_id")
    if user_profile_list.count() >= 1:
        max_student_id = user_profile_list.first().student_id

    else:
        max_student_id = 0
    return max_student_id
