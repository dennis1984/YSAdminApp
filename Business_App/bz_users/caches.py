# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from django.conf import settings
from horizon import redis
from django.utils.timezone import now

from Business_App.bz_users.models import BusinessUser

# 过期时间（单位：秒）
EXPIRES_10_HOURS = 10 * 60 * 60


class BusinessUserCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['business'])
        self.handle = redis.Redis(connection_pool=pool)

    def get_user_detail_id_key(self, user_id):
        return 'user_detail_id:%s' % user_id

    def set_user_to_cache(self, key, data, expires=EXPIRES_10_HOURS):
        self.handle.set(key, data)
        self.handle.expire(key, expires)

    def get_user_detail_by_id(self, user_id):
        key = self.get_user_detail_by_id(user_id)
        user_detail = self.handle.get(key)
        if not user_detail:
            user_detail = BusinessUser.get_object(**{'pk': user_id})
            if isinstance(user_detail, Exception):
                return user_detail
            self.set_user_to_cache(key, user_detail)
        return user_detail
