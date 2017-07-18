# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from business.serializers import (CitySerializer,
                                  CityListSerializer)
from business.permissions import IsAdminOrReadOnly
from business.forms import (CityInputForm,
                            CityListForm,
                            )

from Business_App.bz_dishes.models import (City,
                                           Dishes)
from Business_App.bz_users.models import BusinessUser


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


