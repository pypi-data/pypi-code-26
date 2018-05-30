# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_filters import FilterSet

from ..models import Country, State, City


class CountryFilterSet(FilterSet):
    class Meta:
        model = Country
        fields = (
            'code2',
            'code3'
        )


class StateFilterSet(FilterSet):

    class Meta:
        model = State
        fields = (
            'code',
            'country',
            'country__code2',
            'country__code3'
        )


class CityFilterSet(FilterSet):

    class Meta:
        model = City
        fields = (
            'state',
            'state__code',
            'state__country',
            'state__country__code2',
            'state__country__code3'
        )
