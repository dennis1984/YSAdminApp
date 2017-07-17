# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from users.serializers import (UserSerializer,
                               UserInstanceSerializer,
                               UserDetailSerializer,
                               UserListSerializer,
                               IdentifyingCodeSerializer)
from users.permissions import IsAdminOrReadOnly
from users.models import (ConsumerUser,
                          make_token_expire,
                          IdentifyingCode)
from users.forms import (CreateUserForm,
                         SendIdentifyingCodeForm,
                         VerifyIdentifyingCodeForm,
                         UpdateUserInfoForm,
                         UsersInputForm,
                         SetPasswordForm,
                         WXAuthCreateUserForm)

from Business_App.bz_users.models import BusinessUser


class UserAction(generics.GenericAPIView):
    """
    update user API
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
            return Response({'Error': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserInstanceSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_object_of_user(self, request):
        return ConsumerUser.get_object(**{'pk': request.user.id})

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


class UserDetail(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly, )

    def post(self, request, *args, **kwargs):
        user = ConsumerUser.get_user_detail(request)
        if isinstance(user, Exception):
            return Response({'Error': user.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserDetailSerializer(user)
        # if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    queryset = ConsumerUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
