# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from .models import Country


class CustomSelectFilter(SimpleListFilter):
    template = "admin/location/filters/custom_select_filter.html"


class Translation(CustomSelectFilter):
    title = _('Idioma')
    parameter_name = 'lang'

    def lookups(self, request, model_admin):
        return settings.LANGUAGES

    def queryset(self, request, queryset):
        pass


class CountryFilter(CustomSelectFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in Country.objects.all()]

    def queryset(self, request, queryset):
        if self.value() == 'AFRICA':
            return queryset.filter(country__continent='Africa')
        if self.value():
            return queryset.filter(country__id__exact=self.value())
