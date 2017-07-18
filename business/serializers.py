# -*- coding:utf8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from Business_App.bz_dishes.models import (City,
                                           Dishes,
                                           FoodCourt)
from Business_App.bz_users.models import BusinessUser

from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)
from horizon.decorators import has_permission_to_update
from horizon.models import model_to_dict
from horizon import main

from django.conf import settings
import urllib
import os
import json
import re
import copy


class CitySerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            _data = copy.deepcopy(data)
            if request:
                _data['user_id'] = request.user.id
            super(CitySerializer, self).__init__(data=_data, **kwargs)
        else:
            super(CitySerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = City
        fields = '__all__'

    def save(self, **kwargs):
        try:
            return super(CitySerializer, self).save(**kwargs)
        except Exception as e:
            return e


class CityListSerializer(BaseListSerializer):
    child = CitySerializer()


class FoodCourtSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            super(FoodCourtSerializer, self).__init__(data=data, **kwargs)
        else:
            super(FoodCourtSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = FoodCourt
        fields = '__all__'


class FoodCourtListSerializer(BaseListSerializer):
    child = FoodCourtSerializer()


class UserInstanceSerializer(BaseModelSerializer):
    class Meta:
        model = BusinessUser
        fields = ('id', 'phone', 'business_name', 'head_picture',
                  'food_court_id')


class UserDetailSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=20)
    business_name = serializers.CharField(max_length=100)
    food_court_id = serializers.IntegerField()
    last_login = serializers.DateTimeField()

    head_picture = serializers.ImageField()
    food_court_name = serializers.CharField(max_length=200, required=False)
    city = serializers.CharField(max_length=100, required=False)
    district = serializers.CharField(max_length=100, required=False)
    mall = serializers.CharField(max_length=200, required=False)

    @property
    def data(self):
        _data = super(UserDetailSerializer, self).data
        if _data.get('user_id', None):
            _data['last_login'] = timezoneStringTostring(_data['last_login'])
            base_dir = _data['head_picture'].split('static', 1)[1]
            if base_dir.startswith(os.path.sep):
                base_dir = base_dir[1:]
            _data['head_picture_url'] = os.path.join(settings.WEB_URL_FIX,
                                                     'static',
                                                     base_dir)
        return _data


class UserListSerializer(BaseListSerializer):
    child = UserDetailSerializer()