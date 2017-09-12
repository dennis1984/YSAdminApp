# -*- encoding: utf-8 -*-
from horizon import forms


class PhoneForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=11,
                               error_messages={
                                   'required': u'手机号不能为空',
                                   'min_length': u'手机号位数不够'
                               })


class PasswordForm(forms.Form):
    password = forms.CharField(min_length=6,
                               max_length=50,
                               error_messages={
                                   'required': u'密码不能为空',
                                   'min_length': u'密码长度不能少于6位'
                               })


class CreateUserForm(forms.Form):
    """
    创建用户
    """
    username = forms.CharField(max_length=20, min_length=11,
                               error_messages={'required': u'手机号不能为空',
                                               'min_length': u'手机号位数不够'})
    password = forms.CharField(min_length=6, max_length=50,
                               error_messages={'required': u'密码不能为空',
                                               'min_length': u'密码长度不能少于6位'})
    nickname = forms.CharField(min_length=1, max_length=100, required=False)
    # permission_list为JSON字符串，形如：
    # {'管理平台'： (
    #       {'name': u'城市管理', 'url': '/city/'},
    #  ),
    #   '优惠券': (
    #        {'name': u'优惠券管理', 'url': '/coupons/'},
    # ), ...}
    permission_list = forms.CharField(required=False)


class UpdateUserForm(forms.Form):
    """
    更改用户信息
    """
    password = forms.CharField(min_length=6, max_length=50, required=False)
    nickname = forms.CharField(max_length=100, required=False)


class SendIdentifyingCodeForm(PhoneForm):
    """
    发送手机验证码
    """
    method = forms.ChoiceField(choices=(('register', 1), ('forget_password', 2)),
                               error_messages={
                                   'required': u'method 值必须为"register"或"forget_password"',
                               })


class VerifyIdentifyingCodeForm(PhoneForm):
    """
    验证手机验证码
    """
    identifying_code = forms.CharField(max_length=10,
                                       error_messages={'required': u'验证码不能为空'})


class SetPasswordForm(CreateUserForm):
    """
    忘记密码
    """
