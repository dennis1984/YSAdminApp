# -*- coding:utf8 -*-
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from django.conf import settings
from oauth2_provider.models import AccessToken
from horizon.models import model_to_dict, get_perfect_filter_params
from horizon.main import minutes_15_plus
import datetime
import re
import os
import json


PERMISSION_LIST = {
    u'管理平台': (
        {'name': u'城市管理', 'url': '/city/'},
        {'name': u'商城查询', 'url': '/foodcourt/'},
        {'name': u'商户管理', 'url': '/tenants/'},
        {'name': u'菜单管理', 'url': '/business/'},
        {'name': u'补贴配置', 'url': '/discount/'},
        {'name': u'商户订单', 'url': '/businessorder/'},
        {'name': u'用户订单', 'url': '/order/'},
        {'name': u'用户管理', 'url': '/user/'},
        {'name': u'充值查询', 'url': '/recharge/'},
        {'name': u'用户钱包', 'url': '/wallet/'},
        {'name': u'打款操作', 'url': '/withdraw/operation/'},
        {'name': u'提现查询', 'url': '/withdraw/'},
        {'name': u'广告管理', 'url': '/banner/'},
        {'name': u'意见反馈', 'url': '/feedback/'},
        {'name': u'版本控制', 'url': '/version/'},
    ),
    u'优惠券': (
        {'name': u'优惠券管理', 'url': '/coupons/'},
        {'name': u'优惠券派发', 'url': '/coupons/sender/'},
        {'name': u'优惠券使用', 'url': '/coupons/used/'},
    ),
    u'数据统计': (
        {'name': u'销售统计', 'url': '/order/sale/'},
    ),
}


class AdminUserManager(BaseUserManager):
    def create_user(self, username, password, **kwargs):
        """
        创建管理后台用户，
        参数包括：username （手机号）
                 password （长度必须不小于6位）
        """
        if not username:
            raise ValueError('Username cannot be null!')
        if len(password) < 6:
            raise ValueError('Password length must not less then 6!')

        user = self.model(phone=username)
        user.set_password(password)
        for name, value in kwargs.items():
            setattr(user, name, value)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **kwargs):
        user = self.create_user(username=username,
                                password=password,
                                **kwargs)
        user.is_admin = True
        user.save(using=self._db)
        return user


HEAD_PICTURE_PATH = settings.PICTURE_DIRS['consumer']['head_picture']


class AdminUser(AbstractBaseUser):
    phone = models.CharField(u'手机号', max_length=20, unique=True, db_index=True, null=True)
    # out_open_id = models.CharField(u'第三方唯一标识', max_length=64, unique=True,
    #                                db_index=True, null=True)
    nickname = models.CharField(u'昵称', max_length=100, null=True, blank=True)

    # 性别，0：未设定，1：男，2：女
    # gender = models.IntegerField(u'性别', default=0)
    # birthday = models.DateField(u'生日', null=True)
    # province = models.CharField(u'所在省份或直辖市', max_length=16, null=True, blank=True)
    # city = models.CharField(u'所在城市', max_length=32, null=True, blank=True)
    # head_picture = models.ImageField(u'头像', max_length=200,
    #                                  upload_to=HEAD_PICTURE_PATH,
    #                                  default=os.path.join(HEAD_PICTURE_PATH, 'noImage.png'))

    # 注册渠道：客户端：YS，微信第三方：WX，QQ第三方：QQ，淘宝：TB
    #          新浪微博：SINA_WB
    # channel = models.CharField(u'注册渠道', max_length=20, default='YS')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    permission_list = models.TextField(u'权限列表', default='')
    date_joined = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'最后更新时间', auto_now=True)

    objects = AdminUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        db_table = 'ys_auth_user'
        # unique_together = ('nickname', 'food_court_id')

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(**kwargs)
        try:
            instance = cls.objects.get(**kwargs)
        except cls.DoesNotExist as e:
            return e

        if instance.permission_list:
            instance.permission_list = json.loads(instance.permission_list)
        else:
            instance.permission_list = {}
        return instance

    @classmethod
    def get_user_detail(cls, request):
        """
        return: ConsumerUser instance
        """
        try:
            return cls.objects.get(pk=request.user.id)
        except Exception as e:
            return e

    @property
    def to_dict(self):
        detail = model_to_dict(self)
        if detail['permission_list']:
            detail['permission_list'] = json.loads(detail['permission_list'])
        else:
            detail['permission_list'] = {}
        return detail

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(**kwargs)
        try:
            instances = cls.objects.filter(**kwargs)
        except Exception as e:
            return e

        for ins in instances:
            if ins.permission_list:
                ins.permission_list = json.loads(ins.permission_list)
            else:
                ins.permission_list = {}
        return instances


def make_token_expire(request):
    """
    置token过期
    """
    header = request.META
    token = header['HTTP_AUTHORIZATION'].split()[1]
    try:
        _instance = AccessToken.objects.get(token=token)
        _instance.expires = now()
        _instance.save()
    except:
        pass
    return True


class IdentifyingCode(models.Model):
    phone = models.CharField(u'手机号', max_length=20, db_index=True)
    identifying_code = models.CharField(u'手机验证码', max_length=6)
    expires = models.DateTimeField(u'过期时间', default=minutes_15_plus)

    class Meta:
        db_table = 'ys_identifying_code'
        ordering = ['-expires']

    def __unicode__(self):
        return self.phone

    @classmethod
    def get_object_by_phone(cls, phone):
        instances = cls.objects.filter(**{'phone': phone, 'expires__gt': now()})
        if instances:
            return instances[0]
        else:
            return None

