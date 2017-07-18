# -*- coding:utf8 -*-
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password

from horizon.models import model_to_dict

from django.conf import settings
import datetime
import os


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


class BusinessUserManager(BaseUserManager):
    def create_user(self, username, password, business_name, food_court_id, **kwargs):
        """
        创建商户，
        参数包括：username （手机号）
                 password （长度必须不小于6位）
                 business_name 商户名称（字符串）
                 food_court_id  美食城ID（整数）
        """
        if not username:
            raise ValueError('username cannot be null')

        user = self.model(
            phone=username,
            business_name=business_name,
            food_court_id=food_court_id,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, business_name=None,  food_court_id=None, **kwargs):
        user = self.create_user(username=username,
                                password=password,
                                business_name='admin',
                                food_court_id=0, **kwargs)
        user.is_admin = True
        user.save(using=self._db)
        return user

USER_PICTURE_DIR = settings.PICTURE_DIRS['business']['head_picture']


class BusinessUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        null=True,
    )
    business_name = models.CharField(u'商户名称', max_length=100, default='')
    food_court_id = models.IntegerField(u'所属美食城', default=0)
    phone = models.CharField(u'手机号', max_length=20, unique=True, db_index=True)
    head_picture = models.ImageField(u'头像',
                                     upload_to=USER_PICTURE_DIR,
                                     default=os.path.join(USER_PICTURE_DIR, 'noImage.png'),)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=now)

    objects = BusinessUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['business_name']

    class Meta:
        db_table = 'ys_auth_user'
        unique_together = ('business_name', 'food_court_id')
        app_label = 'Business_App.bz_users.models.BusinessUser'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_user_detail(cls, request):
        """
        返回数据结构：
             {'id',             用户ID
             'phone',           手机号
             'business_name',   商户名称
             'food_court_id',   所属美食城ID
             'last_login',      最后登录时间
             'head_picture',    商户头像
             'city',            美食城所在城市
             'district',        美食城所在城市市区
             'food_court_name', 美食城名称
             'mall',            美食城所属购物中心
             }
        """
        try:
            business_user = BusinessUser.objects.get(pk=request.user.id)
        except Exception as e:
            return e
        if request.user.is_admin:
            food_court = {}
        else:
            try:
                food_court = FoodCourt.objects.get(pk=business_user.food_court_id)
            except Exception as e:
                return e

        return cls.join_user_and_food_court(business_user, food_court)

    @classmethod
    def filter_users_detail(cls, **kwargs):
        """
        获取用户列表
        """
        _kwargs = get_perfect_filter_params(**kwargs)
        if 'start_created' in kwargs:
            _kwargs['created__gte'] = kwargs['start_created']
        if 'end_created' in kwargs:
            _kwargs['created__lte'] = kwargs['end_created']
        try:
            _instances_list = cls.objects.filter(**_kwargs)
        except Exception as e:
            return e

        results = []
        for _instance in _instances_list:
            try:
                food_court = FoodCourt.objects.get(pk=_instance.food_court_id)
            except Exception as e:
                return e
            user_data = cls.join_user_and_food_court(_instance, food_court)
            results.append(user_data)
        return results

    @classmethod
    def join_user_and_food_court(cls, user_instance, food_court_instance):
        business_user = model_to_dict(user_instance)
        business_user['user_id'] = business_user['id']
        if food_court_instance:
            business_user.update(**model_to_dict(food_court_instance))
            business_user['food_court_name'] = business_user['name']
        if business_user['last_login'] is None:
            business_user['last_login'] = business_user['date_joined']
        return business_user


class FoodCourt(models.Model):
    """
    美食城数据表
    """
    name = models.CharField('美食城名字', max_length=200)
    city = models.CharField('所属城市', max_length=100, null=False)
    district = models.CharField('所属市区', max_length=100, null=False)
    mall = models.CharField('所属购物中心', max_length=200, default='')
    address = models.CharField('购物中心地址', max_length=256, null=True, blank=True)
    extend = models.TextField('扩展信息', default='', blank=True, null=True)

    class Meta:
        db_table = 'ys_food_court'
        unique_together = ('name', 'mall')
        app_label = 'Business_App.bz_dishes.models.FoodCourt'

    def __unicode__(self):
        return self.name

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
    def get_object_list(cls, **kwargs):
        _kwargs = cls.get_perfect_filter_params(**kwargs)
        try:
            return cls.objects.filter(**_kwargs)
        except Exception as e:
            return e


