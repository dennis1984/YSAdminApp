# -*- coding:utf8 -*-

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from business import views

urlpatterns = [
    url(r'^city_action/$', views.CityAction.as_view()),
    url(r'^city_list/$', views.CityList.as_view()),
    url(r'^city_detail/$', views.CityDetail.as_view()),

    url(r'^city_simple_list/$', views.CitySimpleList.as_view()),
    url(r'^district_list/$', views.DistrictList.as_view()),
    url(r'^food_court_action/$', views.FoodCourtAction.as_view()),
    url(r'^food_court_list/$', views.FoodCourtList.as_view()),
    url(r'^food_court_detail/$', views.FoodCourtDetail.as_view()),

    url(r'^user_with_food_court_list/$', views.UserWithFoodCourtList.as_view()),
    url(r'^dishes_list/$', views.DishesList.as_view()),
    url(r'^dishes_action/$', views.DishesAction.as_view()),
    url(r'^dishes_detail/$', views.DishesDetail.as_view()),

    url(r'^user_action/$', views.UserAction.as_view()),
    url(r'^user_list/$', views.UserList.as_view()),

    url(r'^advert_picture_action/$', views.AdvertPictureAction.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


