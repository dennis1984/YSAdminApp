# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from django.conf import settings
from Business_App.bz_users.models import BusinessUser, FoodCourt
from horizon.models import (model_to_dict,
                            BaseManager,
                            get_perfect_filter_params)
from django.conf import settings

import os
import json

DISHES_SIZE_DICT = {
    'default': 10,
    'small': 11,
    'medium': 12,
    'large': 13,
    'custom': 20,
}
DISHES_SIZE_CN_MATCH = {
    10: u'标准',
    11: u'小份',
    12: u'中份',
    13: u'大份',
    20: u'自定义',
}
DISHES_MARK = {
    'default': 0,
    'new': 10,
    'preferential': 20,
    'flagship': 30,
    'new_business': 40,
    'night_discount': 50,
}
DISHES_MARK_DISCOUNT_VALUES = (10, 20, 30, 40, 50)
CAN_NOT_USE_COUPONS_WITH_MARK = [DISHES_MARK['new_business']]
DISHES_PICTURE_DIR = settings.PICTURE_DIRS['business']['dishes']


class Dishes(models.Model):
    """
    菜品信息表
    """
    title = models.CharField('菜品名称', null=False, max_length=40)
    subtitle = models.CharField('菜品副标题', max_length=100, default='')
    description = models.TextField('菜品描述', default='')
    # 默认：10，小份：11，中份：12，大份：13，自定义：20
    size = models.IntegerField('菜品规格', default=10)
    size_detail = models.CharField('菜品规格详情', max_length=30, null=True, blank=True)
    price = models.CharField('价格', max_length=16, null=False, blank=False)
    image = models.ImageField('菜品图片（封面）',
                              upload_to=DISHES_PICTURE_DIR,
                              default=os.path.join(DISHES_PICTURE_DIR, 'noImage.png'),)
    image_detail = models.ImageField('菜品图片（详情）',
                                     upload_to=DISHES_PICTURE_DIR,
                                     default=os.path.join(DISHES_PICTURE_DIR, 'noImage.png'), )
    user_id = models.IntegerField('创建者ID', null=False)
    food_court_id = models.IntegerField('商城ID', db_index=True)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('最后修改时间', auto_now=True)
    status = models.IntegerField('数据状态', default=1)   # 1 有效 2 已删除 3 其他（比如暂时不用）
    is_recommend = models.BooleanField('是否推荐该菜品', default=False)   # 0: 不推荐  1：推荐

    # 运营标记： 0：无标记  10：新品  20：特惠  30：招牌  40: 新商户专区  50: 晚市特惠
    mark = models.IntegerField('运营标记', default=0)
    # 优惠金额
    discount = models.CharField('优惠金额', max_length=16, default='0')
    # 优惠时间段-开始 (用来标记菜品在某个时段是否有优惠)，以24小时制数字为标准， 如：8:00（代表早晨8点）
    discount_time_slot_start = models.CharField('优惠时间段-开始', max_length=16, null=True)
    # 优惠时间段-结束 (用来标记菜品在某个时段是否有优惠)，以24小时制数字为标准， 如：19:30（代表晚上7点30分）
    discount_time_slot_end = models.CharField('优惠时间段-结束', max_length=16, null=True)

    # 菜品标记和排序顺序
    tag = models.CharField('标记', max_length=64, default='', null=True, blank=True)
    sort_orders = models.IntegerField('排序标记', default=None, null=True)
    # 菜品类别:  0: 默认
    classify = models.IntegerField('菜品类别', default=0)

    extend = models.TextField('扩展信息', default='', blank=True)

    objects = BaseManager()

    class Meta:
        db_table = 'ys_dishes'
        unique_together = ('user_id', 'title', 'size',
                           'size_detail', 'status')
        ordering = ['-updated']
        app_label = 'Business_App.bz_dishes.models.Dishes'

    def __unicode__(self):
        return self.title

    @property
    def perfect_data(self):
        detail = model_to_dict(self)
        detail['classify_name'] = u'默认'
        if self.classify:
            dishes_classify = DishesClassify.get_object(pk=self.classify)
            if not isinstance(dishes_classify, Exception):
                detail['classify_name'] = dishes_classify.name
        return detail

    @classmethod
    def get_detail(cls, *args, **kwargs):
        instance = cls.get_object(*args, **kwargs)
        if isinstance(instance, Exception):
            return instance
        return instance.perfect_data

    @classmethod
    def get_object(cls, *args, **kwargs):
        _kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(*args, **_kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, *args, **kwargs):
        _kwargs = get_perfect_filter_params(cls, **kwargs)
        if 'title' in _kwargs:
            _kwargs['title__contains'] = _kwargs.pop('title')
        try:
            return cls.objects.filter(*args, **_kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_details(cls, *args, **kwargs):
        instances = cls.filter_objects(*args, **kwargs)
        if isinstance(instances, Exception):
            return instances
        details = []
        for ins in instances:
            details.append(ins.perfect_data)
        return details

    @classmethod
    def get_discount_details(cls, **kwargs):
        kwargs.update(**{'status': 1,
                         'mark__in': [10, 20, 30]})
        query = ~Q(discount='0')
        instance = cls.get_object(query, **kwargs)

        if isinstance(instance, Exception):
            return instance
        return cls.get_perfect_dishes_detail(instance)

    @classmethod
    def filter_discount_details(cls, **kwargs):
        kwargs.update(**{'status': 1,
                         'mark__in': [10, 20, 30]})
        query = ~Q(discount='0')
        instances = cls.filter_objects(query, **kwargs)
        details = []
        for instance in instances:
            perfect_detail = cls.get_perfect_dishes_detail(instance)
            details.append(perfect_detail)
        return details

    @classmethod
    def get_hot_sale_object(cls, **kwargs):
        try:
            dishes = cls.objects.get(**kwargs)
            dishes_detail = cls.get_dishes_detail_dict_with_user_info(pk=dishes.pk)
            return dishes_detail
        except Exception as e:
            return e

    @classmethod
    def get_hot_sale_list(cls, request, **kwargs):
        filter_dict = {'food_court_id': kwargs['food_court_id'],
                       'is_recommend': 1}
        try:
            hot_objects = cls.objects.filter(**filter_dict)
            dishes_list = []
            for item in hot_objects:
                dishes = cls.get_dishes_detail_dict_with_user_info(pk=item.pk)
                dishes_list.append(dishes)

            return dishes_list
        except Exception as e:
            return e

    @classmethod
    def get_dishes_detail_dict_with_user_info(cls, **kwargs):
        instance = cls.get_object(**kwargs)
        if isinstance(instance, Exception):
            return instance

        return cls.get_perfect_dishes_detail(instance)

    @classmethod
    def get_perfect_dishes_detail(cls, dishes):
        """
        获取带商户信息及美食城信息的菜品详情
        """
        user = BusinessUser.get_object(pk=dishes.user_id)
        dishes_dict = model_to_dict(dishes)
        dishes_dict['business_name'] = getattr(user, 'business_name', '')
        dishes_dict['business_id'] = dishes_dict['user_id']

        base_dir = str(dishes_dict['image']).split('static', 1)[1]
        if base_dir.startswith(os.path.sep):
            base_dir = base_dir[1:]
        dishes_dict.pop('image')
        dishes_dict['image_url'] = os.path.join(settings.WEB_URL_FIX,
                                                'static',
                                                base_dir)
        # 获取美食城信息
        food_instance = FoodCourt.get_object(pk=user.food_court_id)
        dishes_dict['food_court_name'] = getattr(food_instance, 'name', '')
        dishes_dict['food_court_id'] = getattr(food_instance, 'id', None)
        return dishes_dict


class City(models.Model):
    """
    城市信息
    """
    city = models.CharField('城市名称', max_length=40, db_index=True)
    # 市区数据结构：
    # [{'id': 1, 'name': u'大兴区'}, ...
    # ]
    district = models.CharField('市区信息', max_length=40)

    user_id = models.IntegerField('创建者')
    # 城市信息状态：1：有效 2：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField(default=now)
    updated = models.DateTimeField(auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'ys_city'
        ordering = ['city', 'district']
        unique_together = ('city', 'district', 'status')
        app_label = 'Business_App.bz_dishes.models.City'

    def __unicode__(self):
        return self.city

    @classmethod
    def get_object(cls, **kwargs):
        _kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**_kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, fuzzy=True, **kwargs):
        _kwargs = get_perfect_filter_params(cls, **kwargs)
        if fuzzy:
            if 'city' in _kwargs:
                _kwargs['city__contains'] = _kwargs.pop('city')
        try:
            return cls.objects.filter(**_kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_details(cls, fuzzy=True, **kwargs):
        instances = cls.filter_objects(fuzzy, **kwargs)
        if isinstance(instances, Exception):
            return instances

        return [model_to_dict(ins) for ins in instances]


# class DishesExtend(models.Model):
#     """
#     菜品信息扩展
#     """
#     dishes_id = models.IntegerField('菜品ID', db_index=True, unique=True)
#     tag = models.CharField('标记', max_length=64, default='', null=True, blank=True)
#     sort_orders = models.IntegerField('排序标记', null=True)
#
#     created = models.DateTimeField('创建时间', default=now)
#     updated = models.DateTimeField('更新时间', auto_now=True)
#
#     class Meta:
#         db_table = 'ys_dishes_extend'
#         app_label = 'Business_App.bz_dishes.models.DishesExtend'


class DishesClassify(models.Model):
    """
    菜品分类信息表
    """
    name = models.CharField('类别名称', max_length=64, unique=True)
    description = models.CharField('类别描述', max_length=256, null=True, blank=True)
    user_id = models.IntegerField('用户ID')
    # 状态：1：有效 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'ys_dishes_classify'
        unique_together = ('user_id', 'name', 'status')
        ordering = ('name',)
        app_label = 'Business_App.bz_dishes.models.DishesClassify'

    @property
    def perfect_data(self):
        detail = model_to_dict(self)
        user = BusinessUser.get_object(id=self.user_id)
        if isinstance(user, Exception):
            return user
        detail['user_phone'] = user.phone
        detail['business_name'] = user.business_name
        detail['food_court_id'] = user.food_court_id
        return detail

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def get_detail(cls, **kwargs):
        instance = cls.get_object(**kwargs)
        if isinstance(instance, Exception):
            return instance
        return instance.perfect_data

    @classmethod
    def filter_objects(cls, **kwargs):
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_details(cls, **kwargs):
        instances = cls.filter_objects(**kwargs)
        if isinstance(instances, Exception):
            return instances
        details = []
        for ins in instances:
            detail = ins.perfect_data
            if isinstance(detail, Exception):
                continue
            details.append(detail)
        return details
