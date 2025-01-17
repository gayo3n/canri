# accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import User

# accounts/backends.py
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"Authenticating user: {username}")  # デバッグ用
        try:
            user = User.objects.get(name=username)
            if user.deletion_flag:
                print("User is deleted")  # デバッグ用
                return None
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            print("User does not exist")  # デバッグ用
            return None
