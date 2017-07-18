# -*- coding:utf8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from Business_App.bz_dishes.models import (City,
                                           Dishes,
                                           FoodCourt)

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



# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdminUser
#         fields = '__all__'
#         # fields = ('id', 'phone', 'business_name', 'head_picture',
#         #           'food_court_id')
#
#     @has_permission_to_update
#     def update_password(self, request, instance, validated_data):
#         password = validated_data.get('password', None)
#         if password is None:
#             raise ValueError('Password is cannot be empty.')
#         validated_data['password'] = make_password(password)
#         return super(UserSerializer, self).update(instance, validated_data)
#
#     @has_permission_to_update
#     def update_userinfo(self, request, instance, validated_data):
#         if 'password' in validated_data:
#             validated_data['password'] = make_password(validated_data['password'])
#         return super(UserSerializer, self).update(instance, validated_data)
#
#     def binding_phone_to_user(self, request, instance, validated_data):
#         _validated_data = {'phone': validated_data['username']}
#         return super(UserSerializer, self).update(instance, _validated_data)
#
#
# class UserInstanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdminUser
#         fields = ('id', 'phone', 'nickname', 'head_picture',)



class UserDetailSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    phone = serializers.CharField(max_length=20, allow_blank=True,
                                  allow_null=True)
    nickname = serializers.CharField(max_length=100, required=False)
    gender = serializers.IntegerField(default=0)
    birthday = serializers.DateField(required=False)
    region = serializers.CharField(required=False)
    channel = serializers.CharField(default='YS')
    province = serializers.CharField(max_length=16)
    city = serializers.CharField(max_length=32)
    last_login = serializers.DateTimeField()

    head_picture = serializers.ImageField()

    # food_court_name = serializers.CharField(max_length=200, required=False)
    # city = serializers.CharField(max_length=100, required=False)
    # district = serializers.CharField(max_length=100, required=False)
    # mall = serializers.CharField(max_length=200, required=False)

    @property
    def data(self):
        _data = super(UserDetailSerializer, self).data
        if _data.get('pk', None):
            _data['member_id'] = 'NO.%06d' % _data['pk']
            _data['last_login'] = timezoneStringTostring(_data['last_login'])
            head_picture = _data.pop('head_picture')
            if head_picture.startswith('http'):
                _data['head_picture_url'] = urllib.unquote(head_picture)
            else:
                _data['head_picture_url'] = os.path.join(settings.WEB_URL_FIX,
                                                         head_picture)
        return _data


class UserListSerializer(BaseListSerializer):
    child = UserDetailSerializer()


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


# class IdentifyingCodeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IdentifyingCode
#         fields = '__all__'

