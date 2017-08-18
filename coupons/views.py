# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from coupons.serializers import (UserSerializer,
                                 UserInstanceSerializer,
                                 UserDetailSerializer,)
from coupons.permissions import IsAdminOrReadOnly
from coupons.models import (CouponsConfig,
                            DishesDiscountConfig,
                            COUPONS_CONFIG_TYPE,
                            COUPONS_CONFIG_TYPE_CN_MATCH)
from coupons.forms import (CouponsInputForm)

from Business_App.bz_users.models import BusinessUser


class CouponsAction(generics.GenericAPIView):
    """
    优惠券创建、更新及删除
    """
    permission_classes = (IsAdminOrReadOnly, )

    def is_request_valid(self, request):
        form = CouponsInputForm(request.data)
        if not form.is_valid():
            return False, Exception(form.errors)

        cld = form.cleaned_data
        if cld['type'] == COUPONS_CONFIG_TYPE['custom']:
            if 'type_detail' not in cld:
                return False, Exception('When type is 200, type_detail must not be empty.')
        if cld['service_ratio'] + cld['business_ratio'] != 100:
            return False, Exception('The sum of fields [service_ratio, business_ratio] must be 100')
        return True, cld

    def post(self, request, *args, **kwargs):
        """
        创建优惠券
        """
        is_valid, cld = self.is_request_valid(request)
        if not is_valid:
            return Response({'Detail': cld.args}, status=status.HTTP_400_BAD_REQUEST)


        try:
            user = BusinessUser.objects.create_user(**cld)
        except Exception as e:
            return Response({'Error': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserInstanceSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        更新用户信息
        """
        form = UpdateUserInfoForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        obj = self.get_object_of_user(request)
        if isinstance(obj, Exception):
            return Response({'Detail': obj.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(obj)
        try:
            serializer.update_userinfo(request, obj, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer_response = UserInstanceSerializer(obj)
        return Response(serializer_response.data, status=status.HTTP_206_PARTIAL_CONTENT)

