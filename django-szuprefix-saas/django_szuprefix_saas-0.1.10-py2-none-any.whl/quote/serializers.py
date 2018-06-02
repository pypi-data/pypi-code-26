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
    product_name = serializers.CharField(source="product.name", label='产品', read_only=True)

    class Meta:
        model = models.Quote
        exclude = ()
        read_only_fields = ('amount', 'amount_taxed', 'delivery_days_from', 'delivery_days_to', 'party')


class ItemSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.__str__", label='产品', read_only=True)

    class Meta:
        model = models.Item
        exclude = ()
        read_only_fields = ('amount', 'amount_taxed', 'party', 'delivery_days_from', 'delivery_days_to')


class ItemSmallSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        fields = ('product_name',)


class RequestSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", label='客户', read_only=True)
    items_count = serializers.IntegerField(source="items.count", label="产品数量", read_only=True)
    items = ItemSmallSerializer(label="产品", read_only=True, many=True)
    user_name = serializers.CharField(source="user.get_full_name", label='销售', read_only=True)

    class Meta:
        model = models.Request
        # exclude = ()
        read_only_fields = ('code', 'amount', 'amount_taxed', 'party')
        fields = (
            'customer', 'user', 'items', 'customer_name', 'amount', 'amount_taxed', 'items_count', 'create_time', 'status', 'user_name', 'code'
        )
        # todo: 如果这里用exclude, 而不用fields, 那code会一直提示不能为空, 有空去深入研究一下差别
