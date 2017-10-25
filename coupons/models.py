# -*- coding:utf8 -*-

from django.db import models
from django.utils.timezone import now

from horizon.models import (model_to_dict,
                            BaseManager,
                            get_perfect_filter_params)
from horizon.main import minutes_15_plus
from horizon import main
from Business_App.bz_dishes.models import Dishes

import datetime
import re
import os
import copy
from decimal import Decimal


COUPONS_CONFIG_TYPE = {
    'cash': 1,           # 代金券
    'discount': 2,       # 折扣券
}

COUPONS_CONFIG_TYPE_CN_MATCH = {
    1: u'代金券',
    2: u'折扣券',
}

COUPONS_CONFIG_FUZZY_FIELDS = ('name',)


class BaseCouponsManager(models.Manager):
    def get(self, *args, **kwargs):
        if 'status' not in kwargs:
            kwargs['status'] = 1
        instance = super(BaseCouponsManager, self).get(*args, **kwargs)
        return instance

    def filter(self, *args, **kwargs):
        if 'status' not in kwargs:
            kwargs['status'] = 1
        instances = super(BaseCouponsManager, self).filter(*args, **kwargs)
        return instances


class CouponsConfig(models.Model):
    """
    优惠券配置
    """
    name = models.CharField(u'优惠券名称', max_length=64)

    # 优惠券类别：1：代金券， 2：折扣券
    type = models.IntegerField(u'优惠券类别')
    # 优惠券类别详情：0：未设置 10：首单优惠券 20：节日券 30：促销券 100：其他优惠券
    type_detail = models.IntegerField(u'优惠券类别详情', default=0)

    amount_of_money = models.CharField(u'优惠金额', max_length=16, null=True)
    discount_percent = models.IntegerField(u'折扣率', null=True)
    service_ratio = models.IntegerField(u'平台商承担（优惠）比例')
    business_ratio = models.IntegerField(u'商户承担（优惠）比例')
    start_amount = models.CharField(u'满足优惠条件的起始金额', max_length=16, default='0')

    total_count = models.IntegerField(u'优惠券总数量', null=True)
    send_count = models.IntegerField(u'优惠券发放数量', default=0)
    description = models.CharField(u'优惠券描述', max_length=256, default='',
                                   blank=True, null=True)

    expire_in = models.IntegerField(u'过期天数', default=7)
    # 数据状态：1：正常 400：已过期 其它值：已删除
    status = models.IntegerField(u'数据状态', default=1)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'最后更新时间', auto_now=True)

    note = models.TextField(u'优惠券备注', default='', null=True, blank=True)

    objects = BaseCouponsManager()

    class Meta:
        db_table = 'ys_coupons_config'
        unique_together = ('name', 'status')
        ordering = ['-updated']

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def get_active_object(cls, **kwargs):
        return cls.get_object(**kwargs)

    @classmethod
    def filter_objects(cls, fuzzy=False, **kwargs):
        start_amount = None
        if 'start_amount' in kwargs:
            start_amount = kwargs.pop('start_amount')

        kwargs = get_perfect_filter_params(cls, **kwargs)
        if fuzzy:
            for key in COUPONS_CONFIG_FUZZY_FIELDS:
                if key in kwargs:
                    kwargs['%s__contains' % key] = kwargs.pop(key)
        try:
            instances = cls.objects.filter(**kwargs)
        except Exception as e:
            return e

        if not start_amount:
            return instances
        filter_instances = []
        for ins in instances:
            if Decimal(ins.start_amount) >= Decimal(start_amount):
                filter_instances.append(ins)
        return filter_instances


DISHES_DISCOUNT_FUZZY_FIELDS = ('dishes_name', 'business_name')


class DishesDiscountConfig(models.Model):
    """
    菜品优惠配置
    """
    dishes_id = models.IntegerField(u'菜品ID', db_index=True)
    # dishes_name = models.CharField(u'菜品名称', max_length=40)
    # business_id = models.IntegerField(u'商户ID')
    # business_name = models.CharField(u'商品名称', max_length=128)
    # food_court_id = models.IntegerField(u'美食城ID')
    # food_court_name = models.CharField(u'美食城名称', max_length=200)

    service_ratio = models.IntegerField(u'平台商承担（优惠）比例')
    business_ratio = models.IntegerField(u'商户承担（优惠）比例')

    # expires = models.DateTimeField(u'优惠券失效日期', default=main.days_7_plus)
    # 数据状态：1：正常 其它值：已删除
    status = models.IntegerField(u'数据状态', default=1)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'最后更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'ys_dishes_discount_config'
        unique_together = ('dishes_id', 'status')
        index_together = (['dishes_id', 'status'])

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def get_discount_config_detail(cls, **kwargs):
        instance = cls.get_object(**kwargs)

        if 'dishes_id' in kwargs:
            kwargs['id'] = kwargs.pop('dishes_id')
        dishes_detail = Dishes.get_discount_details(**kwargs)
        if isinstance(dishes_detail, Exception):
            return dishes_detail

        if isinstance(instance, Exception):
            update_dict = {'service_ratio': None,
                           'business_ratio': None,
                           'created': None,
                           'updated': None,
                           'dishes_id': dishes_detail['id'],
                           'dishes_name': dishes_detail['title']}
            dishes_detail.update(update_dict)
        else:
            ins_dict = model_to_dict(instance)
            ins_dict.pop('id')
            ins_dict['dishes_name'] = dishes_detail['title']
            ins_dict['created'] = str(ins_dict['created'])
            ins_dict['updated'] = str(ins_dict['updated'])
            dishes_detail.update(ins_dict)
        return dishes_detail

    @classmethod
    def filter_objects(cls, fuzzy=False, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        if fuzzy:
            for key in DISHES_DISCOUNT_FUZZY_FIELDS:
                if key in kwargs:
                    kwargs['%s__contains' % key] = kwargs.pop(key)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_discount_config_details(cls, fuzzy=False, **kwargs):
        instances = cls.filter_objects()
        instances_dict = {instance.dishes_id: instance for instance in instances}

        dishes_details = Dishes.filter_discount_details(**kwargs)
        details = []
        for detail in dishes_details:
            detail_dict = copy.deepcopy(detail)
            if detail['id'] in instances_dict:
                ins = instances_dict[detail['id']]
                ins_dict = model_to_dict(ins)
                ins_dict.pop('id')
                ins_dict['dishes_name'] = detail_dict['title']
                ins_dict['created'] = str(ins_dict['created'])
                ins_dict['updated'] = str(ins_dict['updated'])
                detail_dict.update(ins_dict)
            else:
                update_dict = {'service_ratio': None,
                               'business_ratio': None,
                               'created': None,
                               'updated': None,
                               'dishes_id': detail_dict['id'],
                               'dishes_name': detail_dict['title']}
                detail_dict.update(update_dict)
            details.append(detail_dict)
        return details


class CouponsSendRecord(models.Model):
    """
    优惠券派发记录
    """
    coupons_id = models.IntegerField(u'优惠券ID', db_index=True)
    user_id = models.IntegerField(u'用户ID')
    phone = models.CharField(u'用户手机号', max_length=20, null=True, blank=True)
    count = models.IntegerField(u'发放数量', default=1)

    created = models.DateTimeField(u'创建时间', default=now)

    class Meta:
        db_table = 'ys_coupons_send_record'
        ordering = ['-created']

    def __unicode__(self):
        return '%s-%s' % (self.coupons_id, self.user_id)

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
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

    @classmethod
    def filter_perfect_objects(cls, **kwargs):
        instances = cls.filter_objects(**kwargs)
        if isinstance(instances, Exception):
            return instances
        details = []
        coupons_dict = {}
        for ins in instances:
            coupons = coupons_dict.get(ins.coupons_id)
            if not coupons:
                coupons = CouponsConfig.get_object(pk=ins.coupons_id)
                coupons_dict[ins.coupons_id] = coupons
            detail = model_to_dict(ins)
            update_dict = {'coupons_name': coupons.name,
                           'coupons_type': coupons.type,
                           }
            detail.update(update_dict)
            details.append(detail)
        return details


class CouponsUsedRecord(models.Model):
    """
    优惠券使用记录
    """
    coupons_id = models.IntegerField(u'优惠券ID', db_index=True)
    user_id = models.IntegerField(u'用户ID')
    phone = models.CharField(u'用户手机号', max_length=20, null=True, blank=True)
    count = models.IntegerField(u'使用数量', default=1)

    created = models.DateTimeField(u'创建时间', default=now)

    class Meta:
        db_table = 'ys_coupons_used_record'
        ordering = ['-created']

    def __unicode__(self):
        return '%s-%s' % (self.coupons_id, self.user_id)

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
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

    @classmethod
    def filter_perfect_objects(cls, **kwargs):
        instances = cls.filter_objects(**kwargs)
        if isinstance(instances, Exception):
            return instances
        details = []
        coupons_dict = {}
        for ins in instances:
            coupons = coupons_dict.get(ins.coupons_id)
            if not coupons:
                coupons = CouponsConfig.get_object(pk=ins.coupons_id)
                coupons_dict[ins.coupons_id] = coupons
            detail = model_to_dict(ins)
            update_dict = {'coupons_name': coupons.name,
                           'coupons_type': coupons.type,
                           }
            detail.update(update_dict)
            details.append(detail)
        return details
