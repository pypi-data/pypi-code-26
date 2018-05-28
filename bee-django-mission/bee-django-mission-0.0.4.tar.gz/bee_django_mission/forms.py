# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import Mission

class MissionForm(forms.ModelForm):

    class Meta:
        model = Mission
        fields = ['mission_type', "stage", "name", "count", "info", 'order_by']