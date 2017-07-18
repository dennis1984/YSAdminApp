# -*- encoding: utf-8 -*-
from horizon import forms


class CityInputForm(forms.Form):
    city = forms.CharField(min_length=2, max_length=20)
    province = forms.CharField(min_length=2, max_length=20)


class CityListForm(forms.Form):
    province = forms.CharField(min_length=2, max_length=20, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class FoodCourtInputForm(forms.Form):
    name = forms.CharField(min_length=2, max_length=60)
    city_id = forms.IntegerField(min_value=1)
    district = forms.CharField(min_length=2, max_length=30)
    mall = forms.CharField(min_length=2, max_length=60)
    address = forms.CharField(min_length=2, max_length=60)


class FoodCourtListForm(forms.Form):
    city = forms.CharField(min_length=2, max_length=30, required=False)
    district = forms.CharField(min_length=2, max_length=30, required=False)
    mall = forms.CharField(min_length=2, max_length=50, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class UsersInputForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=11,
                               error_messages={'required': u'手机号不能为空',
                                               'min_length': u'手机号位数不够'})
    password = forms.CharField(min_length=6, max_length=50,
                               error_messages={'required': u'密码不能为空',
                                               'min_length': u'密码长度不能少于6位'})
    business_name = forms.CharField(min_length=2, max_length=100)
    food_court_id = forms.IntegerField(min_value=1)


class UserListForm(forms.Form):
    food_court_id = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)

