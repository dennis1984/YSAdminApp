from users.models import AdminUser
from django.utils.timezone import now


class AdminUserBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user = AdminUser.objects.get(phone=username)
        except AdminUser.DoesNotExist:
            pass
        else:
            if user.check_password(password):
                user.last_login = now()
                user.save()
                return user
        return None

    def get_user(self, user_id):
        try:
            return AdminUser.objects.get(pk=user_id)
        except AdminUser.DoesNotExist:
            return None