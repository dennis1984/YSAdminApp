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
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e


class ReplyComment(models.Model):
    """
    管理员回复点评
    """
    comment_id = models.IntegerField(u'被回复点评的记录ID', unique=True, db_index=True)
    user_id = models.IntegerField('管理员用户ID')
    orders_id = models.CharField('订单ID', max_length=32)

    messaged = models.TextField('评价留言', null=True, blank=True)
    created = models.DateTimeField('创建时间', default=now)

    class Meta:
        db_table = 'ys_reply_comment'
        app_label = 'Consumer_App.cs_comment.models.ReplyComment'

    def __unicode__(self):
        return self.orders_id

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e
