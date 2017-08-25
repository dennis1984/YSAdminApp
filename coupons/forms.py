# -*- encoding: utf-8 -*-
from horizon import forms


class CouponsInputForm(forms.Form):
    name = forms.CharField(max_length=64,
                           error_messages={'required': u'优惠券名称不能为空'})
    type = forms.ChoiceField(choices=((10, 1),
                                      (20, 2),
                                      (100, 3),
                                      (200, 4)),
                             error_messages={'required': u'优惠券类别值只能在以下列表中，'
                                                         u'[10, 20, 100, 200]'})
    type_detail = forms.CharField(max_length=64, required=False)
    amount_of_money = forms.FloatField(min_value=0.01, error_messages={'required': u'优惠金额不能为空'})
    service_ratio = forms.IntegerField(min_value=0, max_value=100,
                                       error_messages={'required': u'平台商承担优惠比例值不能为空',
                                                       'max_value': u'service_ratio取值范围为0~100'})
    business_ratio = forms.IntegerField(min_value=0, max_value=100,
                                        error_messages={'required': u'商户承担优惠比例值不能为空',
                                                        'max_value': u'business_ratio取值范围为0~100'})
    start_amount = forms.FloatField(min_value=0,
                                    error_messages={'required': u'满足优惠条件的起始金额不能为空'})
    total_count = forms.IntegerField(min_value=1, required=False)
    expires = forms.DateTimeField(error_messages={'required': u'过期时间不能为空'})


class CouponsUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    name = forms.CharField(max_length=64, required=False)
    type = forms.ChoiceField(choices=((10, 1),
                                      (20, 2),
                                      (100, 3),
                                      (200, 4)),
                             required=False)
    type_detail = forms.CharField(max_length=64, required=False)
    amount_of_money = forms.FloatField(min_value=0.01, required=False)
    service_ratio = forms.IntegerField(min_value=0, max_value=100, required=False)
    business_ratio = forms.IntegerField(min_value=0, max_value=100, required=False)
    start_amount = forms.FloatField(min_value=0, required=False)
    total_count = forms.IntegerField(min_value=1, required=False)
    expires = forms.DateTimeField(required=False)


class CouponsDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class CouponsListForm(forms.Form):
    name = forms.CharField(max_length=64, required=False)
    type_detail = forms.CharField(max_length=64, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class CouponsDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class DishesDiscountInputForm(forms.Form):
    dishes_id = forms.IntegerField(min_value=1,
                                   error_messages={'required': u'菜品ID不能为空'})
    service_ratio = forms.IntegerField(min_value=0, max_value=100,
                                       error_messages={'required': u'平台商承担优惠比例值不能为空',
                                                       'max_value': u'service_ratio取值范围为0~100'})
    business_ratio = forms.IntegerField(min_value=0, max_value=100,
                                        error_messages={'required': u'商户承担优惠比例值不能为空',
                                                        'max_value': u'business_ratio取值范围为0~100'})
    expires = forms.DateTimeField(error_messages={'required': u'过期时间不能为空'})


class DishesDiscountUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    service_ratio = forms.IntegerField(min_value=0, max_value=100, required=False)
    business_ratio = forms.IntegerField(min_value=0, max_value=100, required=False)
    expires = forms.DateTimeField(required=False)


class DishesDiscountDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class DishesDiscountListForm(forms.Form):
    dishes_name = forms.CharField(max_length=40, required=False)
    business_name = forms.CharField(max_length=100, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class DishesDiscountDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class SendCouponsForm(forms.Form):
    coupons_id = forms.IntegerField(min_value=1)
    consumer_ids = forms.CharField()
