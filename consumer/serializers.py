# -*- coding:utf8 -*-
from rest_framework import serializers
from horizon.serializers import (BaseListSerializer,
                                 BaseSerializer,
                                 BaseModelSerializer)

from Consumer_App.cs_comment.models import Comment
from Consumer_App.cs_users.models import ConsumerUser
from Consumer_App.cs_comment.models import ReplyComment
import re
import copy


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = ConsumerUser
        fields = ('id', 'phone', 'nickname', 'out_open_id', 'last_login',
                  'date_joined', 'gender', 'channel', 'province', 'city',
                  'is_active', 'head_picture')

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


class RechargeOrdersSerializer(BaseSerializer):
    orders_id = serializers.CharField(max_length=32)
    user_id = serializers.IntegerField()
    phone = serializers.CharField(allow_null=True, allow_blank=True)
    payable = serializers.CharField()
    recharge_type = serializers.CharField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    payment_status = serializers.IntegerField()


class RechargeOrdersListSerializer(BaseListSerializer):
    child = RechargeOrdersSerializer()


class ConsumerOrdersSerializer(BaseSerializer):
    pay_orders_id = serializers.CharField()
    consume_orders_id = serializers.CharField()
    user_id = serializers.IntegerField()
    phone = serializers.CharField(allow_null=True, allow_blank=True)
    payable = serializers.CharField()
    business_name = serializers.CharField()
    payment_status = serializers.IntegerField()
    orders_type = serializers.IntegerField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    is_commented = serializers.IntegerField()
    comment_messaged = serializers.CharField(allow_blank=True, allow_null=True)
    comment_id = serializers.IntegerField(required=False)
    reply_messaged = serializers.CharField(allow_blank=True, allow_null=True)


class ConsumeOrdersListSerializer(BaseListSerializer):
    child = ConsumerOrdersSerializer()


class ReplyCommentSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            if request:
                data['user_id'] = request.user.id
            super(ReplyCommentSerializer, self).__init__(data=data, **kwargs)
        else:
            super(ReplyCommentSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = ReplyComment
        fields = '__all__'

    def update(self, instance, validated_data):
        return super(ReplyCommentSerializer, self).update(instance, validated_data)

    def save(self, **kwargs):
        return super(ReplyCommentSerializer, self).save(**kwargs)


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


class WalletDetailSerializer(BaseSerializer):
    user_id = serializers.IntegerField()
    balance = serializers.CharField()
    phone = serializers.CharField(allow_blank=True, allow_null=True)


class WalletListSerializer(BaseListSerializer):
    child = WalletDetailSerializer()
