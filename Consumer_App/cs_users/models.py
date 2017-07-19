# -*- coding:utf8 -*-
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.timezone import now
from django.conf import settings

from horizon.models import model_to_dict
from Consumer_App.cs_wallet.models import Wallet
import datetime
import re
import os


class ConsumerUserManager(BaseUserManager):
    def create_user(self, username, password, **kwargs):
        """
        创建消费者用户，
        参数包括：username （手机号）
                 password （长度必须不小于6位）
        """
        if not username:
            raise ValueError('Username cannot be null!')
        if len(password) < 6:
            raise ValueError('Password length must not less then 6!')

        user = self.model(phone=username)
        user.set_password(password)
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


class ConsumerUser(AbstractBaseUser):
    phone = models.CharField(u'手机号', max_length=20, unique=True, db_index=True, null=True)
    out_open_id = models.CharField(u'第三方唯一标识', max_length=64, unique=True,
                                   db_index=True, null=True)
    nickname = models.CharField(u'昵称', max_length=100, null=True, blank=True)

    # 性别，0：未设定，1：男，2：女
    gender = models.IntegerField(u'性别', default=0)
    birthday = models.DateField(u'生日', null=True)
    province = models.CharField(u'所在省份或直辖市', max_length=16, null=True, blank=True)
    city = models.CharField(u'所在城市', max_length=32, null=True, blank=True)
    head_picture = models.ImageField(u'头像', max_length=200,
                                     upload_to=HEAD_PICTURE_PATH,
                                     default=os.path.join(HEAD_PICTURE_PATH, 'noImage.png'))

    # 注册渠道：客户端：YS，微信第三方：WX，QQ第三方：QQ，淘宝：TB
    #          新浪微博：SINA_WB
    channel = models.CharField(u'注册渠道', max_length=20, default='YS')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'最后更新时间', auto_now=True)

    objects = ConsumerUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['channel']

    class Meta:
        db_table = 'ys_auth_user'
        app_label = 'Consumer_App.cs_users.models.ConsumerUser'

    @property
    def is_binding(self):
        re_com = re.compile(r'^1[0-9]{10}$')
        result = re_com.match(self.phone)
        if result is None:
            return False
        return True

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
        kwargs = cls.get_perfect_filter_params(**kwargs)
        try:
            return cls.objects.get(**kwargs)
        except cls.DoesNotExist as e:
            return Exception(e)

    @classmethod
    def filter_users_detail(cls, **kwargs):
        kwargs = cls.get_perfect_filter_params(**kwargs)
        try:
            users = cls.objects.filter(**kwargs)
        except Exception as e:
            return e
        return cls.join_user_and_wallet(users, wallets=None)

    @classmethod
    def join_user_and_wallet(cls, users, wallets=None):
        if not wallets:
            wallets = Wallet.filter_objects()

        users_detail = []
        wallets_dict = {item.user_id: item for item in wallets}
        for user in users:
            user_dict = model_to_dict(user)
            user_dict['balance'] = wallets_dict.get(user.id, '0')
            users_detail.append(user_dict)
        return users_detail

