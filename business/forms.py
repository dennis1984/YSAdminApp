# -*- encoding: utf-8 -*-
from horizon import forms


class CityInputForm(forms.Form):
    city = forms.CharField(min_length=2, max_length=20)
    district = forms.CharField(min_length=2, max_length=20)


class CityUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    city = forms.CharField(min_length=2, max_length=20, required=False)
    district = forms.CharField(min_length=2, max_length=30, required=False)


class CityDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class CityDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class CityListForm(forms.Form):
    city = forms.CharField(min_length=1, max_length=20, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class DistrictDetailForm(forms.Form):
    city = forms.CharField(min_length=1, max_length=20)


class FoodCourtInputForm(forms.Form):
    name = forms.CharField(min_length=2, max_length=60)
    type = forms.ChoiceField(choices=((10, 1),
                                      (20, 2)),
                             error_messages={'required': u'type值为 [10, 20] 中的一个'})
    city_id = forms.IntegerField(min_value=1)
    # district_id = forms.IntegerField(min_value=1)
    mall = forms.CharField(min_length=2, max_length=60)
    address = forms.CharField(min_length=2, max_length=60)
    image = forms.ImageField(required=False)


class FoodCourtUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    name = forms.CharField(min_length=2, max_length=60, required=False)
    type = forms.ChoiceField(choices=((10, 1),
                                      (20, 2)),
                             error_messages={'required': u'type值为 [10, 20] 中的一个'},
                             required=False)
    city_id = forms.IntegerField(min_value=1, required=False)
    mall = forms.CharField(min_length=2, max_length=60, required=False)
    address = forms.CharField(min_length=2, max_length=60, required=False)
    image = forms.ImageField(required=False)


class FoodCourtDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class FoodCourtDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class FoodCourtListForm(forms.Form):
    name = forms.CharField(min_length=1, max_length=60, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class UserWithFoodCourtListForm(forms.Form):
    business_name = forms.CharField(min_length=1, max_length=20, required=False)
    food_court_name = forms.CharField(min_length=1, max_length=20, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class UsersInputForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=11,
                               error_messages={'required': u'手机号不能为空',
                                               'min_length': u'手机号位数不够'})
    # password = forms.CharField(min_length=6, max_length=50,
    #                            error_messages={'required': u'密码不能为空',
    #                                            'min_length': u'密码长度不能少于6位'})
    business_name = forms.CharField(min_length=2, max_length=100)
    food_court_id = forms.IntegerField(min_value=1)
    brand = forms.CharField(min_length=2, max_length=20,
                            error_messages={'required': u'品牌不能为空'})
    manager = forms.CharField(min_length=2, max_length=20,
                              error_messages={'required': u'经理人不能为空'})
    chinese_people_id = forms.CharField(min_length=18, max_length=25,
                                        error_messages={'required': u'身份证号不能为空'})
    stalls_number = forms.CharField(min_length=1, max_length=20,
                                    error_messages={'required': u'档口编号不能为空'})


class UserUpdateForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)
    business_name = forms.CharField(min_length=2, max_length=100, required=False)
    food_court_id = forms.IntegerField(min_value=1, required=False)
    brand = forms.CharField(min_length=2, max_length=20, required=False)
    manager = forms.CharField(min_length=2, max_length=20, required=False)
    chinese_people_id = forms.CharField(min_length=18, max_length=25, required=False)
    stalls_number = forms.CharField(min_length=1, max_length=20, required=False)

    is_active = forms.IntegerField(min_value=0, max_value=1, required=False)


class UserResetPasswordForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)


class UserDetailForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)


class UserListForm(forms.Form):
    phone = forms.CharField(min_length=11, max_length=16, required=False)
    business_name = forms.CharField(min_length=1, max_length=20, required=False)
    # food_court_name = forms.CharField(min_length=2, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class DishesInputForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)
    title = forms.CharField(max_length=200)
    subtitle = forms.CharField(max_length=200, required=False)
    description = forms.CharField(max_length=500, required=False)
    price = forms.CharField(max_length=16)
    size = forms.IntegerField(min_value=10, max_value=20, required=False)
    size_detail = forms.CharField(min_length=2, max_length=30, required=False)
    mark = forms.ChoiceField(choices=((0, 1),
                                      (10, 2),
                                      (20, 3),
                                      (30, 4)),
                             error_messages={
                                 'required': 'The fields mark must in '
                                             '[0, 10, 20, 30].'
                             },
                             required=False)
    image = forms.ImageField(required=False)
    image_detail = forms.ImageField(required=False)


class DishesListForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)
    title = forms.CharField(min_length=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class DishesUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    title = forms.CharField(max_length=200, required=False)
    subtitle = forms.CharField(max_length=200, required=False)
    description = forms.CharField(max_length=500, required=False)
    price = forms.CharField(max_length=16, required=False)
    size = forms.IntegerField(min_value=10, max_value=20, required=False)
    size_detail = forms.CharField(min_length=2, max_length=30, required=False)
    mark = forms.ChoiceField(choices=((0, 1),
                                      (10, 2),
                                      (20, 3),
                                      (30, 4)),
                             error_messages={
                                 'required': 'The fields mark must in '
                                             '[0, 10, 20, 30].'
                             },
                             required=False)
    image = forms.ImageField(required=False)
    image_detail = forms.ImageField(required=False)


class DishesDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class DishesDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class WithdrawRecordListForm(forms.Form):
    status = forms.ChoiceField(choices=((0, 1),
                                        (201, 2),
                                        (206, 3),
                                        (400, 4),
                                        (500, 5)),
                               required=False)
    business_name = forms.CharField(min_length=1, max_length=30, required=False)
    amount_of_money = forms.FloatField(min_value=0.01, required=False)
    start_created = forms.DateField(required=False)
    end_created = forms.DateField(required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class WithdrawRecordDetailForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class WithdrawRecordActionForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    status = forms.ChoiceField(choices=((201, 1),
                                        (206, 2),
                                        (500, 3)),
                               error_messages={
                                   'required': 'status must in [201, 206, 500]'})


class OrdersListForm(forms.Form):
    payment_status = forms.ChoiceField(choices=((0, 1),
                                                (200, 2),
                                                (201, 3),
                                                (206, 4),
                                                (400, 5),
                                                (500, 6)),
                                       )
    pay_orders_id = forms.CharField(min_length=14, max_length=32, required=False)
    verify_orders_id = forms.CharField(min_length=14, max_length=32, required=False)
    phone = forms.CharField(min_length=11, max_length=16, required=False)
    business_name = forms.CharField(min_length=1, max_length=30, required=False)
    start_created = forms.DateField(required=False)
    end_created = forms.DateField(required=False)
    min_payable = forms.FloatField(min_value=0.01, required=False)
    max_payable = forms.FloatField(min_value=0.01, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)


class OrdersDetailForm(forms.Form):
    orders_id = forms.CharField(min_length=14, max_length=32)


class BankCardAddForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)
    bank_card_number = forms.CharField(min_length=16, max_length=25)
    bank_name = forms.CharField(min_length=4, max_length=50)
    account_name = forms.CharField(min_length=2, max_length=20)


class BankCardUpdateForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    bank_card_number = forms.CharField(min_length=16, max_length=25, required=False)
    bank_name = forms.CharField(min_length=4, max_length=50, required=False)
    account_name = forms.CharField(min_length=2, max_length=20, required=False)


class BankCardDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)


class BankCardListForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)


class AdvertPictureInputForm(forms.Form):
    name = forms.CharField(max_length=20)
    image = forms.ImageField()


class AdvertPictureDeleteForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
