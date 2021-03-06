# -*- encoding: utf-8 -*-
from horizon import forms


class UserListForm(forms.Form):
    phone = forms.CharField(min_length=11, max_length=16, required=False)
    user_id = forms.IntegerField(min_value=1, required=False)
    nickname = forms.CharField(min_length=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class UserDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class UserUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    is_active = forms.IntegerField(min_value=0, max_value=1)


class RechargeListForm(forms.Form):
    orders_id = forms.CharField(min_length=14, max_length=32, required=False)
    phone = forms.CharField(min_length=11, max_length=15, required=False)
    recharge_type = forms.ChoiceField(choices=((1, 1),
                                               (2, 2)),
                                      required=False)
    start_created = forms.DateField(required=False)
    end_created = forms.DateField(required=False)
    payment_status = forms.ChoiceField(choices=((0, 1),
                                                (200, 2),
                                                (400, 3),
                                                (500, 4)),
                                       error_messages={'required': u'支付状态不能为空'})
    min_payable = forms.FloatField(min_value=0, required=False)
    max_payable = forms.FloatField(min_value=0, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class RechargeDetailForm(forms.Form):
    orders_id = forms.CharField(min_length=14, max_length=32)


class ConsumeOrdersListForm(forms.Form):
    pay_orders_id = forms.CharField(min_length=14, max_length=32, required=False)
    consume_orders_id = forms.CharField(min_length=14, max_length=32, required=False)
    phone = forms.CharField(min_length=11, max_length=15, required=False)
    business_name = forms.CharField(min_length=2, max_length=20, required=False)
    payment_status = forms.ChoiceField(choices=((201, 1),
                                                (206, 2)),
                                       error_messages={'required': u'支付状态不能为空'},
                                       required=False)
    start_created = forms.DateField(required=False)
    end_created = forms.DateField(required=False)
    min_payable = forms.FloatField(min_value=0, required=False)
    max_payable = forms.FloatField(min_value=0, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class ConsumeOrdersDetailForm(forms.Form):
    consume_orders_id = forms.CharField(min_length=14, max_length=32)


class ReplyCommentInputForm(forms.Form):
    comment_id = forms.IntegerField(min_value=1)
    messaged = forms.CharField(max_length=256)


class WalletListForm(forms.Form):
    user_id = forms.IntegerField(min_value=1, required=False)
    phone = forms.CharField(min_length=11, max_length=16, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class WalletTradeDetailListForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class RechargeActionFrom(forms.Form):
    user_id = forms.IntegerField(min_value=1)
    payable = forms.FloatField(min_value=0.01)
    # 是否赠送优惠券标识
    does_give_coupons = forms.ChoiceField(choices=((0, 1),
                                                   (1, 2)),
                                          required=False)


class CommentListForm(forms.Form):
    business_id = forms.IntegerField(min_value=1, required=False)
    user_id = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class FeedbackListForm(forms.Form):
    phone = forms.CharField(min_length=11, max_length=20, required=False)
    nickname = forms.CharField(max_length=100, required=False)
    content = forms.CharField(max_length=120, required=False)
    page_size = forms.IntegerField(required=False)
    page_index = forms.IntegerField(required=False)


class FeedbackDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class WalletRechargeGiftActionForm(forms.Form):
    phone_number = forms.CharField(min_length=11, max_length=11)
    verification_code = forms.CharField(min_length=6, max_length=6)


class WalletRechargeGiftListForm(forms.Form):
    phone_number = forms.CharField(min_length=11, max_length=11, required=False)
    verification_code = forms.CharField(min_length=6, max_length=6, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class WalletRechargeGiftDetailForm(forms.Form):
    id = forms.IntegerField(min_value=1)


class CancelUnConsumedOrdersActionForm(forms.Form):
    orders_id = forms.CharField(min_length=14, max_length=64)


class ConfirmUnConsumedOrdersActionForm(forms.Form):
    orders_id = forms.CharField(min_length=14, max_length=64)
