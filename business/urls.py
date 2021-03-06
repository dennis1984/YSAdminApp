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
    url(r'^user_detail/$', views.UserDetail.as_view()),

    url(r'^withdraw_record_list/$', views.WithdrawRecordList.as_view()),
    url(r'^withdraw_record_detail/$', views.WithdrawRecordDetail.as_view()),
    url(r'^withdraw_record_action/$', views.WithdrawRecordAction.as_view()),

    url(r'^orders_list/$', views.OrdersList.as_view()),
    url(r'^orders_detail/$', views.OrdersDetail.as_view()),

    url(r'^bank_card_action/$', views.BankCardAction.as_view()),
    url(r'^bank_card_list/$', views.BankCardList.as_view()),
    url(r'^bank_card_detail/$', views.BankCardDetail.as_view()),

    url(r'^advert_picture_action/$', views.AdvertPictureAction.as_view()),
    url(r'^advert_picture_list/$', views.AdvertPictureList.as_view()),
    url(r'^advert_picture_detail/$', views.AdvertPictureDetail.as_view()),

    url(r'^app_version_action/$', views.AppVersionAction.as_view()),
    url(r'^app_version_detail/$', views.AppVersionDetail.as_view()),
    url(r'^app_version_list/$', views.AppVersionList.as_view()),

    url(r'^dishes_classify_action/$', views.DishesClassifyAction.as_view()),
    url(r'^dishes_classify_detail/$', views.DishesClassifyDetail.as_view()),
    url(r'^dishes_classify_list/$', views.DishesClassifyList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


