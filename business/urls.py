# -*- coding:utf8 -*-

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from business import views

urlpatterns = [
    url(r'city_action/$', views.CityAction.as_view()),
    url(r'city_list/$', views.CityList.as_view()),

    url(r'food_court_action/$', views.FoodCourtAction.as_view()),
    url(r'food_court_list/$', views.FoodCourtList.as_view()),

    url(r'user_action/$', views.UserAction.as_view()),
    url(r'user_list/$', views.UserList.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)

