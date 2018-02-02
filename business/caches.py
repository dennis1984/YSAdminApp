# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from django.conf import settings
from horizon import redis
from django.utils.timezone import now

from users.models import AdminUser


# 过期时间（单位：秒）
EXPIRES_24_HOURS = 24 * 60 * 60
EXPIRES_10_HOURS = 10 * 60 * 60


class BusinessUserCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['business'])
        self.handle = redis.Redis(connection_pool=pool)

    def get_user_id_key(self, user_id):
        # return 'user_instance_id:%s' % user_id
        return 'dishes_list_key:%s' % request.user.id

    def delete_from_data(self, key):
        return self.handle.delete(key)

    def delete_dishes_list_by_user_id(self, user_id):
        key = self.get_user_id_key(user_id)
        return self.delete_from_data(key)


class ConsumerUserCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['consumer'])
        self.handle = redis.Redis(connection_pool=pool)

    def get_hot_sale_list_key(self, food_court_id=1, mark=10):
        return 'hot_sale_id_key:food_court_id:%s:mark:%s' % (food_court_id, mark)

    def delete_from_data(self, key):
        return self.handle.delete(key)

    def delete_hot_sale_list(self, food_court_id, mark):
        key = self.get_hot_sale_list_key(food_court_id, mark)
        return self.delete_from_data(key)
