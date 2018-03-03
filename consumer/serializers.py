# -*- coding:utf8 -*-
from rest_framework import serializers
from horizon.serializers import (BaseListSerializer,
                                 BaseSerializer,
                                 BaseModelSerializer)

from Consumer_App.cs_comment.models import Comment
from Consumer_App.cs_users.models import ConsumerUser
from Consumer_App.cs_comment.models import ReplyComment
from Consumer_App.cs_wallet.models import (WalletTradeDetail,
                                           WalletAction,
                                           Wallet,
                                           WalletRechargeGift)
from Consumer_App.cs_orders.models import (PayOrders,
                                           ConsumeOrders,
                                           ORDERS_PAYMENT_STATUS,
                                           ConsumeOrdersAction)
from Consumer_App.cs_setup.models import Feedback
from Business_App.bz_wallet.models import WalletAction as BZ_WalletAction
from Business_App.bz_orders.models import VerifyOrders

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
    payment_time = serializers.DateTimeField(allow_null=True)
    updated = serializers.DateTimeField()
    is_commented = serializers.IntegerField()
    comment_messaged = serializers.CharField(allow_blank=True, allow_null=True)
    comment_id = serializers.IntegerField(allow_null=True)
    reply_messaged = serializers.CharField(allow_blank=True, allow_null=True)

    business_id = serializers.IntegerField()
    stalls_number = serializers.CharField(allow_blank=True, allow_null=True)
    food_court_id = serializers.IntegerField()
    food_court_name = serializers.CharField()

    dishes_ids = serializers.ListField()
    total_amount = serializers.CharField()
    member_discount = serializers.CharField()
    online_discount = serializers.CharField()
    other_discount = serializers.CharField()
    coupons_discount = serializers.CharField()
    coupons_id = serializers.IntegerField(allow_null=True)

    # 支付方式：0:未指定支付方式 1：钱包支付 2：微信支付 3：支付宝支付
    payment_mode = serializers.IntegerField()
    # 所属主订单
    master_orders_id = serializers.CharField()
    # 核销码：如果已经核销，该字段不为空，如果没有核销，该字段为空
    confirm_code = serializers.CharField(allow_blank=True, allow_null=True)
    notes = serializers.CharField(allow_blank=True, allow_null=True)
    # 核销时段：例如：17:30~20:30
    consumer_time_slot = serializers.CharField(allow_blank=True, allow_null=True)
    expires = serializers.DateTimeField()
    extend = serializers.CharField(allow_blank=True, allow_null=True)


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
    user_id = serializers.CharField()
    balance = serializers.CharField()
    phone = serializers.CharField(allow_blank=True, allow_null=True)


class WalletListSerializer(BaseListSerializer):
    child = WalletDetailSerializer()


class WalletTradeDetailSerializer(BaseModelSerializer):
    class Meta:
        model = WalletTradeDetail
        fields = ('orders_id', 'user_id', 'amount_of_money', 'trade_type',
                  'created')


class WalletTradeDetailListSerializer(BaseListSerializer):
    child = WalletTradeDetailSerializer()


class WalletSerializer(BaseModelSerializer):
    class Meta:
        model = Wallet
        fields = ('user_id', 'balance', 'updated')


class PayOrdersSerializer(BaseModelSerializer):
    class Meta:
        model = PayOrders
        fields = '__all__'

    def go_to_recharge(self, **kwargs):
        #  #### 添加事务操作（发生错误时要回滚）  ####
        try:
            instance = self.save()
        except Exception as e:
            return e

        does_give_coupons = kwargs.get('does_give_coupons', False)
        wallet_instance = WalletAction().recharge(None, instance,
                                                  gateway='admin_pay',
                                                  does_give_coupons=does_give_coupons)
        if isinstance(wallet_instance, Exception):
            raise wallet_instance

        serializer = WalletSerializer(wallet_instance)
        return serializer.data


class FeedbackSerializer(BaseModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class FeedbackListSerializer(BaseListSerializer):
    child = FeedbackSerializer()


class WalletRechargeGiftSerializer(BaseModelSerializer):
    class Meta:
        model = WalletRechargeGift
        fields = '__all__'

    def update_status_to_used(self, instance):
        validated_data = {'status': 2}
        return super(WalletRechargeGiftSerializer, self).update(instance, validated_data)


class WalletRechargeGiftDetailSerializer(BaseSerializer):
    user_id = serializers.IntegerField()
    phone = serializers.CharField()
    verification_code = serializers.CharField()
    status = serializers.IntegerField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class WalletRechargeGiftListSerializer(BaseListSerializer):
    child = WalletRechargeGiftDetailSerializer()


class ConsumeOrdersSerializer(BaseModelSerializer):
    class Meta:
        model = ConsumeOrders
        fields = '__all__'

    def update_payment_status_to_cancel(self, instance):
        """
        取消用户的待核销订单
        """
        # 同步订单支付状态
        instance = ConsumeOrdersAction().update_payment_status_to_canceled(instance.orders_id)
        if isinstance(instance, Exception):
            raise instance

        # 将订单应付款返回到用户钱包中
        wallet_instance = WalletAction().orders_refund(None, instance, gateway='admin_pay')
        if isinstance(wallet_instance, Exception):
            raise wallet_instance
        return instance

    def update_payment_status_to_consumed(self, instance):
        """
        确认核销用户的待核销订单
        """
        # 同步订单支付状态
        instance = ConsumeOrdersAction().update_payment_status_to_consumed(instance.orders_id)
        if isinstance(instance, Exception):
            raise instance

        # 钱包余额更新 (订单收入)
        verify_orders = VerifyOrders.get_object(orders_id=instance.orders_id)
        result = BZ_WalletAction().income(None, verify_orders, gateway='admin_pay')
        if isinstance(result, Exception):
            raise result

        return instance


