# -*- coding:utf8 -*-

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from business import views

urlpatterns = [
    url(r'city_action/$', views.CityAction.as_view()),
    url(r'city_list/$', views.CityAction.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)


