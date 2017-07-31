# -*- coding:utf8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from Business_App.bz_dishes.models import (City,
                                           Dishes,
                                           DISHES_SIZE_DICT,
                                           DISHES_SIZE_CN_MATCH,
                                           FoodCourt)
from Business_App.bz_users.models import (BusinessUser,
                                          AdvertPicture)
from Business_App.bz_wallet.models import (WithdrawRecord,
                                           WalletAction,
                                           WITHDRAW_RECORD_STATUS,
                                           WITHDRAW_RECORD_STATUS_STEP)

from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)
from horizon.decorators import has_permission_to_update
from horizon.models import model_to_dict
from horizon import main

from django.conf import settings
import urllib
import os
import json
import re
import copy


class CitySerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            _data = copy.deepcopy(data)
            if request:
                _data['user_id'] = request.user.id
            super(CitySerializer, self).__init__(data=_data, **kwargs)
        else:
            super(CitySerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = City
        fields = '__all__'

    def save(self, **kwargs):
        try:
            return super(CitySerializer, self).save(**kwargs)
        except Exception as e:
            return e

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        try:
            super(CitySerializer, self).update(instance, validated_data)
        except Exception as e:
            return e
        else:
            # 批量修改美食城的所属城市信息
            if validated_data:
                instances = FoodCourt.filter_objects(city_id=instance.pk)
                for ins in instances:
                    kwargs = {'city': instance.city,
                              'district': instance.district}
                    f_serializer = FoodCourtSerializer(ins)
                    f_serializer.update(ins, kwargs)
        return instance

    def delete(self, instance):
        validated_data = {'status': 2,
                          'district': '%s-%s' % (
                              instance.district,
                              main.make_random_char_and_number_of_string(5))}
        return super(CitySerializer, self).update(instance, validated_data)

    # def add_district(self, instance, district_name):
    #     try:
    #         district_list = json.loads(instance.district)
    #     except Exception as e:
    #         if not instance.district:
    #             district_list = []
    #         else:
    #             return e
    #     for item in district_list:
    #         if district_name == item['name']:
    #             return Exception('District %s does exist.' % district_name)
    #     district_dict = {
    #         'id': len(district_list) + 1,
    #         'name': district_name,
    #     }
    #     district_list.append(district_dict)
    #     validated_data = {'district': json.dumps(district_list)}
    #     return super(CitySerializer, self).update(instance, validated_data)
    #
    # def delete_district(self, instance, pk):
    #     try:
    #         district_list = json.loads(instance.district)
    #     except Exception as e:
    #         if not instance.district:
    #             district_list = []
    #         else:
    #             return e
    #     district_dict = {item['id']: item for item in district_list}
    #     if pk not in district_dict:
    #         return instance
    #     district_dict.pop(pk)
    #     district_list = sorted(district_dict.values(), key=lambda x: x['id'])
    #     validated_data = {'district': json.dumps(district_list)}
    #     return super(CitySerializer, self).update(instance, validated_data)
    #
    # def update_district(self, instance, pk, district_name):
    #     try:
    #         district_list = json.loads(instance.district)
    #     except Exception as e:
    #         if not instance.district:
    #             district_list = []
    #         else:
    #             return e
    #     district_dict = {item['id']: item for item in district_list}
    #     if pk not in district_dict:
    #         return Exception('District %s does not exist.' % district_name)
    #
    #     district_dict['id']['name'] = district_name
    #     district_list = sorted(district_dict.values(), key=lambda x: x['id'])
    #     validated_data = {'district': json.dumps(district_list)}
    #     return super(CitySerializer, self).update(instance, validated_data)


# class CityDetailSerializer(BaseSerializer):
#     city = serializers.CharField(max_length=40)
#     province = serializers.CharField(max_length=40, required=False,
#                                      allow_null=True, allow_blank=True)
#     district = serializers.ListField(required=False)
#
#     user_id = serializers.IntegerField()
#     status = serializers.IntegerField()
#     created = serializers.DateTimeField()
#     updated = serializers.DateTimeField()


class CityListSerializer(BaseListSerializer):
    child = CitySerializer()


class FoodCourtSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            super(FoodCourtSerializer, self).__init__(data=data, **kwargs)
        else:
            super(FoodCourtSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = FoodCourt
        fields = '__all__'

    def update(self, instance, validated_data):
        return super(FoodCourtSerializer, self).update(instance, validated_data)

    def delete(self, instance, validated_data):
        validated_data.update({'status': 2,
                               'name': '%s-%s' %
                                       (instance.name,
                                        main.make_random_char_and_number_of_string(5))
                               })
        return super(FoodCourtSerializer, self).update(instance, validated_data)


class FoodCourtListSerializer(BaseListSerializer):
    child = FoodCourtSerializer()


class UserWithFoodCourtSerializer(BaseSerializer):
    user_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=20)
    business_name = serializers.CharField(max_length=100)
    food_court_name = serializers.CharField(max_length=200, required=False)
    food_court_id = serializers.IntegerField()


class UserWithFoodCourtListSerializer(BaseListSerializer):
    child = UserWithFoodCourtSerializer()


class DishesSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            size = data.get('size', 10)
            if size != DISHES_SIZE_DICT['custom']:
                data['size_detail'] = DISHES_SIZE_CN_MATCH[size]

            # 处理管理后台上传图片图片名字没有后缀的问题
            if 'image' in data:
                image_names = data['image'].name.split('.')
                if len(image_names) == 1:
                    data['image'].name = '%s.png' % image_names[0]
            super(DishesSerializer, self).__init__(data=data, **kwargs)
        else:
            super(DishesSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Dishes
        fields = '__all__'

    def update_dishes_recommend_status(self, instance, validated_data):
        kwargs = {'is_recommend': validated_data['is_recommend']}
        try:
            return super(DishesSerializer, self).update(instance, kwargs)
        except Exception as e:
            return e

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        return super(DishesSerializer, self).update(instance, validated_data)

    def delete(self, instance):
        validated_data = {'status': 2,
                          'title': '%s-%s' % (
                              instance.title,
                              main.make_random_char_and_number_of_string(5))
                          }
        return super(DishesSerializer, self).update(instance, validated_data)


class DishesListSerializer(BaseListSerializer):
    child = DishesSerializer()


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = BusinessUser
        fields = ('id', 'phone', 'business_name', 'food_court_id',
                  'brand', 'manager', 'chinese_people_id', 'stalls_number',
                  'is_active', 'date_joined', 'last_login', 'head_picture',)

    def update(self, instance, validated_data):
        for key in ['pk', 'id', 'user_id']:
            if key in validated_data:
                validated_data.pop(key)
        return super(UserSerializer, self).update(instance, validated_data)

    def reset_password(self, instance, password):
        validated_data = {'password': make_password(password)}
        return super(UserSerializer, self).update(instance, validated_data)


class UserDetailSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=20)
    business_name = serializers.CharField(max_length=100)
    food_court_id = serializers.IntegerField()
    brand = serializers.CharField(allow_blank=True, allow_null=True)
    manager = serializers.CharField(max_length=20, allow_null=True, allow_blank=True)
    chinese_people_id = serializers.CharField(max_length=25, allow_blank=True,
                                              allow_null=True)
    stalls_number = serializers.CharField(max_length=20, allow_blank=True,
                                          allow_null=True)

    last_login = serializers.DateTimeField()
    date_joined = serializers.DateTimeField()
    is_active = serializers.BooleanField()

    head_picture = serializers.ImageField()
    food_court_name = serializers.CharField(max_length=200, required=False)
    city = serializers.CharField(max_length=100, required=False)
    district = serializers.CharField(max_length=100, required=False)
    mall = serializers.CharField(max_length=200, required=False)

    @property
    def data(self):
        _data = super(UserDetailSerializer, self).data
        if _data.get('user_id', None):
            _data['last_login'] = timezoneStringTostring(_data['last_login'])
            base_dir = _data['head_picture'].split('static', 1)[1]
            if base_dir.startswith(os.path.sep):
                base_dir = base_dir[1:]
            _data['head_picture_url'] = os.path.join(settings.WEB_URL_FIX,
                                                     'static',
                                                     base_dir)
            _data.pop('head_picture')
        return _data


class UserListSerializer(BaseListSerializer):
    child = UserDetailSerializer()


class WithdrawRecordSerializer(BaseSerializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    business_name = serializers.CharField()
    amount_of_money = serializers.CharField()
    service_charge = serializers.CharField()
    payment_of_money = serializers.CharField()
    account_id = serializers.IntegerField()
    bank_card_number = serializers.CharField(allow_null=True, allow_blank=True)
    bank_name = serializers.CharField(allow_null=True, allow_blank=True)
    account_name = serializers.CharField(allow_null=True, allow_blank=True)
    status = serializers.IntegerField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class WithdrawRecordListSerializer(BaseListSerializer):
    child = WithdrawRecordSerializer()


class WithdrawRecordInstanceSerializer(BaseModelSerializer):
    class Meta:
        model = WithdrawRecord
        fields = '__all__'

    def update_status(self, request, instance, validated_data):
        if 'status' not in validated_data:
            raise Exception('Data Error.')
        else:
            if len(validated_data) != 1:
                raise Exception('Data Error.')
        status = validated_data['status']
        if instance.status not in WITHDRAW_RECORD_STATUS_STEP.keys() or \
            status not in WITHDRAW_RECORD_STATUS_STEP[instance.status]:
            raise Exception('Can not perform this action.')

        if instance.status == WITHDRAW_RECORD_STATUS['unpaid']:
            if status == WITHDRAW_RECORD_STATUS['waiting_pay']:
                return super(WithdrawRecordInstanceSerializer, self).update(instance, validated_data)
            elif status == WITHDRAW_RECORD_STATUS['failed']:
                # 添加事务管理(审核未通过)
                super(WithdrawRecordInstanceSerializer, self).update(instance, validated_data)
                # 解除冻结的金额
                return None
        elif instance.status == WITHDRAW_RECORD_STATUS['waiting_pay']:
            if status == WITHDRAW_RECORD_STATUS['paid']:
                instance = super(WithdrawRecordInstanceSerializer, self).update(instance, validated_data)
                # 添加事务管理（打款操作）
                # 扣除打款的金额及冻结的金额
                wallet_instance = WalletAction().withdrawals(request, instance)
                if isinstance(wallet_instance, Exception):
                    return wallet_instance
                return instance
        else:
            return instance


class AdvertPictureSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            # 处理管理后台上传图片图片名字没有后缀的问题
            if 'image' in data:
                image_names = data['image'].name.split('.')
                if len(image_names) == 1:
                    data['image'].name = '%s.png' % image_names[0]
            super(AdvertPictureSerializer, self).__init__(data=data, **kwargs)
        else:
            super(AdvertPictureSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = AdvertPicture
        fields = '__all__'

    def delete(self, instance):
        validated_data = {'status': 2,
                          'name': '%s-%s' % (instance.name,
                                             main.make_random_char_and_number_of_string(5))}
        return super(AdvertPictureSerializer, self).update(instance, validated_data)

