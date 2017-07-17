# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from business.serializers import (CitySerializer,)
from business.permissions import IsAdminOrReadOnly
from users.models import (AdminUser,
                          make_token_expire,
                          IdentifyingCode)
from business.forms import (CityInputForm,
                            )

from Business_App.bz_users.models import BusinessUser


class CityAction(generics.GenericAPIView):
    """
    城市管理
    """
    permission_classes = (IsAdminOrReadOnly,)

    def post(self, request, *args, **kwargs):
        """
        创建城市
        """
        form = CityInputForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        serializer = CitySerializer(data=cld, request=request)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        result = serializer.save()
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

