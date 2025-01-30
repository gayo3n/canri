from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from accounts.models import User  # 修正：accounts.models からインポート

class UserManagerTests(TestCase):
    def setUp(self):
        """テストの準備: カスタムユーザーモデルを取得"""
        self.User = get_user_model()

    def test_create_user_success(self):
        """通常のユーザー作成が成功する場合のテスト"""
        user = self.User.objects.create_user(name="mkn", password="masato111")

        self.assertIsNotNone(user)  # ユーザーが作成されたか
        self.assertEqual(user.name, "mkn")  # 名前が正しいか
        self.assertTrue(user.check_password("masato111"))  # パスワードが正しいか
        self.assertTrue(user.is_active)  # デフォルトでアクティブ
        self.assertFalse(user.is_staff)  # スタッフ権限がない
        self.assertFalse(user.is_superuser)  # スーパーユーザー権限がない

    def test_create_user_without_name_error(self):
        """名前が指定されていない場合にエラーを発生させるテスト"""
        with self.assertRaises(ValueError) as context:
            self.User.objects.create_user(name=None, password="testpassword")
        self.assertEqual(str(context.exception), "名前フィールドは必須です")

    def test_create_user_duplicate_name_error(self):
        """名前が重複している場合のエラーをテスト"""
        self.User.objects.create_user(name="testuser", password="testpassword")
        with self.assertRaises(IntegrityError):  # 名前の重複によるエラーを確認
            self.User.objects.create_user(name="testuser", password="testpassword2")

    def test_create_user_with_extra_fields(self):
        """追加フィールドが渡された場合の動作を確認"""
        user = self.User.objects.create_user(
            name="testuser",
            password="testpassword",
            is_active=False,  # デフォルトを上書き
            is_staff=True,
        )
        
        # 追加フィールドが反映されているか確認
        self.assertEqual(user.name, "testuser")
        self.assertTrue(user.check_password("testpassword"))
        self.assertFalse(user.is_active)  # is_active が False に設定されているか
        self.assertTrue(user.is_staff)  # is_staff が True に設定されているか
        self.assertFalse(user.is_superuser)  # is_superuser はデフォルトの False のまま

    def test_create_user_password_none(self):
        """パスワードが None の場合の挙動を確認"""
        # パスワードがNoneの場合でもエラーが発生しないことを確認
        user = self.User.objects.create_user(name="testuser", password=None)
        
        # ユーザーが作成されていることを確認
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "testuser")
        self.assertFalse(user.has_usable_password())  # パスワードが設定されていないことを確認

    def test_create_user_without_password_error(self):
        """パスワードが空の場合にエラーが発生しないことを確認"""
        user = self.User.objects.create_user(name="testuser", password=None)  # 修正：Noneを使用

        # ユーザーが作成されていることを確認
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "testuser")
        self.assertFalse(user.has_usable_password())  # パスワードが設定されていないことを確認
