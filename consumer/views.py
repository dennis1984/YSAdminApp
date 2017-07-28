# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from consumer.serializers import (UserListSerializer,
                                  UserDetailSerializer,
                                  UserSerializer,
                                  RechargeOrdersSerializer,
                                  RechargeOrdersListSerializer,
                                  ConsumerOrdersSerializer,
                                  ConsumeOrdersListSerializer,
                                  CommentListSerializer)
from consumer.permissions import IsAdminOrReadOnly
from consumer.forms import (UserListForm,
                            UserDetailForm,
                            UserUpdateForm,
                            RechargeListForm,
                            RechargeDetailForm,
                            ConsumeOrdersListForm,
                            CommentListForm)

from Consumer_App.cs_users.models import ConsumerUser
from Consumer_App.cs_comment.models import Comment
from Consumer_App.cs_orders.models import (PayOrders,
                                           ConsumeOrders,
                                           ORDERS_PAYMENT_MODE)


class UserList(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly, )

    def get_user_list(self, cld):
        if 'user_id' in cld:
            cld['pk'] = cld.pop('user_id')
        return ConsumerUser.filter_users_detail(fuzzy=True, **cld)

    def post(self, request, *args, **kwargs):
        form = UserListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        users = self.get_user_list(cld)
        serializer = UserListSerializer(data=users)
        if serializer.is_valid():
            datas = serializer.list_data(**cld)
            if isinstance(datas, Exception):
                return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
            return Response(datas, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(generics.GenericAPIView):
    """
    用户详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_user_object(self, user_id):
        user_list = ConsumerUser.filter_users_detail(**{'pk': user_id})
        if isinstance(user_list, Exception):
            return user_list
        return user_list[0]

    def post(self, request, *args, **kwargs):
        form = UserDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        user = self.get_user_object(cld['pk'])
        if isinstance(user, Exception):
            return Response({'Detail': user.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserDetailSerializer(data=user)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAction(generics.GenericAPIView):
    """
    用户Action
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_user_object(self, user_id):
        return ConsumerUser.get_object(**{'pk': user_id})

    def put(self, request, *args, **kwargs):
        """
        添加或移除黑名单
        """
        form = UserUpdateForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        user = self.get_user_object(cld['pk'])
        if isinstance(user, Exception):
            return Response({'Detail': user.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(user)
        try:
            serializer.update(user, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)


class RechargeList(generics.GenericAPIView):
    """
    会员充值记录查询
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_recharge_orders(self, **kwargs):
        if 'phone' in kwargs:
            user = self.get_user_object(kwargs['phone'])
            if isinstance(user, Exception):
                return []
            kwargs.pop('phone')
            kwargs['user_id'] = user.id
        if 'recharge_type' in kwargs:
            if int(kwargs['recharge_type']) == 1:
                filter_payment_mode_list = [value
                                            for key, value in ORDERS_PAYMENT_MODE.items()
                                            if key != 'admin']
                kwargs['payment_mode__in'] = filter_payment_mode_list
            else:
                kwargs['payment_mode'] = ORDERS_PAYMENT_MODE['admin']
        return PayOrders.filter_orders_details(_filter='RECHARGE', **kwargs)

    def get_user_object(self, phone):
        return ConsumerUser.get_object(phone=phone)

    def post(self, request, *args, **kwargs):
        form = RechargeListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        orders = self.get_recharge_orders(**cld)
        if isinstance(orders, Exception):
            return Response({'Detail': orders.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RechargeOrdersListSerializer(data=orders)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status.HTTP_200_OK)


class RechargeDetail(generics.GenericAPIView):
    """
    充值订单详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_recharge_orders_detail(self, orders_id):
        orders_list = PayOrders.filter_orders_details(_filter='RECHARGE',
                                               **{'orders_id': orders_id})
        if isinstance(orders_list, Exception):
            return orders_list
        if len(orders_list) != 1:
            return Exception('Data Error.')
        return orders_list[0]

    def post(self, request, *args, **kwargs):
        form = RechargeDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        orders_detail = self.get_recharge_orders_detail(cld['orders_id'])
        if isinstance(orders_detail, Exception):
            return Response({'Detail': orders_detail.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RechargeOrdersSerializer(data=orders_detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConsumeOrdersList(generics.GenericAPIView):
    """
    消费订单列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def filter_orders_details(self, **kwargs):
        return ConsumeOrders.filter_objects_detail(**kwargs)

    def post(self, request, *args, **kwargs):
        form = ConsumeOrdersListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.filter_orders_details(**cld)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ConsumeOrdersListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class CommentList(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly,)

    def get_comment_list(self, cld):
        return Comment.filter_comment_details(**cld)

    def post(self, request, *args, **kwargs):
        form = CommentListForm(request.data)
        if not form.is_valid():
            return Response({'Detail:': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_comment_list(cld)
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentListSerializer(data=instances)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)
