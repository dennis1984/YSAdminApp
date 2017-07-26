# -*- coding:utf8 -*-
from rest_framework import serializers
from horizon.serializers import (BaseListSerializer,
                                 BaseSerializer,
                                 BaseModelSerializer)

from Consumer_App.cs_comment.models import Comment
from Consumer_App.cs_users.models import ConsumerUser
import re
import copy


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = ConsumerUser
        fields = '__all__'

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        return super(UserSerializer, self).update(instance, validated_data)


class UserDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    phone = serializers.CharField(max_length=20, allow_blank=True,
                                  allow_null=True)
    nickname = serializers.CharField(max_length=100, required=False,
                                     allow_null=True, allow_blank=True)
    out_open_id = serializers.CharField(max_length=64, allow_null=True)
    balance = serializers.CharField(max_length=16)
    last_login = serializers.DateTimeField(allow_null=True)
    date_joined = serializers.DateTimeField()

    gender = serializers.IntegerField(default=0)
    channel = serializers.CharField(default='YS')
    province = serializers.CharField(max_length=16, allow_null=True,
                                     allow_blank=True)
    city = serializers.CharField(max_length=32, allow_blank=True,
                                 allow_null=True)
    is_active = serializers.BooleanField()
    head_picture_url = serializers.CharField(allow_null=True, allow_blank=True)


class UserListSerializer(BaseListSerializer):
    child = UserDetailSerializer()


class CommentDetailSerializer(BaseSerializer):
    user_id = serializers.IntegerField()
    orders_id = serializers.CharField(max_length=32)
    business_id = serializers.IntegerField()
    business_name = serializers.CharField(max_length=100)
    business_comment = serializers.ListField()
    dishes_comment = serializers.ListField()

    messaged = serializers.CharField(max_length=2048,
                                     allow_null=True, allow_blank=True)
    created = serializers.DateTimeField()


class CommentListSerializer(BaseListSerializer):
    child = CommentDetailSerializer()



