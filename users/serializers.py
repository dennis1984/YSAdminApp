# -*- coding:utf8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from users.models import AdminUser, IdentifyingCode
from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 timezoneStringTostring)
from django.conf import settings
from horizon.models import model_to_dict
from horizon import main
import urllib
import os
import json
import re
import copy


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = AdminUser
        fields = '__all__'

    def update_password(self, request, instance, validated_data):
        password = validated_data.get('password', None)
        if password is None:
            raise ValueError('Password is cannot be empty.')
        validated_data['password'] = make_password(password)
        return super(UserSerializer, self).update(instance, validated_data)

    def update_userinfo(self, request, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).update(instance, validated_data)

    def binding_phone_to_user(self, request, instance, validated_data):
        _validated_data = {'phone': validated_data['username']}
        return super(UserSerializer, self).update(instance, _validated_data)


class UserInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ('id', 'phone', 'nickname',)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class IdentifyingCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentifyingCode
        fields = '__all__'

