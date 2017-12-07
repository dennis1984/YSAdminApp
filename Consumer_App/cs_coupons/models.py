# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.db import transaction
from horizon.main import minutes_15_plus, DatetimeEncode
from horizon.models import (model_to_dict,
                            get_perfect_filter_params)
from Consumer_App.cs_users.models import ConsumerUser
from coupons.models import CouponsConfig, CouponsSendRecord
from horizon.main import make_perfect_time_delta

from decimal import Decimal
import json
import datetime


class Coupons(models.Model):
    """
    我的优惠券
    """
    coupons_id = models.IntegerField(u'优惠券ID', db_index=True)
    user_id = models.IntegerField(u'用户ID')

    # 优惠券状态：1：未使用  2：已使用  400：已过期
    status = models.IntegerField(u'优惠券状态', default=1)

    expires = models.DateTimeField(u'优惠券过期时间', default=now)
    created = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'更新时间', auto_now=True)

    class Meta:
        db_table = 'ys_coupons'
        app_label = 'Consumer_App.cs_orders.models.Coupons'

    def __unicode__(self):
        return str(self.coupons_id)

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


class CouponsAction(object):
    """
    我的优惠券操作
    """
    def create_coupons(self, user_ids, coupons):
        """
        发放优惠券到用户手中
        返回：成功：发放数量,
             失败：Exception
        """
        if isinstance(user_ids, (str, unicode)):
            if user_ids.lower() != 'all':
                return Exception('The params data is incorrect.')
            user_ids = ConsumerUser.filter_objects()
        else:
            if not isinstance(user_ids, (list, tuple)):
                return Exception('The params data is incorrect.')
        if coupons.total_count:
            if (coupons.total_count - coupons.send_count) < len(user_ids):
                return Exception('The coupon total count is not enough.')

        send_count = 0
        for item in user_ids:
            if hasattr(item, 'pk'):
                user_id = item.pk
                phone = item.phone
            else:
                user_id = item
                user = ConsumerUser.get_object(pk=user_id)
                phone = user.phone
            initial_data = {'coupons_id': coupons.pk,
                            'user_id': user_id,
                            'expires': make_perfect_time_delta(days=coupons.expire_in,
                                                               hours=23,
                                                               minutes=59,
                                                               seconds=59)}
            instances = []
            if coupons.each_count:
                for i in range(coupons.each_count):
                    instance = Coupons(**initial_data)
                    instances.append(instance)
            else:
                instances = [Coupons(**initial_data)]
            for ins in instances:
                try:
                    ins.save()
                except Exception as e:
                    return e

            send_count += len(instances)
            send_record_data = {'coupons_id': coupons.pk,
                                'user_id': user_id,
                                'phone': phone,
                                'count': len(instances)}
            try:
                CouponsSendRecord(**send_record_data).save()
            except Exception as e:
                pass

        return send_count
