# -*- encoding: utf-8 -*-
from horizon import forms


class UserListForm(forms.Form):
    username = forms.CharField(min_length=11, max_length=16, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class CommentListForm(forms.Form):
    business_id = forms.IntegerField(min_value=1, required=False)
    user_id = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)
