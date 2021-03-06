# -*- coding:utf8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from Business_App.bz_dishes.models import (City,
                                           Dishes,
                                           DISHES_SIZE_DICT,
                                           DISHES_SIZE_CN_MATCH,
                                           FoodCourt,
                                           DishesClassify)
from Business_App.bz_users.models import (BusinessUser,
                                          AdvertPicture)
from Business_App.bz_wallet.models import (WithdrawRecord,
                                           WalletAction,
                                           BankCard,
                                           WITHDRAW_RECORD_STATUS,
                                           WITHDRAW_RECORD_STATUS_STEP)
from Business_App.bz_setup.models import AppVersion

from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)
from horizon.decorators import has_permission_to_update
from horizon.models import model_to_dict
from horizon import main
from business.caches import BusinessUserCache, ConsumerUserCache


from django.conf import settings
import urllib
import os
import json
import re
import copy
from decimal import Decimal


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

    def save(self, **kwargs):
        instance = super(DishesSerializer, self).save(**kwargs)
        # 删除缓存
        self.delete_from_cache(instance)
        return instance

    def update_dishes_recommend_status(self, instance, validated_data):
        kwargs = {'is_recommend': validated_data['is_recommend']}
        return super(DishesSerializer, self).update(instance, kwargs)

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        price = validated_data.get('price', instance.price)
        discount = validated_data.get('discount', instance.discount)
        if Decimal(price) < Decimal(discount):
            raise Exception('[discount] can not greater than [price]')

        # 删除缓存
        self.delete_from_cache(instance)
        return super(DishesSerializer, self).update(instance, validated_data)

    def delete(self, instance):
        # 删除缓存
        self.delete_from_cache(instance)
        validated_data = {'status': 2,
                          'title': '%s-%s' % (
                              instance.title,
                              main.make_random_char_and_number_of_string(5))
                          }
        return super(DishesSerializer, self).update(instance, validated_data)

    def delete_from_cache(self, instance):
        # 删除缓存
        BusinessUserCache().delete_dishes_list_by_user_id(instance.user_id)
        ConsumerUserCache().delete_hot_sale_list(instance.food_court_id, instance.mark)


class DishesDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_null=True, allow_blank=True)
    description = serializers.CharField(allow_null=True, allow_blank=True)
    size = serializers.IntegerField()
    size_detail = serializers.CharField(allow_null=True, allow_blank=True)
    price = serializers.CharField()
    image = serializers.ImageField()
    image_detail = serializers.ImageField()
    user_id = serializers.IntegerField()
    food_court_id = serializers.IntegerField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    status = serializers.IntegerField()
    is_recommend = serializers.BooleanField()

    mark = serializers.IntegerField()
    discount = serializers.CharField()
    discount_time_slot_start = serializers.CharField(allow_null=True, allow_blank=True)
    discount_time_slot_end = serializers.CharField(allow_null=True, allow_blank=True)

    tag = serializers.CharField(allow_null=True, allow_blank=True)
    sort_orders = serializers.IntegerField(allow_null=True)
    classify = serializers.IntegerField()
    classify_name = serializers.CharField(allow_null=True, allow_blank=True)


class DishesListSerializer(BaseListSerializer):
    child = DishesDetailSerializer()


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = BusinessUser
        fields = ('id', 'phone', 'business_name', 'food_court_id','business_summary',
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

    business_summary = serializers.CharField(allow_blank=True, allow_null=True)
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
                instance = super(WithdrawRecordInstanceSerializer, self).update(instance, validated_data)
                # 解除冻结的金额
                wallet_instance = WalletAction().unblock_blocked_money(request, instance)
                if isinstance(wallet_instance, Exception):
                    raise wallet_instance
                return instance
        elif instance.status == WITHDRAW_RECORD_STATUS['waiting_pay']:
            if status == WITHDRAW_RECORD_STATUS['paid']:
                instance = super(WithdrawRecordInstanceSerializer, self).update(instance, validated_data)
                # 添加事务管理（打款操作）
                # 扣除打款的金额及冻结的金额
                wallet_instance = WalletAction().withdrawals(request, instance)
                if isinstance(wallet_instance, Exception):
                    raise wallet_instance
                return instance
        else:
            return instance


class OrdersDetailSerializer(BaseSerializer):
    orders_id = serializers.CharField()
    pay_orders_id = serializers.CharField(allow_blank=True, allow_null=True)
    verify_orders_id = serializers.CharField(allow_blank=True, allow_null=True)
    business_name = serializers.CharField(allow_null=True, allow_blank=True)
    user_id = serializers.IntegerField()
    food_court_name = serializers.CharField()
    total_amount = serializers.CharField(allow_null=True, allow_blank=True)
    member_discount = serializers.CharField(allow_null=True, allow_blank=True)
    other_discount = serializers.CharField(allow_null=True, allow_blank=True)
    payable = serializers.CharField()
    payment_status = serializers.IntegerField()
    payment_mode = serializers.IntegerField()
    orders_type = serializers.IntegerField()
    created = serializers.DateTimeField()
    payment_time = serializers.DateTimeField(allow_null=True)


class OrdersListSerializer(BaseListSerializer):
    child = OrdersDetailSerializer()


class BankCardSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            super(BankCardSerializer, self).__init__(data=data, **kwargs)
        else:
            super(BankCardSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = BankCard
        fields = '__all__'

    def save(self, request, **kwargs):
        if not request.user.is_admin:
            return Exception('Permission denied.')
        return super(BankCardSerializer, self).save(**kwargs)

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        return super(BankCardSerializer, self).update(instance, validated_data)

    def delete(self, request, instance, **kwargs):
        if not request.user.is_admin:
            return Exception('Permission denied.')

        kwargs['status'] = 2
        kwargs['bank_card_number'] = '%s-%s' % (instance.bank_card_number,
                                                main.make_random_char_and_number_of_string(5))
        try:
            return super(BankCardSerializer, self).update(instance, kwargs)
        except Exception as e:
            return e


class BankCardListSerializer(BaseListSerializer):
    child = BankCardSerializer()


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

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        return super(AdvertPictureSerializer, self).update(instance, validated_data)

    def delete(self, instance):
        validated_data = {'status': 2,
                          'name': '%s-%s' % (instance.name,
                                             main.make_random_char_and_number_of_string(5))}
        return super(AdvertPictureSerializer, self).update(instance, validated_data)


class AdvertPictureDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    food_court_id = serializers.IntegerField()
    food_court_name = serializers.CharField()
    owner = serializers.IntegerField()
    name = serializers.CharField()
    ad_position_name = serializers.CharField()
    ad_link = serializers.CharField()
    image = serializers.ImageField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class AdvertPictureListSerializer(BaseListSerializer):
    child = AdvertPictureDetailSerializer()


class AppVersionSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            if 'app_file' in data:
                data['package_path'] = data.pop('app_file')
                app_file_names = data['package_path'].name.split('.')
                if len(app_file_names) == 1:
                    data['package_path'].name = '%s.apk' % app_file_names[0]
            super(AppVersionSerializer, self).__init__(data=data, **kwargs)
        else:
            super(AppVersionSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = AppVersion
        fields = '__all__'

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        if 'app_file' in validated_data:
            validated_data['package_path'] = validated_data.pop('app_file')
        return super(AppVersionSerializer, self).update(instance, validated_data)

    def delete(self, instance):
        validated_data = {'status': instance.id + 1}
        return super(AppVersionSerializer, self).update(instance, validated_data)


class AppVersionListSerializer(BaseListSerializer):
    child = AppVersionSerializer()


class DishesClassifySerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            data['user_id'] = data.pop('business_id')
            super(DishesClassifySerializer, self).__init__(data=data, **kwargs)
        else:
            super(DishesClassifySerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = DishesClassify
        fields = '__all__'

    def update(self, instance, validated_data):
        pop_keys = ['id', 'pk', 'dishes_classify_id']
        for p_key in pop_keys:
            if p_key in validated_data:
                validated_data.pop(p_key)
        return super(DishesClassifySerializer, self).update(instance, validated_data)

    def delete(self, instance):
        validated_data = {'status': instance.id + 1}
        return super(DishesClassifySerializer, self).update(instance, validated_data)


class DishesClassifyDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    user_id = serializers.IntegerField()
    user_phone = serializers.CharField()
    business_name = serializers.CharField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class DishesClassifyListSerializer(BaseListSerializer):
    child = DishesClassifyDetailSerializer()

