# backends.py
from django.contrib.auth.backends import ModelBackend
from .models import User

class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # username または user_id でユーザーを検索
            user = User.objects.get(name=username) if username else User.objects.get(user_id=kwargs.get('user_id'))
            
            # 削除フラグが立っている場合は認証失敗
            if user.deletion_flag:
                return None
            
            # パスワードが正しいかチェック
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
