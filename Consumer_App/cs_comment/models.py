# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now

from horizon.models import model_to_dict
import json
import datetime


class Comment(models.Model):
    """
    用户点评
    """
    user_id = models.IntegerField('用户ID')
    orders_id = models.CharField('订单ID', db_index=True, unique=True, max_length=32)
    business_id = models.IntegerField('商户ID')
    business_name = models.CharField('商户名称', max_length=100)
    business_comment = models.TextField('商户的点评内容')
    # 商户的点评内容的数据格式为：
    # [{'id': 1,
    #   'star': 3,
    #   'cn_name': u'服务质量'},...
    # ]

    dishes_comment = models.TextField('菜品的点评内容')
    # 菜品的点评内容的数据格式为：
    # [{'dishes_id':  1,
    #    'dishes_name': '菜品名称',
    #    'image_url': 'http://',
    #    'star': 3}, ....
    # ]

    messaged = models.TextField('评价留言', null=True, blank=True)
    created = models.DateTimeField('创建时间', default=now)

    class Meta:
        db_table = 'ys_comment'
        app_label = 'Consumer_App.cs_comment.models.Comment'

    def __unicode__(self):
        return self.orders_id

    @classmethod
    def get_perfect_filter_params(cls, **kwargs):
        opts = cls._meta
        fields = ['pk']
        for f in opts.concrete_fields:
            fields.append(f.name)

        _kwargs = {}
        for key in kwargs:
            if key in fields:
                _kwargs[key] = kwargs[key]
        return _kwargs

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = cls.get_perfect_filter_params(**kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_comment_details(cls, **kwargs):
        instances = cls.filter_objects(**kwargs)
        if isinstance(instances, Exception):
            return instances
        details = []
        for instance in instances:
            ins_dict = model_to_dict(instance)
            ins_dict['business_comment'] = json.loads(ins_dict['business_comment'])
            ins_dict['dishes_comment'] = json.loads(ins_dict['dishes_comment'])
            details.append(ins_dict)
        return details