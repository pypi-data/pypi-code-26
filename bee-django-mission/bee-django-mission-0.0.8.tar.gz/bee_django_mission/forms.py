# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import Mission, Stage


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ["name", 'level']



class StageUnlimitedForm(StageForm):
    def clean(self):
        level = self.cleaned_data['level']
        is_exist=Stage.objects.filter(level=level, line__line_type=2).exists()
        if is_exist:
            raise forms.ValidationError(u"阶段不能重复")
        return self.cleaned_data


class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ['mission_type', "stage", "name", "count", "info", 'order_by']

    def __init__(self, line, *args, **kwargs):
        super(MissionForm, self).__init__(*args, **kwargs)
        stage_queryset = Stage.objects.filter(line=line)
        self.fields["stage"] = forms.ModelChoiceField(queryset=stage_queryset, label='所属阶段', required=True)
