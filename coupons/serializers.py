# -*- coding:utf8 -*-

from rest_framework import serializers
from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)
from horizon.models import model_to_dict
from horizon import main

from coupons.models import (CouponsConfig,
                            DishesDiscountConfig,
                            COUPONS_CONFIG_TYPE_CN_MATCH,
                            COUPONS_CONFIG_TYPE)

import urllib
import os
import json
import re
import copy


class CouponsSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            if data['type'] != COUPONS_CONFIG_TYPE['custom']:
                data['type_detail'] = COUPONS_CONFIG_TYPE_CN_MATCH[data['type']]
            super(CouponsSerializer, self).__init__(data=data, **kwargs)
        else:
            super(CouponsSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = CouponsConfig
        fields = '__all__'

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        if 'type' in validated_data:
            if validated_data['type'] != COUPONS_CONFIG_TYPE['custom']:
                validated_data['type_detail'] = COUPONS_CONFIG_TYPE_CN_MATCH[validated_data['type']]
        return super(CouponsSerializer, self).update(instance, validated_data)

    def delete(self, instance):
        validated_data = {'status': 2,
                          'name': '%s-%s' % (instance.name, main.make_random_char_and_number_of_string(5))}
        return self.update(instance, validated_data)


class CouponsListSerializer(BaseListSerializer):
    child = CouponsSerializer()
