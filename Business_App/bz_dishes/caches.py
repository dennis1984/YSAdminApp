# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from django.conf import settings
from horizon import redis
from django.utils.timezone import now

from Business_App.bz_dishes.models import Dishes


# 过期时间（单位：秒）
EXPIRES_10_HOURS = 10 * 60 * 60


class DishesCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['business'])
        self.handle = redis.Redis(connection_pool=pool)

    def set_dishes_detail_list(self, user_id, dishes_list):
        key = self.get_dishes_detail_list_key(user_id)
        self.handle.delete(key)
        self.handle.rpush(key, *dishes_list)
        self.handle.expire(key, EXPIRES_10_HOURS)

    def get_dishes_detail_list(self, user_id, **kwargs):
        key = self.get_dishes_detail_list_key(user_id)
        dishes_list = self.handle.lrange(key)
        if not dishes_list:
            kwargs['user_id'] = user_id
            _dishes_list = Dishes.filter_dishes_detail_list(**kwargs)
            self.set_dishes_detail_list(user_id, _dishes_list)
            return _dishes_list
        return dishes_list

    def get_dishes_detail_list_key(self, user_id):
        return 'dishes_detail_list_key:%s' % user_id

    def delete_dishes_detail_list(self, user_id):
        key = self.get_dishes_detail_list_key(user_id)
        self.handle.delete(key)

