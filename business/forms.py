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
