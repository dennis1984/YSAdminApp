# -*- coding:utf8 -*-
from __future__ import unicode_literals
from rest_framework.request import Request
from django.http.request import HttpRequest

from django.db import models
from django.utils.timezone import now
from django.db import transaction
from decimal import Decimal

from horizon.main import days_7_plus

WITHDRAW_RECORD_STATUS = {
    'unpaid': 0,
    'finished': 200,
    'expired': 400,
    'failed': 500,
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
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e