# -*- coding:utf8 -*-
from rest_framework import serializers
from horizon.serializers import BaseListSerializer
from django.conf import settings
from horizon.models import model_to_dict
from horizon import main
import urllib
import os
import json
import re
import copy


class UserDetailSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    phone = serializers.CharField(max_length=20, allow_blank=True,
                                  allow_null=True)
    nickname = serializers.CharField(max_length=100, required=False)
    out_open_id = serializers.CharField(max_length=64)
    balance = serializers.CharField(max_length=16)
    last_login = serializers.DateTimeField()

    gender = serializers.IntegerField(default=0)
    channel = serializers.CharField(default='YS')
    province = serializers.CharField(max_length=16)
    city = serializers.CharField(max_length=32)


class UserListSerializer(BaseListSerializer):
    child = UserDetailSerializer()



