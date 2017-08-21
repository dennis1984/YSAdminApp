# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from coupons.serializers import (CouponsSerializer)
from coupons.permissions import IsAdminOrReadOnly
from coupons.models import (CouponsConfig,
                            DishesDiscountConfig,
                            COUPONS_CONFIG_TYPE,
                            COUPONS_CONFIG_TYPE_CN_MATCH)
from coupons.forms import (CouponsInputForm,
                           CouponsUpdateForm,
                           CouponsDeleteForm)

from Business_App.bz_users.models import BusinessUser
from django.utils.timezone import now


class CouponsAction(generics.GenericAPIView):
    """
    优惠券创建、更新及删除
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_coupons_object(self, pk):
        return CouponsConfig.get_object(pk=pk)

    def is_request_valid(self, request, method='POST'):
        if method.upper() == 'POST':
            form = CouponsInputForm(request.data)
        elif method.upper() == 'PUT':
            form = CouponsUpdateForm(request.data)
        else:
            form = None
        if not form.is_valid():
            return False, Exception(form.errors)

        cld = form.cleaned_data
        if cld.get('type') == COUPONS_CONFIG_TYPE['custom']:
            if 'type_detail' not in cld:
                return False, Exception('When type is 200, type_detail must not be empty.')

        if method.upper() == 'POST':
            if cld['service_ratio'] + cld['business_ratio'] != 100:
                return False, Exception('The sum of fields [service_ratio, business_ratio] must be 100')
            if cld['expires'] < now():
                return False, Exception('Expires can not less than now.')
        else:
            if 'expires' in cld:
                if cld['expires'] < now():
                    return False, Exception('Expires can not less than now.')
            if 'service_ratio' in cld or 'business_ratio' in cld:
                service_ratio = cld.get('service_ratio', 0)
                business_ratio = cld.get('business_ratio', 0)
                if service_ratio + business_ratio != 100:
                    return False, Exception('The sum of fields [service_ratio, business_ratio] must be 100')

        return True, cld

    def post(self, request, *args, **kwargs):
        """
        创建优惠券
        """
        is_valid, cld = self.is_request_valid(request)
        if not is_valid:
            return Response({'Detail': cld.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CouponsSerializer(data=cld)
        try:
            serializer.save()
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        更新优惠券信息
        """
        is_valid, cld = self.is_request_valid(request, method='PUT')
        if not is_valid:
            return Response({'Detail': cld.args}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_coupons_object(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CouponsSerializer(instance)
        try:
            serializer.update(instance, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def delete(self, request, *args, **kwargs):
        """
        删除优惠券信息
        """
        form = CouponsDeleteForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_coupons_object(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CouponsSerializer(instance)
        try:
            serializer.delete(instance)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

