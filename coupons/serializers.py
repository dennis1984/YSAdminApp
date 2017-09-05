# -*- coding:utf8 -*-

from rest_framework import serializers
from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)
from coupons.models import (CouponsConfig,
                            DishesDiscountConfig,
                            COUPONS_CONFIG_TYPE_CN_MATCH,
                            COUPONS_CONFIG_TYPE)

from Business_App.bz_dishes.models import Dishes
from horizon.models import model_to_dict
from horizon import main

import urllib
import os
import json
import re
import copy


class CouponsSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            super(CouponsSerializer, self).__init__(data=data, **kwargs)
        else:
            super(CouponsSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = CouponsConfig
        fields = '__all__'

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        return super(CouponsSerializer, self).update(instance, validated_data)

    def add_send_count(self, instance, send_count):
        validated_data = {'send_count': instance.send_count + send_count}
        return super(CouponsSerializer, self).update(instance, validated_data)

    def delete(self, instance):
        validated_data = {'status': '%d' % (instance.pk + 400 + 1)}
        return self.update(instance, validated_data)


class CouponsListSerializer(BaseListSerializer):
    child = CouponsSerializer()


class DishesDiscountSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            super(DishesDiscountSerializer, self).__init__(data=data, **kwargs)
        else:
            super(DishesDiscountSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = DishesDiscountConfig
        fields = '__all__'

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        return super(DishesDiscountSerializer, self).update(instance, validated_data)

    def delete(self, instance):
        validated_data = {'status': '%d' % (instance.pk + 400 + 1)}
        return self.update(instance, validated_data)


class DishesDiscountDetailSerializer(BaseSerializer):
    dishes_id = serializers.IntegerField()
    dishes_name = serializers.CharField()
    business_id = serializers.IntegerField()
    business_name = serializers.CharField()
    food_court_id = serializers.IntegerField()
    food_court_name = serializers.CharField()

    price = serializers.CharField()
    discount = serializers.CharField()

    service_ratio = serializers.IntegerField(allow_null=True)
    business_ratio = serializers.IntegerField(allow_null=True)

    created = serializers.CharField(allow_null=True, allow_blank=True)
    updated = serializers.CharField(allow_null=True, allow_blank=True)


class DishesDiscountListSerializer(BaseListSerializer):
    child = DishesDiscountDetailSerializer()


class CouponsSendRecordSerializer(BaseSerializer):
    id = serializers.IntegerField()
    coupons_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    phone = serializers.CharField(allow_null=True, allow_blank=True)
    count = serializers.IntegerField()
    coupons_name = serializers.CharField()
    coupons_type = serializers.IntegerField()
    created = serializers.DateTimeField()


class CouponsSendRecordListSerializer(BaseListSerializer):
    child = CouponsSendRecordSerializer()


class CouponsUsedRecordSerializer(BaseSerializer):
    id = serializers.IntegerField()
    coupons_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    phone = serializers.CharField(allow_null=True, allow_blank=True)
    count = serializers.IntegerField()
    coupons_name = serializers.CharField()
    coupons_type = serializers.IntegerField()
    created = serializers.DateTimeField()


class CouponsUsedRecordListSerializer(BaseListSerializer):
    child = CouponsUsedRecordSerializer()
