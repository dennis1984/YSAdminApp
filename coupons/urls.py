# -*- coding:utf8 -*-

from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from coupons import views

urlpatterns = [
    url(r'^coupons_action/$', views.CouponsAction.as_view()),
    url(r'^coupons_list/$', views.CouponsList.as_view()),
    url(r'^coupons_detail/$', views.CouponsDetail.as_view()),

    url(r'^dishes_discount_action/$', views.DishesDiscountAction.as_view()),
    url(r'^dishes_discount_list/$', views.DishesDiscountList.as_view()),
    url(r'^dishes_discount_detail/$', views.DishesDiscountDetail.as_view()),

    url(r'^send_coupons/$', views.SendCoupons.as_view()),
    url(r'^coupons_send_record_list/$', views.CouponsSendRecordList.as_view()),
    url(r'^coupons_used_record_list/$', views.CouponsUsedRecordList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
