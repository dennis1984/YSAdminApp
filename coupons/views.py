# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from coupons.serializers import (CouponsSerializer,
                                 CouponsListSerializer,
                                 DishesDiscountSerializer,
                                 DishesDiscountDetailSerializer,
                                 DishesDiscountListSerializer,
                                 CouponsSendRecordListSerializer,
                                 CouponsUsedRecordListSerializer)
from coupons.permissions import IsAdminOrReadOnly
from coupons.models import (CouponsConfig,
                            DishesDiscountConfig,
                            CouponsSendRecord,
                            CouponsUsedRecord,
                            COUPONS_CONFIG_TYPE,
                            COUPONS_CONFIG_TYPE_CN_MATCH,
                            COUPONS_CONFIG_TYPE_DETAIL)
from coupons.forms import (CouponsInputForm,
                           CouponsUpdateForm,
                           CouponsDeleteForm,
                           CouponsListForm,
                           CouponsDetailForm,
                           DishesDiscountInputForm,
                           DishesDiscountUpdateForm,
                           DishesDiscountDeleteForm,
                           DishesDiscountDetailForm,
                           DishesDiscountListForm,
                           SendCouponsForm,
                           CouponsSendRecordForm,
                           CouponsUsedRecordForm)

from Business_App.bz_users.models import BusinessUser
from Business_App.bz_dishes.models import Dishes
from Consumer_App.cs_coupons.models import CouponsAction as CouponsConfigAction
from django.utils.timezone import now

import json


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
        if cld.get('type') == COUPONS_CONFIG_TYPE['cash']:
            if 'amount_of_money' not in cld:
                return False, Exception('Amount Of Money is required.')
        elif cld.get('type') == COUPONS_CONFIG_TYPE['discount']:
            if 'discount_percent' not in cld:
                return False, Exception('Discount Percent is required.')

        if method.upper() == 'POST':
            if cld['service_ratio'] + cld['business_ratio'] != 100:
                return False, Exception('The sum of fields [service_ratio, business_ratio]'
                                        ' must be 100')
        else:
            if 'service_ratio' in cld or 'business_ratio' in cld:
                service_ratio = cld.get('service_ratio', 0)
                business_ratio = cld.get('business_ratio', 0)
                if service_ratio + business_ratio != 100:
                    return False, Exception('The sum of fields [service_ratio, business_ratio] '
                                            'must be 100')

        if cld.get('type_detail') == COUPONS_CONFIG_TYPE_DETAIL['recharge_give']:
            if not cld.get('each_count'):
                return False, Exception('When [type_detail] is "recharge_give",'
                                        'The field [each_count] does can not empty.')
        else:
            if cld.get('each_count'):
                cld.pop('each_count')

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
        form = CouponsUpdateForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_coupons_object(pk=cld['pk'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CouponsSerializer(instance)
        try:
            serializer.update(instance, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    # def delete(self, request, *args, **kwargs):
    #     """
    #     删除优惠券信息
    #     """
    #     form = CouponsDeleteForm(request.data)
    #     if not form.is_valid():
    #         return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     cld = form.cleaned_data
    #     instance = self.get_coupons_object(pk=cld['pk'])
    #     if isinstance(instance, Exception):
    #         return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
    #     serializer = CouponsSerializer(instance)
    #     try:
    #         serializer.delete(instance)
    #     except Exception as e:
    #         return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


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
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)
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

    def get_dishes_discount_object(self, dishes_id):
        return DishesDiscountConfig.get_object(dishes_id=dishes_id)

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

        instance = self.get_dishes_discount_object(dishes_id=cld['dishes_id'])
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
        instance = self.get_dishes_discount_object(dishes_id=cld['dishes_id'])
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
        if 'business_name' in kwargs:
            business_users = BusinessUser.filter_objects(fuzzy=True,
                                                         business_name=kwargs['business_name'])
            business_ids = [user.id for user in business_users]
            kwargs['user_id__in'] = business_ids
            kwargs.pop('business_name')
        if 'dishes_name' in kwargs:
            kwargs['title'] = kwargs.pop('dishes_name')
        return DishesDiscountConfig.filter_discount_config_details(fuzzy=True, **kwargs)

    def post(self, request, *args, **kwargs):
        form = DishesDiscountListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_dishes_discount_list(**cld)
        serializer = DishesDiscountListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class DishesDiscountDetail(generics.GenericAPIView):
    """
    菜品优惠券详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_dishes_discount_object(self, dishes_id):
        return DishesDiscountConfig.get_discount_config_detail(dishes_id=dishes_id)

    def post(self, request, *args, **kwargs):
        form = DishesDiscountDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        detail = self.get_dishes_discount_object(dishes_id=cld['dishes_id'])
        if isinstance(detail, Exception):
            return Response({'Detail': detail.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DishesDiscountDetailSerializer(data=detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendCoupons(generics.GenericAPIView):
    """
    发放优惠券
    """
    permission_classes = (IsAdminOrReadOnly,)

    def is_request_valid(self, request):
        form = SendCouponsForm(request.data)
        if not form.is_valid():
            return False, Exception(form.errors)

        cld = form.cleaned_data
        if cld['consumer_ids'] != 'all':
            try:
                cld['consumer_ids'] = json.loads(cld['consumer_ids'])
            except Exception as e:
                return False, e

        coupons_instance = self.get_coupons_object(coupons_id=cld['coupons_id'])
        if isinstance(coupons_instance, Exception):
            return False, coupons_instance
        cld['coupons'] = coupons_instance
        return True, cld

    def get_coupons_object(self, coupons_id):
        return CouponsConfig.get_active_object(pk=coupons_id)

    def post(self, request, *args, **kwargs):
        is_valid, cld = self.is_request_valid(request)
        if not is_valid:
            return Response({'Detail': cld.args}, status=status.HTTP_400_BAD_REQUEST)

        coupons = cld['coupons']
        send_count = CouponsConfigAction().create_coupons(cld['consumer_ids'], coupons)
        if isinstance(send_count, Exception):
            return Response({'Detail': send_count.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CouponsSerializer(coupons)
        try:
            serializer.add_send_count(coupons, send_count)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CouponsSendRecordList(generics.GenericAPIView):
    """
    优惠券派发记录
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_send_record_details(self, **kwargs):
        if 'coupons_name' in kwargs:
            instances = CouponsConfig.filter_objects(fuzzy=True, name=kwargs.pop('coupons_name'))
            coupons_ids = [ins.id for ins in instances]
            kwargs['coupons_id__in'] = coupons_ids
        return CouponsSendRecord.filter_perfect_objects(**kwargs)

    def post(self, request, *args, **kwargs):
        form = CouponsSendRecordForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_send_record_details(**cld)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CouponsSendRecordListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class CouponsUsedRecordList(generics.GenericAPIView):
    """
    优惠券使用记录
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_used_record_details(self, **kwargs):
        if 'coupons_name' in kwargs:
            instances = CouponsConfig.filter_objects(fuzzy=True, name=kwargs.pop('coupons_name'))
            coupons_ids = [ins.id for ins in instances]
            kwargs['coupons_id__in'] = coupons_ids
        return CouponsUsedRecord.filter_perfect_objects(**kwargs)

    def post(self, request, *args, **kwargs):
        form = CouponsUsedRecordForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_used_record_details(**cld)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CouponsUsedRecordListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)
