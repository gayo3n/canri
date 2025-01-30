from django.test import TestCase
from django.contrib.auth import get_user_model  # ユーザーモデルを取得
from django.urls import reverse
from django.test import Client

class TestAccounts(TestCase):

    # ユーザー作成のテスト
    def test_create_user(self):
        User = get_user_model()  # ユーザーモデルを取得
        self.assertEqual(User.objects.count(), 0)  # ユーザーが作成されていないことを確認

        # ユーザーを作成
        user = User.objects.create_user(name='testuser', password='testpassword')

        # ユーザーが作成されたことを確認
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.name, 'testuser')
        self.assertTrue(user.check_password('testpassword'))

    # ユーザーログインのテスト
    def test_user_login(self):
        User = get_user_model()  # ユーザーモデルを取得
        user = User.objects.create_user(name='testuser', password='testpassword')

        # クライアントを作成
        client = Client()

        # ログインしてみる
        login = client.login(username='testuser', password='testpassword')  # 'username'を使用

        # ログインが成功したことを確認
        self.assertTrue(login)

        # ログイン後のページにアクセス
        response = client.get(reverse('home'))  # homeのURLを確認し、変更が必要な場合があります

        # レスポンスのステータスコードを確認
        if response.status_code == 404:
            print("404 Not Found")
        elif response.status_code == 500:
            print("500 Internal Server Error")
        elif response.status_code == 200:
            print("OK (200)")

        # レスポンスが200 OKであることを確認
        self.assertEqual(response.status_code, 200)

    # 不正なログインのテスト
    def test_invalid_user_login(self):
        # クライアントを作成
        client = Client()

        # 不正なログイン（間違ったパスワード）
        login = client.login(username='testuser', password='wrongpassword')

        # ログインが失敗したことを確認
        self.assertFalse(login)
