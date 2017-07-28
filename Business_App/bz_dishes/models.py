# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
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

    # 0：无标记  10：新品  20：特惠  30：招牌
    mark = models.IntegerField('运营标记', default=0)
    extend = models.TextField('扩展信息', default='', blank=True)

    objects = BaseManager()

    class Meta:
        db_table = 'ys_dishes'
        unique_together = ('user_id', 'title', 'size',
                           'size_detail', 'status')
        app_label = 'Business_App.bz_dishes.models.Dishes'

    def __unicode__(self):
        return self.title

    @classmethod
    def get_object(cls, **kwargs):
        _kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**_kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        _kwargs = get_perfect_filter_params(cls, **kwargs)
        if 'title' in _kwargs:
            _kwargs['title__contains'] = _kwargs.pop('title')
        try:
            return cls.objects.filter(**_kwargs)
        except Exception as e:
            return e

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
