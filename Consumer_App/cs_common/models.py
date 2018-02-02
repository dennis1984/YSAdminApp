# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.db import transaction
from decimal import Decimal

from horizon.models import get_perfect_filter_params

import json
import datetime

ORDERS_ORDERS_TYPE = {
    'unknown': 0,
    'online': 101,
    'business': 102,
    'take_out': 103,
    'wallet_recharge': 201,
}

ORDERS_PAYMENT_MODE = {
    'unknown': 0,
    'wallet': 1,
    'wxpay': 2,
    'alipay': 3,
    'admin': 20,
}

WALLET_TRADE_DETAIL_TRADE_TYPE_DICT = {
    'recharge': 1,
    'consume': 2,
    'withdrawals': 3,
}

WALLET_ACTION_METHOD = ('recharge', 'consume', 'withdrawals')


class WalletManager(models.Manager):
    def get(self, *args, **kwargs):
        kwargs['trade_status'] = 200
        return super(WalletManager, self).get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        kwargs['trade_status'] = 200
        return super(WalletManager, self).filter(*args, **kwargs)


class Wallet(models.Model):
    """
    用户钱包
    """
    user_id = models.IntegerField('用户ID', db_index=True)
    balance = models.CharField('余额', max_length=16, default='0')
    password = models.CharField('支付密码', max_length=560, null=True)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('最后修改时间', auto_now=True)
    extend = models.TextField('扩展信息', default='', blank=True)

    class Meta:
        db_table = 'ys_wallet'
        app_label = 'Consumer_App.cs_common.models.Wallet'

    def __unicode__(self):
        return str(self.user_id)

    @classmethod
    def has_enough_balance(cls, request, amount_of_money):
        wallet = cls.get_object(**{'user_id': request.user.id})
        if isinstance(wallet, Exception):
            return False
        try:
            return Decimal(wallet.balance) >= Decimal(amount_of_money)
        except:
            return False

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e


class AliYunPhoneMessageInformation(models.Model):
    """
    阿里云短信服务配置
    """
    region = models.CharField('区域', max_length=32)
    access_id = models.CharField('ACCESS_ID_KEY', max_length=32)
    access_secret = models.CharField('ACCESS_ID_SECRET', max_length=64)

    created = models.DateTimeField(default=now)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ys_aliyun_phone_message_information'
        app_label = 'Consumer_App.cs_common.models.AliYunPhoneMessageInformation'

    def __unicode__(self):
        return self.access_id

    @classmethod
    def get_object(cls, *args, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

