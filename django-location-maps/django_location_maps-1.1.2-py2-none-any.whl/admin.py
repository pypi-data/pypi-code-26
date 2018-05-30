# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from location.inlines import CountryTranslationsTabularInline, StateTranslationTabularInline, \
    CityTranslationTabularInline
from .forms import LocationForm, CountryForm, CityForm, StateForm
from .models import *
from .filters import CountryFilter, Translation


class CityAdmin(admin.ModelAdmin):
    form = CityForm
    inlines = (CityTranslationTabularInline,)


admin.site.register(City, CityAdmin)


class StateAdmin(admin.ModelAdmin):
    form = StateForm
    inlines = (StateTranslationTabularInline,)

    list_display = (
        'name',
        'country',
        'translations',
    )

    list_filter = (
        'country',
        CountryFilter,
        Translation
    )

    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.6-rc.0/js/select2.full.min.js',
        )
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.6-rc.0/css/select2.min.css',)
        }

    def translations(self, obj):
        return obj.translations
    translations.short_description = _('Traduções')

    def name(self, obj):
        return obj.name
    name.short_description = _('Nome')

admin.site.register(State, StateAdmin)


class CountryAdmin(admin.ModelAdmin):
    form = CountryForm
    inlines = (CountryTranslationsTabularInline,)


admin.site.register(Country, CountryAdmin)


class LocationAdmin(admin.ModelAdmin):
    change_form_template = 'admin/location/change_form_location.html'
    form = LocationForm
    model = Location
    prepopulated_fields = {"slug": ("address",)}
    fieldsets = (
        (
            _('Location'), {
                'fields': (
                    'map',
                    'field1',
                    'country',
                    'states',
                    'city',
                    'neighborhood',
                    'postal_code',
                    'address',
                    'street_number',
                    'complement',
                    'latitude',
                    'longitude',
                )
            }
        ),
    )

    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        super(LocationAdmin, self).__init__(model, admin_site)

    def get_urls(self):
        urls = super(LocationAdmin, self).get_urls()
        my_urls = [
            url(r'^cities/', self.admin_site.admin_view(self.cities), name='city'),
            url(r'^states/', self.admin_site.admin_view(self.states), name='state'),
        ]
        return my_urls + urls

    def cities(self, request):
        cities = [{'id': city.pk, 'name': city.name} for city in
                  City.objects.filter(state=request.GET.get('state')).all()]
        return HttpResponse(json.dumps(cities),
                            content_type='application/json')

    def states(self, request):
        states = [{'id': state.pk, 'name': state.name} for state in
                  State.objects.filter(country=request.GET.get('country')).all()]
        return HttpResponse(json.dumps(states), content_type='application/json')
