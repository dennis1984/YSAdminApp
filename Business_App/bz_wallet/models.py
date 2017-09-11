# -*- coding:utf8 -*-
from __future__ import unicode_literals
from rest_framework.request import Request
from django.http.request import HttpRequest

from django.db import models
from django.utils.timezone import now
from django.db import transaction
from decimal import Decimal

from horizon.main import days_7_plus
from horizon.models import get_perfect_filter_params
from horizon.models import model_to_dict, BaseManager

from Business_App.bz_users.models import BusinessUser
from Business_App.bz_orders.models import ORDERS_ORDERS_TYPE
from Consumer_App.cs_orders.models import SerialNumberGenerator

from horizon.models import BaseManager

import datetime

WITHDRAW_RECORD_STATUS = {
    'unpaid': 0,
    'waiting_pay': 201,
    'paid': 206,
    'expired': 400,
    'failed': 500,
}

WALLET_BLOCK_BALANCE = '0.00'
WALLET_SERVICE_RATE = '0.000'

WITHDRAW_RECORD_STATUS_STEP = {
    0: (201, 500),
    201: (206,),
}
WALLET_TRADE_DETAIL_TRADE_TYPE_DICT = {
    'recharge': 1,
    'income': 2,
    'withdraw': 3,
}
WALLET_ACTION_METHOD = ('recharge', 'income', 'withdraw')


class WalletManager(models.Manager):
    def get(self, *args, **kwargs):
        kwargs['trade_status'] = 200
        return super(WalletManager, self).get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        kwargs['trade_status'] = 200
        return super(WalletManager, self).filter(*args, **kwargs)


class WithdrawRecord(models.Model):
    """
    提现记录
    """
    user_id = models.IntegerField('用户ID', db_index=True)

    amount_of_money = models.CharField('申请提现金额', max_length=16)
    service_charge = models.CharField('手续费', max_length=16)
    payment_of_money = models.CharField('实际提现金额', max_length=16)
    account_id = models.IntegerField('提现到账账户')

    # 提现状态：0:审核中 201:等待打款 206:已打款 400:提现申请已过期 500:审核不通过
    status = models.IntegerField('提现状态', default=0)

    expires = models.DateTimeField('申请提现过期时间', default=days_7_plus)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新实际', auto_now=True)
    extend = models.TextField('扩展信息', default='', blank=True)

    class Meta:
        db_table = 'ys_wallet_withdraw_record'
        ordering = ['-created']
        app_label = 'Business_App.bz_orders.models.WithdrawRecord'

    def __unicode__(self):
        return str(self.user_id)

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def get_unpaid_object(cls, **kwargs):
        kwargs['status'] = WITHDRAW_RECORD_STATUS['unpaid']
        return cls.get_object(**kwargs)

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = cls.make_perfect_filter(**kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def make_perfect_filter(cls, **kwargs):
        _kwargs = get_perfect_filter_params(cls, **kwargs)
        for key in kwargs:
            if key == 'start_created':
                _kwargs['created__gte'] = kwargs[key]
            if key == 'end_created':
                _kwargs['created__lte'] = kwargs[key]
            if key == 'amount_of_money':
                _kwargs['amount_of_money__in'] = ['%.f' % kwargs[key],
                                                  '%.1f' % kwargs[key],
                                                  '%.2f' % kwargs[key]]
                _kwargs.pop('amount_of_money')
        return _kwargs

    @classmethod
    def filter_record_details(cls, **kwargs):
        records = cls.filter_objects(**kwargs)
        if isinstance(records, Exception):
            return records

        user_ids = list(set([item.user_id for item in records]))
        users = BusinessUser.filter_objects(id__in=user_ids)
        users_dict = {user.id: user for user in users}

        details = []
        for item in records:
            record_dict = model_to_dict(item)
            user = users_dict.get(item.user_id)
            if user:
                record_dict['business_name'] = user.business_name
            else:
                record_dict['business_name'] = ''

            bank_card = BankCard.get_object(pk=item.account_id)
            if bank_card.status == BANK_CARD_STATUS['unbinding']:
                if item.status == WITHDRAW_RECORD_STATUS['paid']:
                    record_dict['bank_card_number'] = bank_card.bank_card_number.split('-', 1)[0]
                    record_dict['bank_name'] = bank_card.bank_name
                    record_dict['account_name'] = bank_card.account_name
                else:
                    record_dict['bank_card_number'] = ''
            else:
                record_dict['bank_card_number'] = bank_card.bank_card_number
                record_dict['bank_name'] = bank_card.bank_name
                record_dict['account_name'] = bank_card.account_name

            details.append(record_dict)
        return details


BANK_CARD_STATUS = {
    'binding': 1,
    'unbinding': 2,
}


class BankCard(models.Model):
    """
    银行卡信息
    """
    user_id = models.IntegerField('用户ID', db_index=True)

    bank_card_number = models.CharField('银行卡', max_length=30)
    bank_name = models.CharField('银行名称', max_length=50)
    account_name = models.CharField('开户名', max_length=20)

    # 银行卡绑定状态 1：已绑定，2：已解除
    status = models.IntegerField('绑定状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新实际', auto_now=True)

    # objects = BaseManager()

    class Meta:
        db_table = 'ys_wallet_bank_card'
        ordering = ['-created']
        unique_together = ('bank_card_number', 'status')
        app_label = 'Business_App.bz_orders.models.BankCard'

    def __unicode__(self):
        return str(self.user_id)

    @classmethod
    def get_object(cls, _filter_all=True, **kwargs):
        if not _filter_all:
            kwargs['status'] = 1
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def does_exist_by_pk(cls, pk):
        ins = cls.get_object(pk=pk)
        if isinstance(ins, Exception):
            return False
        return True

    @classmethod
    def filter_objects(cls, _filter_all=True, **kwargs):
        if not _filter_all:
            kwargs['status'] = 1
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e


class Wallet(models.Model):
    """
    用户钱包
    """
    user_id = models.IntegerField('用户ID', db_index=True, unique=True)
    balance = models.CharField('余额', max_length=16, default='0')
    blocked_money = models.CharField('冻结金额', max_length=16, default=WALLET_BLOCK_BALANCE)
    password = models.CharField('支付密码', max_length=560, null=True)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('最后修改时间', auto_now=True)
    extend = models.TextField('扩展信息', default='', blank=True)

    class Meta:
        db_table = 'ys_wallet'
        app_label = 'Business_App.bz_orders.models.Wallet'

    def __unicode__(self):
        return str(self.user_id)

    @classmethod
    def unblock_blocked_money(cls, user_id, amount_of_money):
        """
        解除冻结金额 
        """
        instance = None
        # 数据库加排它锁，保证更改信息是列队操作的，防止数据混乱
        with transaction.atomic(using='business'):
            try:
                _instance = cls.objects.select_for_update().get(user_id=user_id)
            except cls.DoesNotExist:
                raise cls.DoesNotExist
            blocked_money = _instance.blocked_money
            _instance.blocked_money = str(Decimal(blocked_money) - Decimal(amount_of_money))
            _instance.save()
            instance = _instance
        return instance

    @classmethod
    def update_withdraw_balance(cls, user_id, amount_of_money):
        """
        提现
        """
        instance = None
        # 数据库加排它锁，保证更改信息是列队操作的，防止数据混乱
        with transaction.atomic(using='business'):
            try:
                _instance = cls.objects.select_for_update().get(user_id=user_id)
            except cls.DoesNotExist:
                raise cls.DoesNotExist

            if Decimal(_instance.blocked_money) - Decimal(WALLET_BLOCK_BALANCE) < Decimal(amount_of_money) or \
                    Decimal(_instance.balance) - Decimal(WALLET_BLOCK_BALANCE) < Decimal(amount_of_money):
                return Exception('Your balance is not enough.')
            _instance.blocked_money = str(Decimal(_instance.blocked_money) - Decimal(amount_of_money))
            _instance.balance = str(Decimal(_instance.balance) - Decimal(amount_of_money))
            _instance.save()
            instance = _instance
        return instance


class WalletTradeDetail(models.Model):
    """
    交易明细
    """
    serial_number = models.CharField('流水号', unique=True, max_length=32)
    orders_id = models.CharField('订单ID', db_index=True, unique=True, max_length=32)
    user_id = models.IntegerField('用户ID', db_index=True)

    amount_of_money = models.CharField('金额', max_length=16)

    # 交易状态：0:未完成 200:已完成 500:交易失败
    trade_status = models.IntegerField('订单支付状态', default=200)
    # 交易类型 0: 未指定 1: 充值 2：订单收入 3: 提现
    trade_type = models.IntegerField('订单类型', default=0)

    created = models.DateTimeField('创建时间', default=now)
    extend = models.TextField('扩展信息', default='', blank=True)

    objects = WalletManager()

    class Meta:
        db_table = 'ys_wallet_trade_detail'
        ordering = ['-created']
        app_label = 'Business_App.bz_orders.models.WalletTradeDetail'

    def __unicode__(self):
        return str(self.user_id)

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e


class WalletTradeAction(object):
    """
    钱包明细相关功能
    """
    def create(self, request, orders, method='income'):
        """
        创建交易明细（包含：充值（暂不支持）、订单收入和提现的交易明细）
        """
        serial_number = SerialNumberGenerator.get_serial_number()
        kwargs = {}
        if method == 'withdraw':
            kwargs = {'trade_type': WALLET_TRADE_DETAIL_TRADE_TYPE_DICT['withdraw'],   # 交易类型：提现
                      'orders_id': 'TX-%s-%s' % (orders.user_id,
                                                 datetime.datetime.strftime(orders.created, '%Y%m%d%H%M%S')),
                      'user_id': orders.user_id,
                      'amount_of_money': orders.amount_of_money,
                      }

        kwargs['serial_number'] = serial_number
        wallet_detail = WalletTradeDetail(**kwargs)
        try:
            wallet_detail.save()
        except Exception as e:
            return e
        return wallet_detail


class WalletAction(object):
    """
    钱包相关功能
    """
    def withdrawals(self, request, withdraw_record):
        """
        提现
        """
        if not request.user.is_admin:
            return Exception('Permission denied.')
        if not isinstance(withdraw_record, WithdrawRecord):
            return TypeError('Params [withdraw_record] data type error.')
        if withdraw_record.status != WITHDRAW_RECORD_STATUS['paid']:
            return TypeError('Cannot perform this action.')

        # 提现
        instance = Wallet.update_withdraw_balance(withdraw_record.user_id,
                                                  withdraw_record.amount_of_money)
        if isinstance(instance, Exception):
            return instance
        # 生成交易记录
        _trade = WalletTradeAction().create(request, withdraw_record, method='withdraw')
        if isinstance(_trade, Exception):
            return _trade
        return instance

    def unblock_blocked_money(self, request, withdraw_record):
        """
        解除冻结金额（适用于提现审核不通过时的情景）
        """
        if not request.user.is_admin:
            return Exception('Permission denied.')
        if not isinstance(withdraw_record, WithdrawRecord):
            return TypeError('Params [withdraw_record] data type error.')
        if withdraw_record.status != WITHDRAW_RECORD_STATUS['failed']:
            return TypeError('Cannot perform this action.')

        # 解除冻结金额
        instance = Wallet.unblock_blocked_money(withdraw_record.user_id,
                                                withdraw_record.amount_of_money)
        return instance
