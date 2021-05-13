from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

UserModel = get_user_model()


class LoginBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        if not username or not password:
            return

        user = UserModel.objects.filter(username=username).first()

        if not user:
            user = UserModel.objects.filter(email=username).first()

        if not user or not user.check_password(password):
            return

        return user

    def get_user(self, id):
        try:
            return UserModel.objects.get(pk=id)
        except UserModel.DoesNotExist:
            return None
