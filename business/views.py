# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from business.serializers import (CitySerializer,
                                  CityListSerializer,
                                  FoodCourtSerializer,
                                  FoodCourtListSerializer,
                                  UserWithFoodCourtListSerializer,
                                  DishesListSerializer,
                                  DishesSerializer,
                                  UserSerializer,
                                  UserDetailSerializer,
                                  UserListSerializer,
                                  WithdrawRecordSerializer,
                                  WithdrawRecordListSerializer,
                                  WithdrawRecordInstanceSerializer,
                                  OrdersDetailSerializer,
                                  OrdersListSerializer,
                                  BankCardSerializer,
                                  BankCardListSerializer,
                                  AdvertPictureSerializer,
                                  AdvertPictureDetailSerializer,
                                  AdvertPictureListSerializer)
from business.permissions import IsAdminOrReadOnly
from business.forms import (CityInputForm,
                            CityUpdateForm,
                            CityDeleteForm,
                            CityDetailForm,
                            CityListForm,
                            DistrictDetailForm,
                            FoodCourtInputForm,
                            FoodCourtUpdateForm,
                            FoodCourtDeleteForm,
                            FoodCourtDetailForm,
                            FoodCourtListForm,
                            UserWithFoodCourtListForm,
                            UsersInputForm,
                            UserUpdateForm,
                            UserResetPasswordForm,
                            UserDetailForm,
                            UserListForm,
                            DishesInputForm,
                            DishesListForm,
                            DishesDetailForm,
                            DishesUpdateForm,
                            DishesDeleteForm,
                            WithdrawRecordListForm,
                            WithdrawRecordDetailForm,
                            WithdrawRecordActionForm,
                            OrdersListForm,
                            OrdersDetailForm,
                            BankCardAddForm,
                            BankCardDeleteForm,
                            BankCardListForm,
                            BankCardUpdateForm,
                            BankCardDetailForm,
                            AdvertPictureInputForm,
                            AdvertPictureUpdateForm,
                            AdvertPictureDeleteForm,
                            AdvertPictureListForm,
                            AdvertPictureDetailForm)

from Business_App.bz_dishes.models import (City,
                                           Dishes,
                                           FoodCourt)
from Business_App.bz_dishes.caches import DishesCache
from Business_App.bz_users.models import (BusinessUser,
                                          AdvertPicture)
from Business_App.bz_wallet.models import (WithdrawRecord,
                                           BankCard,
                                           WITHDRAW_RECORD_STATUS_STEP)
from Business_App.bz_orders.models import Orders, VerifyOrders
from Business_App.bz_users.caches import BusinessUserCache

import re


class CityAction(generics.GenericAPIView):
    """
    城市管理
    """
    permission_classes = (IsAdminOrReadOnly,)

    def make_perfect_data(self, params_dict):
        for key in params_dict:
            if isinstance(params_dict[key], (str, unicode)):
                param_list = params_dict[key].split()
                params_dict[key] = ''.join(param_list)

    def get_city_object(self, pk):
        return City.get_object(pk=pk)

    def post(self, request, *args, **kwargs):
        """
        创建城市
        """
        form = CityInputForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        self.make_perfect_data(cld)
        serializer = CitySerializer(data=cld, request=request)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        result = serializer.save()
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        更新城市数据
        """
        form = CityUpdateForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_city_object(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CitySerializer(instance)
        data = serializer.update(instance, cld)
        if isinstance(data, Exception):
            return Response({'Detail': data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def delete(self, request, *args, **kwargs):
        """
        删除数据
        """
        form = CityDeleteForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_city_object(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CitySerializer(instance)
        try:
            serializer.delete(instance)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status.HTTP_204_NO_CONTENT)


class CityDetail(generics.GenericAPIView):
    """
    城市详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_city_detail(self, city_id):
        return City.get_object(pk=city_id)

    def post(self, request, *args, **kwargs):
        form = CityDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_city_detail(cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CitySerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CityList(generics.GenericAPIView):
    """
    城市列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_city_list(self, request, cld):
        return City.filter_objects(**cld)

    def make_perfect_data(self, params_dict):
        for key in params_dict:
            if isinstance(params_dict[key], (str, unicode)):
                param_list = params_dict[key].split()
                params_dict[key] = ''.join(param_list)

    def post(self, request, *args, **kwargs):
        form = CityListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        self.make_perfect_data(cld)
        citys = self.get_city_list(request, cld)
        serializer = CityListSerializer(citys)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class CitySimpleList(generics.GenericAPIView):
    """
    城市列表（美食城创建使用）简版
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_city_list(self):
        city_list = City.filter_objects()
        if isinstance(city_list, Exception):
            return []
        city_set = set([city.city for city in city_list])
        return sorted(list(city_set))

    def post(self, request , *args, **kwargs):
        city_list = self.get_city_list()
        return Response(city_list, status=status.HTTP_200_OK)


class DistrictList(generics.GenericAPIView):
    """
    城市辖区列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_city_details(self, city_name):
        return City.filter_details(fuzzy=False, **{'city': city_name})

    def get_district_dict(self, city_name):
        details = self.get_city_details(city_name)
        if isinstance(details, Exception):
            return details

        city_list = []
        for item in details:
            record = {'city_id': item['id'],
                      'district': item['district']}
            city_list.append(record)
        return city_list

    def post(self, request, *args, **kwargs):
        form = DistrictDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_district_dict(cld['city'])
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(details, status=status.HTTP_200_OK)


class FoodCourtAction(generics.GenericAPIView):
    """
    美食城创建
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_city_object(self, city_id):
        return City.get_object(pk=city_id)

    def get_perfect_params(self, params_dict, city):
        params_dict['city'] = city.city
        params_dict['district'] = city.district

    def get_food_court_object(self, pk):
        return FoodCourt.get_object(pk=pk)

    def post(self, request, *args, **kwargs):
        """
        创建美食城
        """
        form = FoodCourtInputForm(data=request.data, files=request.FILES)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        city_data = self.get_city_object(cld['city_id'])
        if isinstance(city_data, Exception):
            return Response({'Detail': city_data.args}, status=status.HTTP_400_BAD_REQUEST)

        self.get_perfect_params(cld, city_data)
        serializer = FoodCourtSerializer(data=cld)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        修改美食城信息
        """
        form = FoodCourtUpdateForm(data=request.data, files=request.FILES)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        if 'city_id' in cld:
            city_data = self.get_city_object(cld['city_id'])
            if isinstance(city_data, Exception):
                return Response({'Detail': city_data.args}, status=status.HTTP_400_BAD_REQUEST)
            self.get_perfect_params(cld, city_data)

        instance = self.get_food_court_object(cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FoodCourtSerializer(instance)
        try:
            serializer.update(instance, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def delete(self, request, *args, **kwargs):
        """
        删除美食城
        """
        form = FoodCourtDeleteForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_food_court_object(cld['pk'])
        if isinstance(instance, Exception):
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = FoodCourtSerializer(instance)
        try:
            serializer.delete(instance, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FoodCourtDetail(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly,)

    def get_food_court_object(self, food_court_id):
        return FoodCourt.get_object(pk=food_court_id)

    def post(self, request, *args, **kwargs):
        form = FoodCourtDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_food_court_object(cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FoodCourtSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FoodCourtList(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly, )

    def get_object_list(self, **kwargs):
        return FoodCourt.filter_objects(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        美食城信息列表
        返回数据格式为：{'count': 当前返回的数据量,
                       'all_count': 总数据量,
                       'has_next': 是否有下一页,
                       'data': [{
                                 FoodCourt model数据
                                },...]
                       }
        """
        form = FoodCourtListForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        datas = self.get_object_list(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FoodCourtListSerializer(datas)
        results = serializer.list_data(**cld)
        if isinstance(results, Exception):
            return Response({'Detail': results.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(results, status=status.HTTP_200_OK)


class UserWithFoodCourtList(generics.GenericAPIView):
    """
    菜品管理：商户列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_user_details(self, **kwargs):
        return BusinessUser.filter_users_detail(**kwargs)

    def get_food_court_objects(self, **kwargs):
        return FoodCourt.filter_objects(**kwargs)

    def get_objects(self, **kwargs):
        if 'food_court_name' in kwargs:
            f_instances = self.get_food_court_objects(name=kwargs['food_court_name'])
            f_ids = [f_ins.pk for f_ins in f_instances]
            user_filter = {'food_court_id__in': f_ids}
            if 'business_name' in kwargs:
                user_filter['business_name'] = kwargs['business_name']
            return self.get_user_details(**user_filter)
        elif 'business_name' in kwargs:
            user_filter = {'business_name': kwargs['business_name']}
            return self.get_user_details(**user_filter)
        else:
            return self.get_user_details()

    def post(self, request, *args, **kwargs):
        """
        商户+商城列表
        """
        form = UserWithFoodCourtListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_objects(**cld)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserWithFoodCourtListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class DishesList(generics.GenericAPIView):
    """
    菜品列表
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_objects_list(self, **kwargs):
        return Dishes.filter_objects(**kwargs)

    def post(self, request, *args, **kwargs):
        form = DishesListForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_objects_list(**cld)
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DishesListSerializer(instances)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class DishesDetail(generics.GenericAPIView):
    """
    菜品详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_dishes_object(self, dishes_id):
        return Dishes.get_object(pk=dishes_id)

    def post(self, request, *args, **kwargs):
        form = DishesDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_dishes_object(cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DishesSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DishesAction(generics.GenericAPIView):
    """
    菜品管理
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_dishes_instance(self, dishes_id):
        return Dishes.get_object(**{'pk': dishes_id})

    def get_user_object(self, user_id):
        return BusinessUser.get_object(pk=user_id)

    def post(self, request, *args, **kwargs):
        """
        创建菜品
        """
        form = DishesInputForm(data=request.data, files=request.FILES)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        user = self.get_user_object(cld['user_id'])
        if isinstance(user, Exception):
            return Response({'Detail': user.args}, status=status.HTTP_400_BAD_REQUEST)
        cld['food_court_id'] = user.food_court_id
        serializer = DishesSerializer(data=cld)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        更新菜品
        """
        form = DishesUpdateForm(data=request.data, files=request.FILES)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_dishes_instance(cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DishesSerializer(instance)
        try:
            serializer.update(instance, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def delete(self, request, *args, **kwargs):
        """
        下架菜品 
        """
        form = DishesDeleteForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_dishes_instance(cld['pk'])
        if isinstance(instance, Exception):
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = DishesSerializer(instance)
        try:
            serializer.delete(instance)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

USER_INITIAL_PASSWORD = '123456'


class UserAction(generics.GenericAPIView):
    """
    用户管理
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_user_object(self, user_id):
        return BusinessUser.get_object(pk=user_id)

    def is_request_data_valid(self, cld):
        if 'is_active' in cld:
            if len(cld) > 2:
                return False
        return True

    def post(self, request, *args, **kwargs):
        """
         创建用户
        """
        form = UsersInputForm(request.data, request.FILES)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        cld['password'] = USER_INITIAL_PASSWORD
        try:
            user = BusinessUser.objects.create_user(**cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        修改用户信息（修改普通信息、添加/移除黑名单）
        """
        form = UserUpdateForm(request.data, request.FILES)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        if not self.is_request_data_valid(cld):
            return Response({'Detail': 'The Params data is incorrect.'})
        user = self.get_user_object(cld['user_id'])
        if isinstance(user, Exception):
            return Response({'Detail': user.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user)
        try:
            serializer.update(user, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def patch(self, request, *args, **kwargs):
        """
        重置密码
        """
        form = UserResetPasswordForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        user = self.get_user_object(cld['user_id'])
        if isinstance(user, Exception):
            return Response({'Detail': user.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user)
        try:
            serializer.reset_password(user, USER_INITIAL_PASSWORD)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT )


class UserList(generics.GenericAPIView):
    """
    用户信息列表
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_objects_list(self, **kwargs):
        return BusinessUser.filter_users_detail(**kwargs)

    def get_food_court_list(self, **kwargs):
        return FoodCourt.filter_objects(**kwargs)

    def post(self, request, *args, **kwargs):
        form = UserListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        _objects = self.get_objects_list(**cld)
        if isinstance(_objects, Exception):
            return Response({'Detail': _objects.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserListSerializer(data=_objects)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class UserDetail(generics.GenericAPIView):
    """
    用户详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_user_object(self, user_id):
        user_list = BusinessUser.filter_users_detail(pk=user_id)
        if isinstance(user_list, Exception):
            return user_list
        if len(user_list) != 1:
            return Exception('Data Error.')
        return user_list[0]

    def post(self, request, *args, **kwargs):
        form = UserDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        user = self.get_user_object(cld['user_id'])
        if isinstance(user, Exception):
            return Response({'Detail': user.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserDetailSerializer(data=user)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WithdrawRecordList(generics.GenericAPIView):
    """
    提现查询（列表）
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_user_objects(self, business_name):
        return BusinessUser.filter_objects(business_name=business_name)

    def get_record_objects(self, **kwargs):
        if 'status' in kwargs:
            for key in kwargs:
                if key not in ['status', 'page_index', 'page_size']:
                    return Exception('Data error.')
        if 'business_name' in kwargs:
            users = self.get_user_objects(kwargs['business_name'])
            if isinstance(users, Exception):
                return users
            kwargs['user_id__in'] = [user.id for user in users]
        return WithdrawRecord.filter_record_details(**kwargs)

    def post(self, request, *args, **kwargs):
        form = WithdrawRecordListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        records = self.get_record_objects(**cld)
        if isinstance(records, Exception):
            return Response({'Detail': records.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WithdrawRecordListSerializer(data=records)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class WithdrawRecordDetail(generics.GenericAPIView):
    """
    提现记录查询（详情）
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_record_object(self, record_id):
        records = WithdrawRecord.filter_record_details(pk=record_id)
        if isinstance(records, Exception):
            return records
        if len(records) != 1:
            return Exception('Data error.')
        return records[0]

    def post(self, request, *args, **kwargs):
        form = WithdrawRecordDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        record = self.get_record_object(cld['pk'])
        if isinstance(record, Exception):
            return Response({'Detail': record.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WithdrawRecordSerializer(data=record)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WithdrawRecordAction(generics.GenericAPIView):
    """
    提现审核及打款
    """
    permission_classes = (IsAdminOrReadOnly,)

    def can_perform_this_action(self, record_id, status):
        record = WithdrawRecord.get_object(pk=record_id)
        if isinstance(record, Exception):
            return False, record
        if record.status not in WITHDRAW_RECORD_STATUS_STEP:
            return False, Exception('Can not perform this action.')
        if status not in WITHDRAW_RECORD_STATUS_STEP[record.status]:
            return False, Exception('Can not perform this action.')
        return True, record

    def put(self, request, *args, **kwargs):
        form = WithdrawRecordActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        can_bool, record = self.can_perform_this_action(record_id=cld['pk'],
                                                        status=cld['status'])
        if not can_bool:
            return Response({'Detail': record.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = WithdrawRecordInstanceSerializer(record)
        try:
            serializer.update_status(request, record, {'status': cld['status']})
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)


class OrdersList(generics.GenericAPIView):
    """
    订单查询
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_orders_list(self, **kwargs):
        if 'pay_orders_id' in kwargs and 'verify_orders_id' in kwargs:
            return Exception('Params Error.')
        if 'phone' in kwargs:
            user = BusinessUser.get_object(phone=kwargs['phone'])
            if isinstance(user, Exception):
                return user
            kwargs['user_id__in'] = user.id
            kwargs.pop('phone')

        orders_details = []
        if 'pay_orders_id' in kwargs:
            orders_details = Orders.filter_orders_details(**kwargs)
        elif 'verify_orders_id' in kwargs:
            orders_details = VerifyOrders.filter_orders_details(**kwargs)
        else:
            orders_list = Orders.filter_orders_details(**kwargs)
            verify_orders_list = VerifyOrders.filter_orders_details(**kwargs)
            try:
                orders_details = orders_list + verify_orders_list
            except Exception as e:
                return e

        if isinstance(orders_details, Exception):
            return orders_details
        return orders_details

    def post(self, request, *args, **kwargs):
        form = OrdersListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        orders_list = self.get_orders_list(**cld)
        if isinstance(orders_list, Exception):
            return Response({'Detail': orders_list.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OrdersListSerializer(data=orders_list)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class OrdersDetail(generics.GenericAPIView):
    """
    订单详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_orders_detail(self, **kwargs):
        orders_id = kwargs['orders_id']
        if orders_id.startswith('Z'):
            details = VerifyOrders.filter_orders_details(orders_id=orders_id)

        else:
            details = Orders.filter_orders_details(orders_id=orders_id)
        if isinstance(details, Exception):
            return details
        if len(details) != 1:
            return Exception('Data Error.')
        return details[0]

    def post(self, request, *args, **kwargs):
        form = OrdersDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        orders_detail = self.get_orders_detail(**cld)
        if isinstance(orders_detail, Exception):
            return Response({'Detail': orders_detail.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OrdersDetailSerializer(data=orders_detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BankCardAction(generics.GenericAPIView):
    """
    银行卡绑定或解除绑定 (需要管理员权限)
    """
    permission_classes = (IsAdminOrReadOnly,)

    def does_user_exist(self, request, user_id):
        ins = BusinessUser.get_object(pk=user_id)
        if isinstance(ins, Exception):
            return False
        return True

    def get_bank_card_instance(self, pk):
        return BankCard.get_object(_filter_all=False, pk=pk)

    def get_perfect_card_number(self, bank_card_number):
        re_com = re.compile(r'^[0-9]+$')
        card_num_list = bank_card_number.split()
        card_num_str = ''.join(card_num_list)
        for item in card_num_list:
            if not re_com.match(item):
                return ValueError('Bank card number is incorrect.')
        if len(card_num_str) > 20:
            return ValueError('Bank card number is incorrect.')

        perfect_list = []
        for index in range(len(card_num_str) / 4 + 1):
            if index * 4 < len(card_num_str):
                perfect_list.append(card_num_str[index * 4: index * 4 + 4])
        return ' '.join(perfect_list)

    def post(self, request, *args, **kwargs):
        """
        绑定银行卡
        """
        form = BankCardAddForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        if not self.does_user_exist(request, cld['user_id']):
            return Response({'Detail': 'The user %d does exist.' % cld['user_id']},
                            status=status.HTTP_400_BAD_REQUEST)

        bank_card_number = self.get_perfect_card_number(cld['bank_card_number'])
        if isinstance(bank_card_number, Exception):
            return Response({'Detail': bank_card_number.args}, status=status.HTTP_400_BAD_REQUEST)

        cld['bank_card_number'] = bank_card_number
        serializer = BankCardSerializer(data=cld)
        if serializer.is_valid():
            try:
                serializer.save(request)
            except Exception as e:
                return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        更改所绑定银行卡的信息
        """
        form = BankCardUpdateForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_bank_card_instance(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BankCardSerializer(instance)
        try:
            serializer.update(instance, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def delete(self, request, *args, **kwargs):
        """
        解除绑定银行卡
        """
        form = BankCardDeleteForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_bank_card_instance(cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': 'The bank card %d does not exist.' % cld['pk']},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = BankCardSerializer(instance)
        result = serializer.delete(request, instance)
        if isinstance(request, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BankCardList(generics.GenericAPIView):
    """
    获取绑定银行卡信息列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_bank_card_list(self, **kwargs):
        return BankCard.filter_objects(_filter_all=False, **kwargs)

    def post(self, request, *args, **kwargs):
        form = BankCardListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_bank_card_list(**cld)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BankCardListSerializer(details)
        result = serializer.list_data()
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


class BankCardDetail(generics.GenericAPIView):
    """
    获取绑定银行卡详情
    """
    def get_bank_card_object(self, bank_card_id):
        return BankCard.get_object(_filter_all=False, pk=bank_card_id)

    def post(self, request, *args, **kwargs):
        form = BankCardDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_bank_card_object(cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BankCardSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdvertPictureAction(generics.GenericAPIView):
    """
    轮播广告
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_instance(self, pk):
        return AdvertPicture.get_object(pk=pk)

    def get_food_court_object(self, food_court_id):
        return FoodCourt.get_object(pk=food_court_id)

    def does_food_court_exist(self, food_court_id):
        instance = self.get_food_court_object(food_court_id)
        if isinstance(instance, Exception):
            return False
        return True

    def post(self, request, *args, **kwargs):
        """
        添加广告图片
        """
        form = AdvertPictureInputForm(data=request.data, files=request.FILES)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        food_court_instance = self.get_food_court_object(cld['food_court_id'])
        if isinstance(food_court_instance, Exception):
            return Response({'Detail': food_court_instance.args},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = AdvertPictureSerializer(data=cld)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        更新图片信息
        """
        form = AdvertPictureUpdateForm(data=request.data, files=request.FILES)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        if 'food_court_id' in cld:
            does_exist = self.does_food_court_exist(cld['food_court_id'])
            if not does_exist:
                return Response(
                    {'Detail': 'The food court %d does not exist' % cld['food_court_id']},
                    status=status.HTTP_400_BAD_REQUEST)

        advert_instance = self.get_instance(pk=cld['pk'])
        if isinstance(advert_instance, Exception):
            return Response({'Detail': advert_instance.args},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = AdvertPictureSerializer(advert_instance)
        try:
            serializer.update(advert_instance, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def delete(self, request, *args, **kwargs):
        """
        删除广告图片
        """
        form = AdvertPictureDeleteForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_instance(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AdvertPictureSerializer(instance)
        try:
            serializer.delete(instance)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdvertPictureList(generics.GenericAPIView):
    """
    广告列表查询
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_advert_picture_instances(self, **kwargs):
        if 'food_court_name' in kwargs:
            food_court_instances = FoodCourt.filter_objects(name=kwargs.pop('food_court_name'))
            if not food_court_instances:
                return []
            kwargs['food_court_id__in'] = [instance.id for instance in food_court_instances]
        return AdvertPicture.filter_details(**kwargs)

    def post(self, request, *args, **kwargs):
        form = AdvertPictureListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_advert_picture_instances(**cld)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AdvertPictureListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class AdvertPictureDetail(generics.GenericAPIView):
    """
    广告图片详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_advert_picture_object(self, advert_picture_id):
        instances = AdvertPicture.filter_details(pk=advert_picture_id)
        if isinstance(instances, Exception):
            return instances
        if len(instances) != 1:
            return Exception('Advert picture of %d does not existed.' % advert_picture_id)
        return instances[0]

    def post(self, request, *args, **kwargs):
        form = AdvertPictureDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        detail = self.get_advert_picture_object(cld['pk'])
        if isinstance(detail, Exception):
            return Response({'Detail': detail.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AdvertPictureDetailSerializer(data=detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
