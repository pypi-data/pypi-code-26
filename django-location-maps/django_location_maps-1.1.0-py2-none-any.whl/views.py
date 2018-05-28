# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from .api.filters import CityFilterSet, CountryFilterSet, StateFilterSet
from .models import City, State, Country, Location
from .serializers import CitySerializer, StateSerializer, CountrySerializer, LocationSerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_class = CityFilterSet
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    http_method_names = ['get', ]


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    filter_class = StateFilterSet
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    http_method_names = ['get', ]


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_class = CountryFilterSet
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    http_method_names = ['get', ]


class LocationViewSet(viewsets.ModelViewSet):
    model = Location
    serializer_class = LocationSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = '__all__'
    http_method_names = ['get', ]

