# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import UserStage

# class UserStageFinishForm(forms.ModelForm):
#
#     class Meta:
#         model = UserStage
#         fields = ['name', "order_by", "is_show", "notice", "cert_image", 'icon']