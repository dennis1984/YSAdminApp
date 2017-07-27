# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from consumer.serializers import (UserListSerializer,
                                  UserDetailSerializer,
                                  UserSerializer,
                                  CommentListSerializer)
from consumer.permissions import IsAdminOrReadOnly
from consumer.forms import (UserListForm,
                            UserDetailForm,
                            UserUpdateForm,
                            RechargeListForm,
                            CommentListForm)

from Consumer_App.cs_users.models import ConsumerUser
from Consumer_App.cs_comment.models import Comment
from Consumer_App.cs_orders.models import PayOrders


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
        return PayOrders.filter_objects(**kwargs)

    def post(self, request, *args, **kwargs):
        form = RechargeListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data




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
