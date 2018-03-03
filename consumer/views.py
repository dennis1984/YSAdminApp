# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from consumer.serializers import (UserListSerializer,
                                  UserDetailSerializer,
                                  UserSerializer,
                                  RechargeOrdersSerializer,
                                  RechargeOrdersListSerializer,
                                  ConsumerOrdersSerializer,
                                  ConsumeOrdersListSerializer,
                                  ReplyCommentSerializer,
                                  WalletListSerializer,
                                  WalletTradeDetailListSerializer,
                                  CommentListSerializer,
                                  PayOrdersSerializer,
                                  FeedbackSerializer,
                                  FeedbackListSerializer,
                                  WalletRechargeGiftSerializer,
                                  WalletRechargeGiftDetailSerializer,
                                  WalletRechargeGiftListSerializer,
                                  ConsumeOrdersSerializer)
from consumer.permissions import IsAdminOrReadOnly
from consumer.forms import (UserListForm,
                            UserDetailForm,
                            UserUpdateForm,
                            RechargeListForm,
                            RechargeDetailForm,
                            ConsumeOrdersListForm,
                            ConsumeOrdersDetailForm,
                            ReplyCommentInputForm,
                            WalletListForm,
                            WalletTradeDetailListForm,
                            RechargeActionFrom,
                            CommentListForm,
                            FeedbackListForm,
                            FeedbackDetailForm,
                            WalletRechargeGiftActionForm,
                            WalletRechargeGiftListForm,
                            WalletRechargeGiftDetailForm,
                            CancelUnConsumedOrdersActionForm,
                            ConfirmUnConsumedOrdersActionForm)

from Consumer_App.cs_users.models import ConsumerUser
from Consumer_App.cs_comment.models import Comment
from Consumer_App.cs_wallet.models import Wallet, WalletTradeDetail, WalletRechargeGift
from Consumer_App.cs_orders.models import (PayOrders,
                                           ConsumeOrders,
                                           ORDERS_PAYMENT_MODE)
from Consumer_App.cs_setup.models import Feedback
from horizon.models import model_to_dict
from horizon import main
import copy


class UserList(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly, )

    def get_user_list(self, cld):
        if 'user_id' in cld:
            cld['pk'] = cld.pop('user_id')
        return ConsumerUser.filter_users_detail(fuzzy=True, **cld)

    def post(self, request, *args, **kwargs):
        form = UserListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        users = self.get_user_list(cld)
        serializer = UserListSerializer(data=users)
        if serializer.is_valid():
            datas = serializer.list_data(**cld)
            if isinstance(datas, Exception):
                return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
            return Response(datas, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(generics.GenericAPIView):
    """
    用户详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_user_object(self, user_id):
        user_list = ConsumerUser.filter_users_detail(**{'pk': user_id})
        if isinstance(user_list, Exception):
            return user_list
        return user_list[0]

    def post(self, request, *args, **kwargs):
        form = UserDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        user = self.get_user_object(cld['pk'])
        if isinstance(user, Exception):
            return Response({'Detail': user.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserDetailSerializer(data=user)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAction(generics.GenericAPIView):
    """
    用户Action
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_user_object(self, user_id):
        return ConsumerUser.get_object(**{'pk': user_id})

    def put(self, request, *args, **kwargs):
        """
        添加或移除黑名单
        """
        form = UserUpdateForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        user = self.get_user_object(cld['pk'])
        if isinstance(user, Exception):
            return Response({'Detail': user.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(user)
        try:
            serializer.update(user, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)


class RechargeList(generics.GenericAPIView):
    """
    会员充值记录查询
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_recharge_orders(self, **kwargs):
        if 'phone' in kwargs:
            user = self.get_user_object(kwargs['phone'])
            if isinstance(user, Exception):
                return []
            kwargs.pop('phone')
            kwargs['user_id'] = user.id
        if 'recharge_type' in kwargs:
            if int(kwargs['recharge_type']) == 1:
                filter_payment_mode_list = [value
                                            for key, value in ORDERS_PAYMENT_MODE.items()
                                            if key != 'admin']
                kwargs['payment_mode__in'] = filter_payment_mode_list
            else:
                kwargs['payment_mode'] = ORDERS_PAYMENT_MODE['admin']
        if 'end_created' in kwargs:
            kwargs['end_created'] = main.make_time_delta_for_custom(kwargs['end_created'],
                                                                    days=1)
        return PayOrders.filter_orders_details(_filter='RECHARGE', **kwargs)

    def get_user_object(self, phone):
        return ConsumerUser.get_object(phone=phone)

    def post(self, request, *args, **kwargs):
        form = RechargeListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        orders = self.get_recharge_orders(**cld)
        if isinstance(orders, Exception):
            return Response({'Detail': orders.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RechargeOrdersListSerializer(data=orders)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status.HTTP_200_OK)


class RechargeDetail(generics.GenericAPIView):
    """
    充值订单详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_recharge_orders_detail(self, orders_id):
        orders_list = PayOrders.filter_orders_details(_filter='RECHARGE',
                                               **{'orders_id': orders_id})
        if isinstance(orders_list, Exception):
            return orders_list
        if len(orders_list) != 1:
            return Exception('Data Error.')
        return orders_list[0]

    def post(self, request, *args, **kwargs):
        form = RechargeDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        orders_detail = self.get_recharge_orders_detail(cld['orders_id'])
        if isinstance(orders_detail, Exception):
            return Response({'Detail': orders_detail.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RechargeOrdersSerializer(data=orders_detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConsumeOrdersList(generics.GenericAPIView):
    """
    消费订单列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def filter_orders_details(self, **kwargs):
        if 'pay_orders_id' in kwargs:
            kwargs['master_orders_id'] = kwargs['pay_orders_id']
        if 'consume_orders_id' in kwargs:
            kwargs['orders_id'] = kwargs['consume_orders_id']
        if 'phone' in kwargs:
            user = self.get_user_object(kwargs['phone'])
            if isinstance(user, Exception):
                return []
            kwargs['user_id'] = user.id
        if 'end_created' in kwargs:
            kwargs['end_created'] = main.make_time_delta_for_custom(kwargs['end_created'],
                                                                    days=1)
        return ConsumeOrders.filter_orders_details(**kwargs)

    def get_user_object(self, phone):
        return ConsumerUser.get_object(phone=phone)

    def post(self, request, *args, **kwargs):
        form = ConsumeOrdersListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.filter_orders_details(**cld)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ConsumeOrdersListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class ConsumeOrdersDetail(generics.GenericAPIView):
    """
    消费订单详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_orders_detail(self, **kwargs):
        details = ConsumeOrders.filter_orders_details(orders_id=kwargs['consume_orders_id'])
        if isinstance(details, Exception):
            return details
        if len(details) != 1:
            return Exception('Data Error.')
        return details[0]

    def post(self, request, *args, **kwargs):
        form = ConsumeOrdersDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        detail = self.get_orders_detail(**cld)
        if isinstance(detail, Exception):
            return Response({'Detail': detail.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ConsumerOrdersSerializer(data=detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReplyCommentAction(generics.GenericAPIView):
    """
    回复消费者评论
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_comment_object(self, comment_id):
        return Comment.get_object(pk=comment_id)

    def make_perfect_initial_data(self, cld, comment):
        data = copy.deepcopy(cld)
        data['orders_id'] = comment.orders_id
        return data

    def post(self, request, *args, **kwargs):
        form = ReplyCommentInputForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        comment = self.get_comment_object(cld['comment_id'])
        if isinstance(comment, Exception):
            return Response({'Detail': comment.args}, status=status.HTTP_400_BAD_REQUEST)

        init_data = self.make_perfect_initial_data(cld, comment)
        serializer = ReplyCommentSerializer(data=init_data, request=request)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WalletList(generics.GenericAPIView):
    """
    用户钱包详情列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_wallet_list(self, **kwargs):
        if 'phone' in kwargs:
            user = self.get_user_object(kwargs['phone'])
            if isinstance(user, Exception):
                return user
            user_id = user.id
            if 'user_id' in kwargs:
                if kwargs['user_id'] != user_id:
                    return Exception('User does not existed.')
            else:
                kwargs['user_id'] = user_id
        return ConsumerUser.filter_users_detail(**kwargs)

    def get_user_object(self, phone):
        return ConsumerUser.get_object(phone=phone)

    def post(self, request, *args, **kwargs):
        form = WalletListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        wallets = self.get_wallet_list(**cld)
        if isinstance(wallets, Exception):
            return Response({'Detail': wallets.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WalletListSerializer(data=wallets)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class WalletTradeDetailList(generics.GenericAPIView):
    """
    交易明细详情列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_objects(self, user_id):
        return WalletTradeDetail.get_success_list(user_id=user_id)

    def post(self, request, *args, **kwargs):
        form = WalletTradeDetailListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        wallet_trade_details = self.get_objects(cld['user_id'])
        if isinstance(wallet_trade_details, Exception):
            return Response({'Detail': wallet_trade_details.args},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = WalletTradeDetailListSerializer(wallet_trade_details)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class WalletAction(generics.GenericAPIView):
    """
    向用户充值 (管理员操作)
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_user_object(self, user_id):
        return ConsumerUser.get_object(pk=user_id)

    def make_orders_by_recharge(self, user_id=None, payable=None, **kwargs):
        return PayOrders.make_orders_by_recharge(user_id, payable)

    def put(self, request, *args, **kwargs):
        form = RechargeActionFrom(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        user = self.get_user_object(cld['user_id'])
        if isinstance(user, Exception):
            return Response({'Detail': user.args}, status=status.HTTP_400_BAD_REQUEST)

        _data = self.make_orders_by_recharge(**cld)
        serializer = PayOrdersSerializer(data=_data)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            wallet_detail = serializer.go_to_recharge(**cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        # # 发送短信提醒用户充值成功
        # main.send_message_to_phone(cld['payable'], user.phone, template_name='recharge')
        return Response(wallet_detail, status=status.HTTP_206_PARTIAL_CONTENT)


class FeedbackList(generics.GenericAPIView):
    """
    意见反馈详情列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_feedback_list(self, **kwargs):
        return Feedback.filter_objects(**kwargs)

    def post(self, request, *args, **kwargs):
        form = FeedbackListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_feedback_list(**cld)
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FeedbackListSerializer(instances)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class FeedbackDetail(generics.GenericAPIView):
    """
    意见反馈详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_feedback_object(self, **kwargs):
        return Feedback.get_object(**kwargs)

    def post(self, request, *args, **kwargs):
        form = FeedbackDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_feedback_object(**cld)
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FeedbackSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentList(generics.GenericAPIView):
    permission_classes = (IsAdminOrReadOnly,)

    def get_comment_list(self, cld):
        return Comment.filter_comment_details(**cld)

    def post(self, request, *args, **kwargs):
        form = CommentListForm(request.data)
        if not form.is_valid():
            return Response({'Detail:': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_comment_list(cld)
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentListSerializer(data=instances)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        datas = serializer.list_data(**cld)
        if isinstance(datas, Exception):
            return Response({'Detail': datas.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas, status=status.HTTP_200_OK)


class WalletRechargeGiveGiftAction(generics.GenericAPIView):
    """
    钱包充值领取礼物
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_user_by_phone_number(self, phone_number):
        return ConsumerUser.get_object(phone=phone_number)

    def get_wallet_recharge_gift(self, user, verification_code):
        kwargs = {'user_id': user.id,
                  'verification_code': verification_code}
        return WalletRechargeGift.get_object(not_used=True, **kwargs)

    def is_verification_code_valid(self, phone_number, verification_code):
        user = self.get_user_by_phone_number(phone_number)
        if isinstance(user, Exception):
            return False, user.args

        recharge_gift = self.get_wallet_recharge_gift(user, verification_code)
        if isinstance(recharge_gift, Exception):
            return False, recharge_gift.args

        if not getattr(self, '_recharge_gift', None):
            self._recharge_gift = recharge_gift
        return True, None

    def put(self, request, *args, **kwargs):
        form = WalletRechargeGiftActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        is_valid, error_message = self.is_verification_code_valid(cld['phone_number'],
                                                                  cld['verification_code'])
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WalletRechargeGiftSerializer(self._recharge_gift)
        try:
            serializer.update_status_to_used(self._recharge_gift)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)


class WalletRechargeGiveGiftDetail(generics.GenericAPIView):
    """
    钱包充值领取礼物的兑奖码详情
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_wallet_recharge_gift_detail(self, pk):
        return WalletRechargeGift.get_detail(id=pk)

    def post(self, request, *args, **kwargs):
        form = WalletRechargeGiftDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        detail = self.get_wallet_recharge_gift_detail(cld['id'])
        if isinstance(detail, Exception):
            return Response({'Detail': detail.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WalletRechargeGiftDetailSerializer(data=detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletRechargeGiveGiftList(generics.GenericAPIView):
    """
    钱包充值领取礼物的兑奖码列表
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_user_by_phone_number(self, phone_number):
        return ConsumerUser.get_object(phone=phone_number)

    def get_wallet_recharge_gift_detail_list(self, phone_number=None, verification_code=None):
        kwargs = {}
        if phone_number:
            user = self.get_user_by_phone_number(phone_number)
            if isinstance(user, Exception):
                return user
            kwargs.update(**{'user_id': user.id})
        if verification_code:
            kwargs.update(**{'verification_code': verification_code})
        return WalletRechargeGift.filter_details(**kwargs)

    def post(self, request, *args, **kwargs):
        form = WalletRechargeGiftListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_wallet_recharge_gift_detail_list(cld.get('phone_number'),
                                                            cld.get('verification_code'))
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WalletRechargeGiftListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


class CancelUnConsumedOrdersAction(generics.GenericAPIView):
    """
    管理员取消消费者的未核销订单
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_consume_orders(self, orders_id):
        return ConsumeOrders.get_object(orders_id=orders_id)

    def is_consume_orders(self, orders_instance):
        if not orders_instance.is_consume_orders:
            return False, 'The Orders\'s payment_status is incorrect.'
        return True, None

    def put(self, request, *args, **kwargs):
        form = CancelUnConsumedOrdersActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_consume_orders(cld['orders_id'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        is_valid, error_message = self.is_consume_orders(instance)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ConsumeOrdersSerializer(instance)
        try:
            serializer.update_payment_status_to_cancel(instance)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Result': True}, status=status.HTTP_206_PARTIAL_CONTENT)


class ConfirmUnConsumedOrdersAction(generics.GenericAPIView):
    """
    确认核销消费者的未核销订单
    """
    permission_classes = (IsAdminOrReadOnly,)

    def get_consume_orders(self, orders_id):
        return ConsumeOrders.get_object(orders_id=orders_id)

    def is_consume_orders(self, orders_instance):
        if not orders_instance.is_consume_orders:
            return False, 'The Orders\'s payment_status is incorrect.'
        return True, None

    def put(self, request, *args, **kwargs):
        form = ConfirmUnConsumedOrdersActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_consume_orders(cld['orders_id'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        is_valid, error_message = self.is_consume_orders(instance)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ConsumeOrdersSerializer(instance)
        try:
            serializer.update_payment_status_to_consumed(instance)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Result': True}, status=status.HTTP_206_PARTIAL_CONTENT)
