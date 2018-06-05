# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from django.contrib.auth.models import User, Group

from .models import UserProfile, UserClass
from django.forms.models import inlineformset_factory


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name"]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["user_class"]


profile_inline_formset = inlineformset_factory(User, UserProfile, form=UserProfileForm, can_delete=False)


class UserClassForm(forms.ModelForm):
    assistant_queryset = User.objects.filter(groups__name__in=['助教'])
    assistant = forms.ModelChoiceField(queryset=assistant_queryset, label='助教', required=False)

    class Meta:
        model = UserClass
        fields = ["name", 'assistant']


class UserGroupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['groups']