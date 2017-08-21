# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from coupons.serializers import (CouponsSerializer,
                                 CouponsListSerializer,
                                 DishesDiscountSerializer,
                                 DishesDiscountListSerializer)
from coupons.permissions import IsAdminOrReadOnly
from coupons.models import (CouponsConfig,
                            DishesDiscountConfig,
                            COUPONS_CONFIG_TYPE,
                            COUPONS_CONFIG_TYPE_CN_MATCH)
from coupons.forms import (CouponsInputForm,
                           CouponsUpdateForm,
                           CouponsDeleteForm,
                           CouponsListForm,
                           CouponsDetailForm,
                           DishesDiscountInputForm,
                           DishesDiscountUpdateForm,
                           DishesDiscountDeleteForm,
                           DishesDiscountDetailForm,
                           DishesDiscountListForm)

from Business_App.bz_users.models import BusinessUser
from Business_App.bz_dishes.models import Dishes
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
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
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

        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class CouponsList(generics.GenericAPIView):
    """
    优惠券信息列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_coupons_list(self, **kwargs):
        return CouponsConfig.filter_objects(fuzzy=True, **kwargs)

    def post(self, request, *args, **kwargs):
        form = CouponsListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_coupons_list(**cld)
        serializer = CouponsListSerializer(instances)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class CouponsDetail(generics.GenericAPIView):
    """
    优惠券详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_coupons_object(self, pk):
        return CouponsConfig.get_object(pk=pk)

    def post(self, request, *args, **kwargs):
        form = CouponsDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_coupons_object(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CouponsSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DishesDiscountAction(generics.GenericAPIView):
    """
    菜品优惠信息创建、更新及删除
    """
    permission_classes = (IsAdminOrReadOnly, )

    def get_dishes_object(self, pk):
        return Dishes.get_object(pk=pk)

    def get_dishes_discount_object(self, pk):
        return DishesDiscountConfig.get_object(pk=pk)

    def is_request_valid(self, request, method='POST'):
        if method.upper() == 'POST':
            form = DishesDiscountInputForm(request.data)
        elif method.upper() == 'PUT':
            form = DishesDiscountUpdateForm(request.data)
        else:
            form = None
        if not form.is_valid():
            return False, Exception(form.errors)

        cld = form.cleaned_data
        if method.upper() == 'POST':
            dishes = self.get_dishes_object(pk=cld['dishes_id'])
            if isinstance(dishes, Exception):
                return False, Exception('Dishes does not existed.')
        if 'service_ratio' in cld or 'business_ratio' in cld:
            service_ratio = cld.get('service_ratio', 0)
            business_ratio = cld.get('business_ratio', 0)
            if service_ratio + business_ratio != 100:
                return False, Exception('The sum of fields [service_ratio, business_ratio] must be 100')
        if 'expires' in cld:
            if cld['expires'] < now():
                return False, Exception('Expires can not less than now.')
        return True, cld

    def post(self, request, *args, **kwargs):
        """
        创建菜品优惠信息
        """
        is_valid, cld = self.is_request_valid(request)
        if not is_valid:
            return Response({'Detail': cld.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DishesDiscountSerializer(data=cld)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        更新菜品优惠信息
        """
        is_valid, cld = self.is_request_valid(request, method='PUT')
        if not is_valid:
            return Response({'Detail': cld.args}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_dishes_discount_object(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DishesDiscountSerializer(instance)
        try:
            serializer.update(instance, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def delete(self, request, *args, **kwargs):
        """
        删除优惠券信息
        """
        form = DishesDiscountDeleteForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_dishes_discount_object(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DishesDiscountSerializer(instance)
        try:
            serializer.delete(instance)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class DishesDiscountList(generics.GenericAPIView):
    """
    菜品优惠信息列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_dishes_discount_list(self, **kwargs):
        return DishesDiscountConfig.filter_objects(fuzzy=True, **kwargs)

    def post(self, request, *args, **kwargs):
        form = DishesDiscountListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_dishes_discount_list(**cld)
        serializer = DishesDiscountListSerializer(instances)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class DishesDiscountDetail(generics.GenericAPIView):
    """
    优惠券详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_dishes_discount_object(self, pk):
        return DishesDiscountConfig.get_object(pk=pk)

    def post(self, request, *args, **kwargs):
        form = DishesDiscountDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_dishes_discount_object(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DishesDiscountSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
