# -*- coding:utf8 -*-
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from consumer import views

urlpatterns = [
    url(r'^user_list/$', views.UserList.as_view()),
    url(r'^user_detail/$', views.UserDetail.as_view()),
    url(r'^user_action/$', views.UserAction.as_view()),

    url(r'^recharge_orders_list/$', views.RechargeList.as_view()),
    url(r'^recharge_orders_detail/$', views.RechargeDetail.as_view()),

    url(r'^consume_orders_list/$', views.ConsumeOrdersList.as_view()),
    url(r'^consume_orders_detail/$', views.ConsumeOrdersDetail.as_view()),

    url(r'^comment_list/$', views.CommentList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


