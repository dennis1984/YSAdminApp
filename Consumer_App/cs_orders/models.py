# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.db import transaction
from horizon.main import minutes_15_plus
from horizon.models import (model_to_dict,
                            get_perfect_filter_params)
from Consumer_App.cs_users.models import ConsumerUser

from decimal import Decimal
import json

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


class OrdersManager(models.Manager):
    def get(self, *args, **kwargs):
        object_data = super(OrdersManager, self).get(
            *args, **kwargs
        )
        if now() >= object_data.expires and object_data.payment_status == 0:
            object_data.payment_status = 400
        return object_data

    def filter(self, *args, **kwargs):
        object_data = super(OrdersManager, self).filter(
            *args, **kwargs
        )
        for item in object_data:
            if now() >= item.expires and item.payment_status == 0:
                item.payment_status = 400
        return object_data


class PayOrders(models.Model):
    """
    支付订单（主订单）
    """
    orders_id = models.CharField('订单ID', db_index=True, unique=True, max_length=32)
    user_id = models.IntegerField('用户ID', db_index=True)
    food_court_id = models.IntegerField('美食城ID')
    food_court_name = models.CharField('美食城名字', max_length=200)

    dishes_ids = models.TextField('订购列表', default='')
    # 订购列表详情
    # {business_id_1: [订购菜品信息],
    #  business_id_2: [订购菜品信息],
    # }
    #
    total_amount = models.CharField('订单总计', max_length=16)
    member_discount = models.CharField('会员优惠', max_length=16, default='0')
    other_discount = models.CharField('其他优惠', max_length=16, default='0')
    payable = models.CharField('应付金额', max_length=16)

    # 0:未支付 200:已支付 400: 已过期 500:支付失败
    payment_status = models.IntegerField('订单支付状态', default=0)
    # 支付方式：0:未指定支付方式 1：钱包 2：微信支付 3：支付宝支付 20：管理员支付
    payment_mode = models.IntegerField('订单支付方式', default=0)
    # 订单类型 0: 未指定 101: 在线订单 102：堂食订单 103：外卖订单
    #         201: 钱包充值订单  (预留：202：钱包消费订单 203: 钱包提现)
    orders_type = models.IntegerField('订单类型', default=0)

    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('最后修改时间', auto_now=True)
    expires = models.DateTimeField('订单过期时间', default=minutes_15_plus)
    extend = models.TextField('扩展信息', default='', blank=True)

    objects = OrdersManager()

    class Meta:
        db_table = 'ys_pay_orders'
        ordering = ['-orders_id']
        app_label = 'Consumer_App.cs_orders.models.PayOrders'

    def __unicode__(self):
        return self.orders_id

    @property
    def is_expired(self):
        if now() >= self.expires:
            return True
        return False

    @property
    def is_success(self):
        """
        订单是否完成
        :return: 
        """
        if self.payment_status == 200:
            return True
        return False

    @property
    def is_recharge_orders(self):
        """
        充值订单
        """
        if self.orders_type == ORDERS_ORDERS_TYPE['wallet_recharge']:
            return True
        return False

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def get_object_detail(cls, **kwargs):
        _object = cls.get_object(**kwargs)
        if isinstance(_object, Exception):
            return _object
        detail = model_to_dict(_object)
        detail['dishes_ids'] = json.loads(detail['dishes_ids'])
        detail['is_expired'] = _object.is_expired
        return detail

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_recharge_objects(cls, **kwargs):
        kwargs.update(**{'orders_type': ORDERS_ORDERS_TYPE['wallet_recharge'],
                         })
        kwargs = cls.mark_perfect_filter(**kwargs)
        return cls.filter_objects(**kwargs)

    @classmethod
    def mark_perfect_filter(cls, **kwargs):
        _kwargs = get_perfect_filter_params(cls, **kwargs)
        for key in kwargs:
            if key == 'start_created':
                _kwargs['created__gte'] = kwargs[key]
            if key == 'end_created':
                _kwargs['created__lte'] = kwargs[key]
            # if key == 'min_payable':
            #     _kwargs['payable__gte'] = float(kwargs[key])
            # if key == 'max_payable':
            #     _kwargs['payable__lte'] = float(kwargs[key])
        return _kwargs

    @classmethod
    def filter_orders_details(cls, _filter='ALL', **kwargs):
        # 充值订单
        if _filter.upper() == 'RECHARGE':
            orders_instances = cls.filter_recharge_objects(**kwargs)
        # 普通订单
        else:
            orders_instances = cls.filter_objects(**kwargs)
        if isinstance(orders_instances, Exception):
            return orders_instances

        user_ids = [item.user_id for item in orders_instances]
        users = ConsumerUser.filter_objects(**{'id__in': user_ids})
        users_dict = {user.id: user for user in users}

        orders_details = []
        for instance in orders_instances:
            orders_dict = model_to_dict(instance)
            if 'min_payable' in kwargs:
                if float(orders_dict['payable']) < float(kwargs['min_payable']):
                    continue
            if 'max_payable' in kwargs:
                if float(orders_dict['payable']) > float(kwargs['max_payable']):
                    continue

            user = users_dict.get(instance.user_id)
            if user:
                phone = user.phone
            else:
                phone = ''
            orders_dict['phone'] = phone
            if _filter.upper() == 'RECHARGE':
                if orders_dict['payment_mode'] == ORDERS_PAYMENT_MODE['admin']:
                    orders_dict['recharge_type'] = 2
                else:
                    orders_dict['recharge_type'] = 1
            orders_details.append(orders_dict)

        return orders_details
