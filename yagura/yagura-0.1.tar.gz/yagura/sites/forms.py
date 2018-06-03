from django import forms
from yagura.sites import models


class SiteCreateForm(forms.ModelForm):
    class Meta:
        model = models.Site
        fields = ['url', ]
