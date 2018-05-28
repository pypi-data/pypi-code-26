# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import serializers
from .models import Country, State, City, Location


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'id',
            'created_at',
            'updated_at',
            'active',
            'slug',
            'code2',
            'code3',
            'flag',
            'name',
        )


class StateSerializer(serializers.ModelSerializer):
    country = CountrySerializer(many=False)

    class Meta:
        model = State
        fields = (
            'id',
            'country',
            'created_at',
            'updated_at',
            'active',
            'code',
            'name',
        )


class CitySerializer(serializers.ModelSerializer):
    state = StateSerializer(many=False)

    class Meta:
        model = City
        fields = (
            'id',
            'state',
            'created_at',
            'updated_at',
            'active',
            'name',
        )


class LocationSerializer(serializers.ModelSerializer):
    city = CitySerializer(many=False)

    class Meta:
        model = Location
        fields = '__all__'
