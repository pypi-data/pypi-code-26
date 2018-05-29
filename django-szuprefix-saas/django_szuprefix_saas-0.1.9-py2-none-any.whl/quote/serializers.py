# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django_szuprefix.api.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models
from ..saas.mixins import PartySerializerMixin


class ManufacturerSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Manufacturer
        fields = ('name', 'code')


class CompanySerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ('name', 'code', 'is_vendor', 'is_customer')


class ProductSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source="manufacturer.name", read_only=True)

    class Meta:
        model = models.Product
        fields = ('name', 'number', 'manufacturer', 'manufacturer_name', 'code')


class QuoteSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", label='供应商', read_only=True)

    class Meta:
        model = models.Quote
        fields = ('create_time', 'item', 'vendor', 'vendor_name', 'unit', 'quantity', 'amount', 'amount_taxed', 'unit_price', 'unit_price_taxed', 'delivery')


class ItemSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.__str__", label='产品', read_only=True)

    class Meta:
        model = models.Item
        fields = (
        'request', 'product', 'product_name', 'unit', 'quantity', 'amount', 'amount_taxed', 'unit_price', 'unit_price_taxed', 'delivery', 'memo')


class ItemSmallSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        fields = ('product_name',)


class RequestSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", label='客户', read_only=True)
    items_count = serializers.IntegerField(source="items.count", label="产品数量", read_only=True)
    items = ItemSmallSerializer(label="产品", read_only=True, many=True)

    class Meta:
        model = models.Request
        fields = (
        'customer', 'user', 'items', 'customer_name', 'items_count', 'amount', 'amount_taxed', 'create_time', 'status',
        'code')
        read_only_fields = ('code',)
