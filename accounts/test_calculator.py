import unittest
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import User

# テストクラス
class TestAccounts(TestCase):
    # ユーザーを作成するテスト
    def test_create_user(self):
        User = get_user_model()# ユーザーモデルを取得
        self.assertEqual(User.objects.count(), 0)# ユーザーが作成されたことを確認

        # ユーザーを作成
        user = User.objects.create_user(name='testuser', password='testpassword')
        
        # ユーザーが作成されたことを確認
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.name, 'testuser')
        self.assertTrue(user.check_password('testpassword'))

    