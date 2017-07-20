# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from business.serializers import (CitySerializer,
                                  CityListSerializer,
                                  FoodCourtSerializer,
                                  FoodCourtListSerializer,
                                  UserInstanceSerializer,
                                  UserListSerializer,
                                  DishesSerializer,
                                  AdvertPictureSerializer,)
from business.permissions import IsAdminOrReadOnly
from business.forms import (CityInputForm,
                            CityListForm,
                            FoodCourtInputForm,
                            FoodCourtListForm,
                            UsersInputForm,
                            UserListForm,
                            DishesListForm,
                            DishesUpdateForm,
                            AdvertPictureInputForm,
                            AdvertPictureDeleteForm)

from Business_App.bz_dishes.models import (City,
                                           Dishes,
                                           FoodCourt)
from Business_App.bz_dishes.caches import Dishes
from Business_App.bz_users.models import (BusinessUser,
                                          AdvertPicture)


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


class FoodCourtAction(generics.GenericAPIView):
    """
    美食城创建
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_city_object(self, city_id):
        return City.get_object(pk=city_id)

    def get_perfect_params(self, params_dict, city):
        params_dict.pop('city_id')
        params_dict['city'] = city.city

    def post(self, request, *args, **kwargs):
        """
        创建美食城
        """
        form = FoodCourtInputForm(request.data)
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


class FoodCourtList(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly, )

    def get_object_list(self, **kwargs):
        return FoodCourt.get_object_list(**kwargs)

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


class UserAction(generics.GenericAPIView):
    """
    用户管理
    """
    permission_classes = (IsAdminOrReadOnly, )

    def post(self, request, *args, **kwargs):
        """
         创建用户
        """
        form = UsersInputForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        try:
            user = BusinessUser.objects.create_user(**cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserInstanceSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserList(generics.GenericAPIView):
    """
    用户信息列表
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_objects_list(self, **kwargs):
        return BusinessUser.filter_users_detail(**kwargs)

    def post(self, request, *args, **kwargs):
        form = UserListForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

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


#### 需要再完善
class DishesList(generics.GenericAPIView):
    """
    菜品列表
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_objects_list(self, **kwargs):
        return Dishes.filter_users_detail(**kwargs)

    def post(self, request, *args, **kwargs):
        form = DishesListForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

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


class DishesAction(generics.GenericAPIView):
    """
    菜品更新
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_dishes_instance(self, dishes_id):
        return Dishes.get_object(**{'pk': dishes_id})

    def update(self, request, *args, **kwargs):
        form = DishesUpdateForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_dishes_instance(cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DishesSerializer(instance)
        result = serializer.update_dishes_recommend_status(instance, cld)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)


class AdvertPictureAction(generics.GenericAPIView):
    """
    轮播广告
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_instance(self, pk):
        return AdvertPicture.get_object(pk=pk)

    def post(self, request, *args, **kwargs):
        """
        添加广告图片
        """
        form = AdvertPictureInputForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        serializer = AdvertPictureSerializer(data=cld)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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

