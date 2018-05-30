# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import Mission, Stage, UserLine, Line


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ["name", 'level']


class StageUnlimitedForm(StageForm):
    def clean(self):
        level = self.cleaned_data['level']
        stage_list = Stage.objects.filter(level=level, line__line_type=1)
        for s in stage_list:
            print(s.id)
        is_exist = stage_list.exists()

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


class UserLineCreateForm(forms.ModelForm):
    class Meta:
        model = UserLine
        fields = ['line']

    def __init__(self,*args, **kwargs):
        super(UserLineCreateForm, self).__init__(*args, **kwargs)
        line_queryset = Line.objects.filter(line_type=1)
        self.fields["line"] = forms.ModelChoiceField(queryset=line_queryset, label='任务线', required=True)
