# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from users.serializers import (UserSerializer,
                               UserDetailSerializer,
                               IdentifyingCodeSerializer)
from users.permissions import IsAdminOrReadOnly
from users.models import (AdminUser,
                          make_token_expire,
                          IdentifyingCode,
                          PERMISSION_LIST)
from users.forms import (CreateUserForm,
                         SendIdentifyingCodeForm,
                         VerifyIdentifyingCodeForm,
                         UpdateUserForm,
                         SetPasswordForm,)
import json


class UserAction(generics.GenericAPIView):
    """
    update user API
    """
    permission_classes = (IsAdminOrReadOnly, )

    def is_request_data_valid(self, request):
        form = CreateUserForm(request.data)
        if not form.is_valid():
            return False, form.errors

        cld = form.cleaned_data
        if 'permission_list' in cld:
            try:
                json.loads(cld['permission_list'])
            except Exception as e:
                return False, e.args
        return True, cld

    def get_object_of_user(self, request):
        return AdminUser.get_object(**{'pk': request.user.id})

    def post(self, request, *args, **kwargs):
        """
         创建用户
        """
        is_valid, cld = self.is_request_data_valid(request)
        if not is_valid:
            return Response({'Detail': cld}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = AdminUser.objects.create_superuser(**cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserDetailSerializer(user.to_dict)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        更新用户信息
        """
        form = UpdateUserForm(request.data)
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

        serializer_response = UserDetailSerializer(obj.to_dict)
        if not serializer_response.is_valid():
            return Response({'Detail': serializer_response.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer_response.data, status=status.HTTP_206_PARTIAL_CONTENT)


class UserDetail(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly, )

    def get_object_of_user(self, request):
        return AdminUser.get_object(**{'pk': request.user.id})

    def post(self, request, *args, **kwargs):
        user = self.get_object_of_user(request)
        if isinstance(user, Exception):
            return Response({'Detail': user.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserDetailSerializer(user.to_dict)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PermissionList(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly, )

    def post(self, request, *args, **kwargs):
        permission_list = PERMISSION_LIST
        return Response(permission_list, status=status.HTTP_200_OK)


class AuthLogout(generics.GenericAPIView):
    """
    用户认证：登出
    """
    def post(self, request, *args, **kwargs):
        make_token_expire(request)
        return Response(status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = AdminUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
