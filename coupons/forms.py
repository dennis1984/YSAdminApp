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
    service_ratio = forms.IntegerField(min_value=0, max_value=100,
                                       error_messages={'required': u'平台商承担优惠比例值不能为空',
                                                       'max_value': u'service_ratio取值范围为0~100'})
    business_ratio = forms.IntegerField(min_value=0, max_value=100,
                                        error_messages={'required': u'商户承担优惠比例值不能为空',
                                                        'max_value': u'business_ratio取值范围为0~100'})
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
    service_ratio = forms.IntegerField(min_value=0, max_value=100, required=False)
    business_ratio = forms.IntegerField(min_value=0, max_value=100, required=False)
    expires = forms.DateTimeField(required=False)


class CouponsDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
