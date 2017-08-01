# -*- coding:utf8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.timezone import now
from django.db import transaction

from horizon.main import minutes_15_plus
from horizon.models import model_to_dict
from horizon.models import get_perfect_filter_params

from Business_App.bz_users.models import BusinessUser

import json
from decimal import Decimal


def date_for_model():
    return now().date()


def ordersIdIntegerToString(orders_id):
    return "%06d" % orders_id


class OrdersIdGenerator(models.Model):
    date = models.DateField('日期', primary_key=True, default=date_for_model)
    orders_id = models.IntegerField('订单ID', default=1)
    created = models.DateTimeField('创建日期', default=now)
    updated = models.DateTimeField('最后更改日期', auto_now=True)

    class Meta:
        db_table = 'ys_orders_id_generator'
        app_label = 'Business_App.bz_orders.models.OrdersIdGenerator'

    def __unicode__(self):
        return str(self.date)

    @classmethod
    def get_orders_id(cls):
        date_day = date_for_model()
        orders_id = 0
        # 数据库加排它锁，保证订单号是唯一的
        with transaction.atomic(using='business'):   # 多数据库事务管理需显示声明操作的数据库
                                                     # （以后的版本可能会改进）
            try:
                _instance = cls.objects.select_for_update().get(pk=date_day)
            except cls.DoesNotExist:
                cls().save()
                orders_id = 1
            else:
                orders_id = _instance.orders_id + 1
                _instance.orders_id = orders_id
                _instance.save()
        orders_id_string = ordersIdIntegerToString(orders_id)
        return '%s%s' % (date_day.strftime('%Y%m%d'), orders_id_string)


class VerifyOrders(models.Model):
    """
    核销订单
    """
    orders_id = models.CharField('订单ID', db_index=True, unique=True, max_length=32)
    user_id = models.IntegerField('用户ID', db_index=True)

    business_name = models.CharField('商户名字', max_length=200)
    food_court_id = models.IntegerField('美食城ID')
    food_court_name = models.CharField('美食城名字', max_length=200)
    consumer_id = models.IntegerField('消费者ID')

    dishes_ids = models.TextField('订购列表', default='')

    total_amount = models.CharField('订单总计', max_length=16)
    member_discount = models.CharField('会员优惠', max_length=16, default='0')
    other_discount = models.CharField('其他优惠', max_length=16, default='0')
    payable = models.CharField('应付金额', max_length=16)

    # 0:未支付 200:已支付 201:待消费 206:已完成 400: 已过期 500:支付失败
    payment_status = models.IntegerField('订单支付状态', default=201)
    # 支付方式：0:未指定支付方式 1：钱包支付 2：微信支付 3：支付宝支付
    payment_mode = models.IntegerField('订单支付方式', default=0)
    # 订单类型 0: 未指定 101: 在线订单 102：堂食订单 103：外卖订单
    orders_type = models.IntegerField('订单类型', default=101)

    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('最后修改时间', auto_now=True)
    expires = models.DateTimeField('订单过期时间', default=minutes_15_plus)
    extend = models.TextField('扩展信息', default='', blank=True)

    # objects = OrdersManager()

    class Meta:
        db_table = 'ys_verify_orders'
        app_label = 'Business_App.bz_orders.models.VerifyOrders'

    def __unicode__(self):
        return self.orders_id

    @classmethod
    def get_object(cls, *args, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

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
            if key == 'payment_status':
                if kwargs[key] == ORDERS_PAYMENT_STATUS['unpaid']:
                    _kwargs['expires__gt'] = now()
                elif kwargs[key] == ORDERS_PAYMENT_STATUS['expired']:
                    _kwargs['payment_status'] = ORDERS_PAYMENT_STATUS['unpaid']
                    _kwargs['expires__lte'] = now()
        return _kwargs

    @classmethod
    def filter_orders_details(cls, **kwargs):
        orders_list = cls.filter_objects(**kwargs)
        if isinstance(orders_list, Exception):
            return orders_list

        # user_ids = list(set([item.user_id for item in orders_list]))
        # users = BusinessUser.filter_objects(id__in=user_ids)
        # users_dict = {user.id: user for user in users}

        details = []
        for item in orders_list:
            orders_dict = model_to_dict(item)
            if 'min_payable' in kwargs:
                if float(orders_dict['payable']) < float(kwargs['min_payable']):
                    continue
            if 'max_payable' in kwargs:
                if float(orders_dict['payable']) > float(kwargs['max_payable']):
                    continue
            # user = users_dict.get(item.user_id)
            # if user:
            #     orders_dict['business_name'] = user.business_name
            # else:
            #     orders_dict['business_name'] = ''
            details.append(orders_dict)
        return details


ORDERS_PAYMENT_STATUS = {
    'unpaid': 0,
    'paid': 200,
    'consuming': 201,
    'finished': 206,
    'expired': 400,
    'failed': 500,
}

ORDERS_ORDERS_TYPE = {
    'unknown': 0,
    'online': 101,
    'business': 102,
    'take_out': 103,
    'wallet_recharge': 201,
}


class OrdersManager(models.Manager):
    def get(self, *args, **kwargs):
        object_data = super(OrdersManager, self).get(*args, **kwargs)
        if now() >= object_data.expires and object_data.payment_status == 0:
            object_data.payment_status = 400
        return object_data

    def filter(self, *args, **kwargs):
        object_data = super(OrdersManager, self).filter(*args, **kwargs)
        for item in object_data:
            if now() >= item.expires and item.payment_status == 0:
                item.payment_status = 400
        return object_data


class Orders(models.Model):
    orders_id = models.CharField('订单ID', db_index=True, unique=True, max_length=30)
    user_id = models.IntegerField('用户ID', db_index=True)
    food_court_id = models.IntegerField('美食城ID')
    food_court_name = models.CharField('美食城名字', max_length=200)
    business_name = models.CharField('商户名字', max_length=100)

    dishes_ids = models.TextField('订购列表', default='')
    # 订购列表详情
    # [
    #  {'id': 1, ...},   # 菜品详情
    #  {'id': 2, ...}, ...
    # ]
    #
    total_amount = models.CharField('订单总计', max_length=16, default='0')
    member_discount = models.CharField('会员优惠', max_length=16, default='0')
    other_discount = models.CharField('其他优惠', max_length=16, default='0')
    payable = models.CharField('订单总计', max_length=16, default='0')

    # 0:未支付 200:已支付 400: 已过期 500:支付失败
    payment_status = models.IntegerField('订单支付状态', default=0)
    # 支付方式：0:未指定支付方式 1：现金支付 2：微信支付 3：支付宝支付
    payment_mode = models.IntegerField('订单支付方式', default=0)
    # 订单类型 0: 未指定 101: 在线订单 102：堂食订单 103：外卖订单
    orders_type = models.IntegerField('订单类型', default=102)

    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('最后修改时间', auto_now=True)
    expires = models.DateTimeField('订单过期时间', default=minutes_15_plus)
    extend = models.TextField('扩展信息', default='', blank=True)

    objects = OrdersManager()

    class Meta:
        db_table = 'ys_orders'
        ordering = ['-orders_id']
        app_label = 'Business_App.bz_orders.models.Orders'

    def __unicode__(self):
        return self.orders_id

    @property
    def is_expired(self):
        if now() >= self.expires:
            return True
        return False

    @classmethod
    def get_object(cls, *args, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

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
            if key == 'payment_status':
                if kwargs[key] == ORDERS_PAYMENT_STATUS['unpaid']:
                    _kwargs['expires__gt'] = now()
                elif kwargs[key] == ORDERS_PAYMENT_STATUS['expired']:
                    _kwargs['payment_status'] = ORDERS_PAYMENT_STATUS['unpaid']
                    _kwargs['expires__lte'] = now()
        return _kwargs

    @classmethod
    def filter_orders_details(cls, **kwargs):
        orders_list = cls.filter_objects(**kwargs)
        if isinstance(orders_list, Exception):
            return orders_list

        # user_ids = list(set([item.user_id for item in orders_list]))
        # users = BusinessUser.filter_objects(id__in=user_ids)
        # users_dict = {user.id: user for user in users}

        details = []
        for item in orders_list:
            orders_dict = model_to_dict(item)
            if 'min_payable' in kwargs:
                if float(orders_dict['payable']) < float(kwargs['min_payable']):
                    continue
            if 'max_payable' in kwargs:
                if float(orders_dict['payable']) > float(kwargs['max_payable']):
                    continue
            # user = users_dict.get(item.user_id)
            # if user:
            #     orders_dict['business_name'] = user.business_name
            # else:
            #     orders_dict['business_name'] = ''
            details.append(orders_dict)
        return details
