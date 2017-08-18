# -*- coding:utf8 -*-

from django.db import models
from django.utils.timezone import now

from horizon.models import (model_to_dict,
                            BaseManager,
                            get_perfect_filter_params)
from horizon.main import minutes_15_plus
import datetime
import re
import os


COUPONS_CONFIG_TYPE = {
    'member': 10,       # 会员优惠
    'online': 20,       # 在线下单优惠
    'other': 100,       # 其它优惠
    'custom': 200,      # 自定义
}
COUPONS_CONFIG_TYPE_CN_MATCH = {
    10: u'会员优惠',
    20: u'在线下单优惠',
    100: u'其它优惠',
    200: u'自定义',
}


class CouponsConfig(models.Model):
    """
    优惠券配置
    """
    name = models.CharField(u'优惠券名称', max_length=64)

    # 优惠券类别：会员优惠：10， 在线下单优惠：20，其它优惠：100，自定义：200
    type = models.IntegerField(u'优惠券类别')
    type_detail = models.CharField(u'优惠券类别详情', max_length=64)
    service_ratio = models.IntegerField(u'平台商承担（优惠）比例')
    business_ratio = models.IntegerField(u'商户承担（优惠）比例')

    # 数据状态：1：正常 2：已删除
    status = models.IntegerField(u'数据状态', default=1)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'最后更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'ys_coupons_config'
        unique_together = ('type_detail', 'name')

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


class DishesDiscountConfig(models.Model):
    """
    菜品优惠配置
    """
    dishes_id = models.IntegerField(u'菜品ID', unique=True, db_index=True)
    business_id = models.IntegerField(u'商户ID')
    business_name = models.CharField(u'商品名称', max_length=128)
    food_court_id = models.IntegerField(u'美食城ID')
    food_court_name = models.CharField(u'美食城名称', max_length=200)

    service_ratio = models.IntegerField(u'平台商承担（优惠）比例')
    business_ratio = models.IntegerField(u'商户承担（优惠）比例')

    # 数据状态：1：正常 2：已删除
    status = models.IntegerField(u'数据状态', default=1)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'最后更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'ys_dishes_discount_config'

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


