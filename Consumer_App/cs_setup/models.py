# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from horizon.models import model_to_dict, get_perfect_filter_params

import json
import datetime

FEEDBACK_FUZZY_LIST = ('nickname', 'content')


class Feedback(models.Model):
    user_id = models.IntegerField('用户ID')
    phone = models.CharField('手机号', max_length=20, null=True, blank=True)
    nickname = models.CharField('菜品ID', max_length=100, null=True, blank=True)

    # 反馈内容
    content = models.CharField('反馈内容', max_length=365, default='')
    created = models.DateTimeField('创建时间', default=now)

    class Meta:
        db_table = 'ys_feedback'
        ordering = ['-created']
        app_label = 'Consumer_App.cs_setup.models.Feedback'

    def __unicode__(self):
        return str(self.user_id)

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
        for key in kwargs.keys():
            if key in FEEDBACK_FUZZY_LIST:
                kwargs['%s__contains' % key] = kwargs.pop(key)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e
