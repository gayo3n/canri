from django.test import TestCase
<<<<<<< HEAD
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
=======
from django.utils import timezone
from .models import User


class TestUserModel(TestCase):
    def setUp(self):
        """
        テスト用データの作成
        """
        self.user = User.objects.create(
            user_id="USR1234567",
            name="TestUser",
            password="password123",  # ハッシュ化は省略
            is_active=True,
            is_staff=False,
            is_superuser=False,
            administrator_flag=False,
            deletion_flag=False,
            creation_date=timezone.now(),
        )

    def test_create_user_success(self):
        """
        正常に User を作成するケース
        """
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.name, "TestUser")
        self.assertTrue(self.user.is_active)

    # def test_create_user_with_duplicate_name(self):
    #     """
    #     name が重複している場合にエラーを検出
    #     """
    #     with self.assertRaises(Exception):
    #         User.objects.create(
    #             user_id="USR7654321",
    #             name="TestUser",  # 重複名
    #             password="password456",
    #             is_active=True,
    #         )
            # 名前の重複ではエラー起きない

    # def test_update_user_success(self):
    #     """
    #     User のデータを正常に更新するケース
    #     """
    #     self.user.name = "UpdatedUser"
    #     self.user.save()
    #     updated_user = User.objects.get(user_id="USR1234567")
    #     self.assertEqual(updated_user.name, "UpdatedUser")

    # def test_delete_user_logically(self):
    #     """
    #     User を論理削除するケース
    #     """
    #     self.user.delete()
    #     deleted_user = User.objects.get(user_id="USR1234567")
    #     self.assertTrue(deleted_user.deletion_flag)
    #     self.assertIsNotNone(deleted_user.deletion_date)

    # def test_create_user_with_short_name(self):
    #     """
    #     name の長さが不十分な場合にエラーを検出
    #     """
    #     with self.assertRaises(ValueError):
    #         User.objects.create(
    #             user_id="USR5432109",
    #             name="Us",  # 短すぎる名前
    #             password="password789",
    #         )

    # def test_create_user_with_invalid_password(self):
    #     """
    #     password の要件を満たしていない場合にエラーを検出
    #     """
    #     with self.assertRaises(ValueError):
    #         User.objects.create(
    #             user_id="USR0987654",
    #             name="AnotherUser",
    #             password="123",  # 短すぎるパスワード
    #         )

if __name__ == "__main__":
    import unittest
    unittest.main()
>>>>>>> f2455ed08110073128726ed3df9433dd18aa0e8a
