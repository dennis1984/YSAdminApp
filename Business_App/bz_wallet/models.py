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
from Business_App.bz_users.models import BusinessUser

from horizon.models import model_to_dict, BaseManager


WITHDRAW_RECORD_STATUS = {
    'unpaid': 0,
    'waiting_pay': 201,
    'paid': 206,
    'expired': 400,
    'failed': 500,
}

WITHDRAW_RECORD_STATUS_STEP = {
    0: (201, 500),
    201: (206,),
}


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
    def get_object(cls, **kwargs):
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
    def filter_objects(cls, **kwargs):
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e
