# -*- encoding: utf-8 -*-
from horizon import forms


class CouponsInputForm(forms.Form):
    name = forms.CharField(max_length=64,
                           error_messages={'required': u'优惠券名称不能为空'})
    type = forms.ChoiceField(choices=((1, 1),
                                      (2, 2),),
                             error_messages={'required': u'优惠券类别值只能在以下列表中，'
                                                         u'[1, 2]'})
    amount_of_money = forms.FloatField(min_value=0.01, required=False)
    discount_percent = forms.IntegerField(min_value=1, max_value=100, required=False)
    service_ratio = forms.IntegerField(min_value=0, max_value=100,
                                       error_messages={'required': u'平台商承担优惠比例值不能为空',
                                                       'max_value': u'service_ratio取值范围为0~100'})
    business_ratio = forms.IntegerField(min_value=0, max_value=100,
                                        error_messages={'required': u'商户承担优惠比例值不能为空',
                                                        'max_value': u'business_ratio取值范围为0~100'})
    start_amount = forms.FloatField(min_value=0,
                                    error_messages={'required': u'满足优惠条件的起始金额不能为空'})
    total_count = forms.IntegerField(min_value=1, required=False)
    expire_in = forms.IntegerField(min_value=1, error_messages={'required': u'过期时间不能为空'})
    description = forms.CharField(max_length=85, required=False)


class CouponsUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    name = forms.CharField(max_length=64, required=False)
    type = forms.ChoiceField(choices=((1, 1),
                                      (2, 2),),
                             required=False)
    amount_of_money = forms.FloatField(min_value=0.01, required=False)
    discount_percent = forms.IntegerField(min_value=1, max_value=100, required=False)
    service_ratio = forms.IntegerField(min_value=0, max_value=100, required=False)
    business_ratio = forms.IntegerField(min_value=0, max_value=100, required=False)
    start_amount = forms.FloatField(min_value=0, required=False)
    total_count = forms.IntegerField(min_value=1, required=False)
    expire_in = forms.IntegerField(min_value=1, required=False)
    description = forms.CharField(max_length=85, required=False)


class CouponsDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class CouponsListForm(forms.Form):
    name = forms.CharField(max_length=64, required=False)
    type = forms.ChoiceField(choices=((1, 1),
                                      (2, 2),),
                             required=False)
    start_amount = forms.FloatField(min_value=0, required=False)
    status = forms.ChoiceField(choices=((1, 1),
                                        (400, 2),),
                               required=False)
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


class DishesDiscountUpdateForm(forms.Form):
    dishes_id = forms.IntegerField(min_value=1)
    service_ratio = forms.IntegerField(min_value=0, max_value=100, required=False)
    business_ratio = forms.IntegerField(min_value=0, max_value=100, required=False)


class DishesDiscountDeleteForm(forms.Form):
    dishes_id = forms.IntegerField(min_value=1)


class DishesDiscountListForm(forms.Form):
    dishes_name = forms.CharField(max_length=40, required=False)
    business_name = forms.CharField(max_length=100, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class DishesDiscountDetailForm(forms.Form):
    dishes_id = forms.IntegerField(min_value=1)


class SendCouponsForm(forms.Form):
    coupons_id = forms.IntegerField(min_value=1)
    consumer_ids = forms.CharField()


class CouponsSendRecordForm(forms.Form):
    coupons_name = forms.CharField(max_length=20, required=False)
    phone = forms.CharField(max_length=20, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class CouponsUsedRecordForm(forms.Form):
    coupons_name = forms.CharField(max_length=20, required=False)
    phone = forms.CharField(max_length=20, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)
