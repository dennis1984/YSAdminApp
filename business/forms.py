# -*- encoding: utf-8 -*-
from horizon import forms


class CityInputForm(forms.Form):
    city = forms.CharField(min_length=2, max_length=20)
    district = forms.CharField(min_length=2, max_length=30)
    province = forms.CharField(min_length=2, max_length=20, required=False)


class CityUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    city = forms.CharField(min_length=2, max_length=20, required=False)
    district = forms.CharField(min_length=2, max_length=30, required=False)
    province = forms.CharField(min_length=2, max_length=20, required=False)


class CityDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class DistrictInputForm(forms.Form):
    city_id = forms.IntegerField(min_value=1)
    district = forms.CharField(min_length=2, max_length=20)


class DistrictUpdateForm(forms.Form):
    city_id = forms.IntegerField(min_value=1)
    district_id = forms.IntegerField(min_value=1)
    district = forms.CharField(min_length=2, max_length=20)


class DistrictDeleteForm(CityDeleteForm):
    city_id = forms.IntegerField(min_value=1)
    district_id = forms.IntegerField(min_value=1)


class CityListForm(forms.Form):
    province = forms.CharField(min_length=2, max_length=20, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class FoodCourtInputForm(forms.Form):
    name = forms.CharField(min_length=2, max_length=60)
    type = forms.ChoiceField(choices=((10, 1),
                                      (20, 2)),
                             error_messages={'required': u'type值为 [10, 20] 中的一个'})
    city_id = forms.IntegerField(min_value=1)
    district = forms.CharField(min_length=2, max_length=30)
    mall = forms.CharField(min_length=2, max_length=60)
    address = forms.CharField(min_length=2, max_length=60)
    image = forms.ImageField(required=False)


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


class DishesListForm(forms.Form):
    user_id = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class DishesUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    is_recommend = forms.IntegerField(min_value=0, max_value=1)


class AdvertPictureInputForm(forms.Form):
    name = forms.CharField(max_length=20)
    image = forms.ImageField()


class AdvertPictureDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
