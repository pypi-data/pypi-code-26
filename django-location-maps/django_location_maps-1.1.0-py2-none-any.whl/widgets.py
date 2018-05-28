# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language


class MapWidget(forms.Widget):
    template_name = 'admin/location/map.html'
    latitude = None
    longitude = None
    lang = get_language()

    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe(
            render_to_string(
                self.template_name,
                {
                    'latitude': self.latitude,
                    'longitude': self.longitude,
                    'name': name,
                    'attrs': attrs,
                }
            )
        )

    @property
    def media(self):
        return forms.Media(
            css={
                'all': (
                    'css/custom.css',
                )
            },
            js=(
                'js/jquery-1.12.4.js',
                'js/location.js',
                'https://maps.googleapis.com/maps/api/js?' +
                'key=' + settings.GOOGLE_MAPS_API_KEY +
                '&language=' + get_language() +
                '&libraries=places' +
                '&callback=DjangoMap.init',

            )
        )
