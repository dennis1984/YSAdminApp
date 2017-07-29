# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.db import transaction
from decimal import Decimal

from horizon.models import model_to_dict
from horizon.models import get_perfect_filter_params

import json
import datetime


# WALLET_TRADE_DETAIL_TRADE_TYPE_DICT = {
#     'recharge': 1,
#     'consume': 2,
#     'withdrawals': 3,
# }
#
# WALLET_ACTION_METHOD = ('recharge', 'consume', 'withdrawals')


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
        app_label = 'Consumer_App.cs_wallet.models.Wallet'

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


class WalletTradeDetail(models.Model):
    """
    交易明细
    """
    orders_id = models.CharField('订单ID', db_index=True, unique=True, max_length=32)
    user_id = models.IntegerField('用户ID', db_index=True)

    amount_of_money = models.CharField('金额', max_length=16)

    # 交易状态：0:未完成 200:已完成 500:交易失败
    trade_status = models.IntegerField('订单支付状态', default=200)
    # 交易类型 0: 未指定 1: 充值 2：消费 3: 取现
    trade_type = models.IntegerField('订单类型', default=0)
    # 金额是否同步到了钱包 0: 未同步 1: 已同步
    is_sync = models.IntegerField('金额是否同步', default=1)

    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('最后修改时间', auto_now=True)
    extend = models.TextField('扩展信息', default='', blank=True)

    objects = WalletManager()

    class Meta:
        db_table = 'ys_wallet_trade_detail'
        ordering = ['-updated']
        app_label = 'Consumer_App.cs_wallet.models.WalletTradeDetail'

    def __unicode__(self):
        return str(self.user_id)

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def get_success_list(cls, **kwargs):
        kwargs['trade_status'] = 200
        try:
            return cls.objects.filter(**kwargs)
        except:
            return []
