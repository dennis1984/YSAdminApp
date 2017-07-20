# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from consumer.serializers import (UserListSerializer,
                                  CommentListSerializer)
from consumer.permissions import IsAdminOrReadOnly
from consumer.forms import (UserListForm,
                            CommentListForm)

from Consumer_App.cs_users.models import ConsumerUser
from Consumer_App.cs_comment.models import Comment


class UserList(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly, )

    def get_user_list(self, cld):
        return ConsumerUser.filter_users_detail(**cld)

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


class CommentList(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly,)

    def get_comment_list(self, cld):
        return Comment.get_object(**cld)

    def post(self, request, *args, **kwargs):
        form = CommentListForm(request.data)
        if not form.is_valid():
            return Response({'Detail:': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_comment_list(cld)
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentListSerializer(instances)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)
