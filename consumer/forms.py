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
    min_balance = forms.CharField(min_length=1, max_length=16, required=False)
    max_balance = forms.CharField(min_length=1, max_length=16, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class CommentListForm(forms.Form):
    business_id = forms.IntegerField(min_value=1, required=False)
    user_id = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)
