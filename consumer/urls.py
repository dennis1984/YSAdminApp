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

    url(r'^wallet_list/$', views.WalletList.as_view()),
    url(r'^wallet_trade_detail_list/$', views.WalletTradeDetailList.as_view()),
    url(r'^wallet_action/$', views.WalletAction.as_view()),

    url(r'^consume_orders_list/$', views.ConsumeOrdersList.as_view()),
    url(r'^consume_orders_detail/$', views.ConsumeOrdersDetail.as_view()),
    url(r'^reply_comment_action/$', views.ReplyCommentAction.as_view()),

    # 意见反馈
    url(r'^feedback_list/$', views.FeedbackList.as_view()),
    url(r'^feedback_detail/$', views.FeedbackList.as_view()),

    url(r'^comment_list/$', views.CommentList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


